#!/usr/bin/env python3
"""
Bhusampadan Chatbot Worker
Runs as a persistent process, communicates via stdin/stdout (no Flask, no HTTP server)
"""

import sys
import json
import os
import re
import unicodedata
import tempfile
import base64

# Make stdout unbuffered for real-time communication
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

# print("🔄 Loading Bhusampadan Chatbot...", file=sys.stderr)

# --------------------------------------------------
# PATH SETUP
# --------------------------------------------------
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from knowledge_base import (
    RESPONSE_KEYS_MAP_SAMANVAY_OFFICER,
    RESPONSE_KEYS_MAP_LAO,
    RESPONSE_KEYS_MAP_PROJECT_INCHARGE,
    RESPONSE_KEYS_MAP_SURVEYOR,
    RESPONSE_KEYS_MAP_DSLR,
    RESPONSE_KEYS_MAP_TEHSILDAR,
    RESPONSE_KEYS_MAP_DRO,
    RESPONSE_KEYS_MAP_COLLECTOR,
    get_knowledge_base,
    get_response_by_key,
    # build_response_with_link
)

# Role → response map lookup
ROLE_RESPONSE_MAPS = {
    "samanvay":         RESPONSE_KEYS_MAP_SAMANVAY_OFFICER,
    "lao":              RESPONSE_KEYS_MAP_LAO,
    "project_incharge": RESPONSE_KEYS_MAP_PROJECT_INCHARGE,
    "surveyor":         RESPONSE_KEYS_MAP_SURVEYOR,
    "dslr":             RESPONSE_KEYS_MAP_DSLR,
    "tehsildar":        RESPONSE_KEYS_MAP_TEHSILDAR,
    "dro":              RESPONSE_KEYS_MAP_DRO,
    "collector":        RESPONSE_KEYS_MAP_COLLECTOR,
}

# from sentence_transformers import SentenceTransformer, util
from simple_embedding import SimpleEmbedder
from gtts import gTTS

# --------------------------------------------------
# CHATBOT CLASS
# --------------------------------------------------
class BhusampadanChatbot:
    def __init__(self):
        self.knowledge_bases = {
            "en": get_knowledge_base("en"),
            "hi": get_knowledge_base("hi"),
            "mr": get_knowledge_base("mr")
        }

        self._fallback_templates = {
            "en": "Sorry, I can answer only questions related to {role}.",
            "hi": "माफ़ करें, मैं केवल {role} से संबंधित प्रश्नों के उत्तर दे सकता हूँ।",
            "mr": "माफ करा, मी फक्त {role} प्रणालीशी संबंधित प्रश्नांची उत्तरे देऊ शकतो."
        }

        # Human-readable role labels for the fallback message
        self._role_labels = {
            "samanvay":         "Samanvay Officer",
            "lao":              "LAO Officer",
            "project_incharge": "Project Incharge",
            "surveyor":         "Surveyor",
            "dslr":             "DSLR Officer",
            "tehsildar":        "Tehsildar",
            "dro":              "DRO Officer",
            "collector":        "Collector",
        }

        # ROLE → allowed intent keys
        self.role_allowed_keys = {
            "samanvay":         set(RESPONSE_KEYS_MAP_SAMANVAY_OFFICER.keys()),
            "lao":              set(RESPONSE_KEYS_MAP_LAO.keys()),
            "project_incharge": set(RESPONSE_KEYS_MAP_PROJECT_INCHARGE.keys()),
            "surveyor":         set(RESPONSE_KEYS_MAP_SURVEYOR.keys()),
            "dslr":             set(RESPONSE_KEYS_MAP_DSLR.keys()),
            "tehsildar":        set(RESPONSE_KEYS_MAP_TEHSILDAR.keys()),
            "dro":              set(RESPONSE_KEYS_MAP_DRO.keys()),
            "collector":        set(RESPONSE_KEYS_MAP_COLLECTOR.keys()),
        }

        # Load model from local folder — no internet, no HuggingFace cache needed
        MODEL_PATH = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "models",
            "paraphrase-multilingual-MiniLM-L12-v2"
        )

        # self.embedder = SentenceTransformer(MODEL_PATH)

        # Enhanced intent profiles - COPY FROM YOUR server.py lines 54-1467
        self.intent_profiles = {
            "dashboard_change_project": {
                "en": [
                    "how to change project",
                    "change project",
                    "switch project",
                    "select another project",
                    "change current project",
                    "how to switch project",
                    "update selected project",
                    "choose different project",
                    "project change option",
                    "change active project"
                ],
                "hi": [
                    "प्रोजेक्ट कैसे बदलें",
                    "प्रोजेक्ट बदलना है",
                    "प्रोजेक्ट स्विच करना",
                    "दूसरा प्रोजेक्ट चुनना",
                    "वर्तमान प्रोजेक्ट बदलना",
                    "चयनित प्रोजेक्ट बदलें",
                    "प्रोजेक्ट बदलने का विकल्प",
                    "नया प्रोजेक्ट चुनें",
                    "सक्रिय प्रोजेक्ट बदलना",
                    "प्रोजेक्ट अपडेट कैसे करें"
                ],
                "mr": [
                    "प्रकल्प कसा बदलावा",
                    "प्रकल्प बदलायचा आहे",
                    "प्रकल्प स्विच करणे",
                    "दुसरा प्रकल्प निवडणे",
                    "सध्याचा प्रकल्प बदलणे",
                    "निवडलेला प्रकल्प बदला",
                    "प्रकल्प बदलण्याचा पर्याय",
                    "नवीन प्रकल्प निवडा",
                    "सक्रिय प्रकल्प बदलणे",
                    "प्रकल्प अपडेट कसा करावा"
                ]
            },

            "dashboard_all_document": {
                "en": [
                    "view all documents",
                    "show all documents",
                    "see all pdf documents",
                    "open all documents",
                    "access all documents",
                    "download all documents",
                    "download all documents as zip",
                    "view document list",
                    "see all files",
                    "all document option"
                ],
                "hi": [
                    "सभी दस्तावेज़ देखें",
                    "सभी पीडीएफ दस्तावेज़ दिखाएं",
                    "सभी डॉक्यूमेंट खोलें",
                    "सभी दस्तावेज़ डाउनलोड करें",
                    "सभी दस्तावेज़ ज़िप में डाउनलोड करें",
                    "डॉक्यूमेंट सूची देखें",
                    "सभी फाइल देखें",
                    "ऑल डॉक्यूमेंट विकल्प",
                    "सभी दस्तावेज़ एक्सेस करें",
                    "सभी पीडीएफ देखें"
                ],
                "mr": [
                    "सर्व दस्तऐवज पाहा",
                    "सर्व पीडीएफ डॉक्युमेंट्स पाहा",
                    "सर्व डॉक्युमेंट उघडा",
                    "सर्व दस्तऐवज डाउनलोड करा",
                    "सर्व दस्तऐवज झिपमध्ये डाउनलोड करा",
                    "डॉक्युमेंट यादी पाहा",
                    "सर्व फाईल्स पाहा",
                    "ऑल डॉक्युमेंट पर्याय",
                    "सर्व कागदपत्रे एक्सेस करा",
                    "सर्व पीडीएफ पाहा"
                ]
            },

            "dashboard_proposal_progress_status": {
                "en": [
                    "check proposal progress status",
                    "view proposal progress",
                    "see section progress",
                    "check section status",
                    "proposal status",
                    "progress of section 11",
                    "progress of section 12",
                    "progress of section 15",
                    "progress of section 19",
                    "progress of section 21",
                    "progress of section 23",
                    "check payment status",
                    "proposal payment progress",
                    "track proposal progress",
                    "view progress details"
                ],
                "hi": [
                    "प्रस्ताव की प्रगति स्थिति देखें",
                    "सेक्शन की स्थिति जांचें",
                    "सेक्शन 11 की प्रगति",
                    "सेक्शन 12 की प्रगति",
                    "सेक्शन 15 की प्रगति",
                    "सेक्शन 19 की प्रगति",
                    "सेक्शन 21 की प्रगति",
                    "सेक्शन 23 की प्रगति",
                    "भुगतान स्थिति जांचें",
                    "प्रस्ताव प्रगति ट्रैक करें",
                    "प्रस्ताव की स्थिति",
                    "प्रगति विवरण देखें",
                    "सेक्शन स्टेटस देखें",
                    "पेमेंट प्रगति देखें"
                ],
                "mr": [
                    "प्रस्तावाची प्रगती स्थिती पाहा",
                    "सेक्शनची स्थिती तपासा",
                    "सेक्शन 11 प्रगती",
                    "सेक्शन 12 प्रगती",
                    "सेक्शन 15 प्रगती",
                    "सेक्शन 19 प्रगती",
                    "सेक्शन 21 प्रगती",
                    "सेक्शन 23 प्रगती",
                    "पेमेंट स्थिती तपासा",
                    "प्रस्ताव प्रगती ट्रॅक करा",
                    "प्रस्ताव स्थिती पाहा",
                    "प्रगती तपशील पाहा",
                    "सेक्शन स्टेटस पाहा",
                    "पेमेंट प्रगती पाहा"
                ]
            },

            "add_user": {
                "en": [
                    "add user",
                    "create new user",
                    "add system user",
                    "user management add user",
                    "register user",
                    "new user entry",
                    "create user account",
                    "how to add user",
                    "add user in system",
                    "user creation"
                ],
                "hi": [
                    "नया उपयोगकर्ता जोड़ें",
                    "यूजर जोड़ना",
                    "नया यूजर बनाएं",
                    "उपयोगकर्ता प्रबंधन में यूजर जोड़ें",
                    "यूजर रजिस्टर करें",
                    "नया यूजर एंट्री",
                    "यूजर अकाउंट बनाएं",
                    "सिस्टम में यूजर जोड़ें",
                    "यूजर कैसे जोड़ें",
                    "यूजर बनाना है"
                ],
                "mr": [
                    "नवीन वापरकर्ता जोडा",
                    "यूजर जोडा",
                    "नवीन यूजर तयार करा",
                    "वापरकर्ता व्यवस्थापनात यूजर जोडा",
                    "यूजर नोंदणी करा",
                    "नवीन यूजर एंट्री",
                    "यूजर अकाउंट तयार करा",
                    "सिस्टममध्ये यूजर जोडा",
                    "यूजर कसा जोडावा",
                    "यूजर तयार करणे"
                ]
            },

            "add_sub_user": {
                "en": [
                    "add sub user",
                    "create sub user",
                    "add sub-user",
                    "sub user management add",
                    "register sub user",
                    "new sub user entry",
                    "how to add sub user",
                    "create sub account",
                    "add subordinate user",
                    "sub user creation"
                ],
                "hi": [
                    "उप उपयोगकर्ता जोड़ें",
                    "सब यूजर जोड़ें",
                    "उप-यूजर बनाएं",
                    "उप उपयोगकर्ता प्रबंधन",
                    "नया सब यूजर जोड़ें",
                    "सब यूजर रजिस्टर करें",
                    "उप-यूजर एंट्री",
                    "सब अकाउंट बनाएं",
                    "उप उपयोगकर्ता कैसे जोड़ें",
                    "सब यूजर बनाना है"
                ],
                "mr": [
                    "उप-वापरकर्ता जोडा",
                    "सब यूजर जोडा",
                    "नवीन उप-वापरकर्ता तयार करा",
                    "उप-वापरकर्ता व्यवस्थापनात जोडा",
                    "सब यूजर नोंदणी करा",
                    "नवीन उप-यूजर एंट्री",
                    "उप-वापरकर्ता अकाउंट तयार करा",
                    "उप-वापरकर्ता कसा जोडावा",
                    "सब यूजर तयार करणे",
                    "उप-वापरकर्ता तयार करणे"
                ]
            },

            "create_project": {
                "en": [
                    "create new project in project management system",
                    "add project to the system",
                    "how to make a new project",
                    "start a new project in system"
                ],
                "hi": [
                    "प्रोजेक्ट प्रबंधन में नया प्रोजेक्ट बनाना",
                    "सिस्टम में नया प्रोजेक्ट जोड़ना",
                    "नया प्रोजेक्ट कैसे बनाएं",
                    "प्रोजेक्ट मैनेजमेंट में प्रोजेक्ट जोड़ना"
                ],
                "mr": [
                    "प्रकल्प व्यवस्थापन मध्ये नवीन प्रकल्प तयार करणे",
                    "सिस्टममध्ये नवीन प्रकल्प जोडणे",
                    "नवीन प्रकल्प कसा तयार करायचा",
                    "प्रकल्प व्यवस्थापनात प्रकल्प जोडणे"
                ]
            },

            "edit_project": {
                "en": [
                    "edit existing project details",
                    "update project information",
                    "modify project data",
                    "change project details"
                ],
                "hi": [
                    "मौजूदा प्रोजेक्ट के विवरण को संपादित करना",
                    "प्रोजेक्ट की जानकारी अपडेट करना",
                    "प्रोजेक्ट डेटा में बदलाव करना",
                    "प्रोजेक्ट विवरण बदलना"
                ],
                "mr": [
                    "विद्यमान प्रकल्पाचे तपशील संपादित करणे",
                    "प्रकल्प माहिती अपडेट करणे",
                    "प्रकल्प डेटा बदलणे",
                    "प्रकल्पाचे तपशील बदलणे"
                ]
            },

            "create_proposal": {
                "en": [
                    "create proposal",
                    "add proposal",
                    "new proposal entry",
                    "how to create proposal",
                    "start new proposal",
                    "proposal creation",
                    "make new proposal",
                    "register proposal",
                    "add new proposal",
                    "create proposal in system"
                ],
                "hi": [
                    "प्रस्ताव बनाएं",
                    "नया प्रस्ताव जोड़ें",
                    "प्रस्ताव कैसे बनाएं",
                    "प्रस्ताव बनाना है",
                    "प्रस्ताव एंट्री करें",
                    "नया प्रस्ताव शुरू करें",
                    "प्रस्ताव रजिस्टर करें",
                    "प्रस्ताव जोड़ना है",
                    "प्रस्ताव निर्माण",
                    "सिस्टम में प्रस्ताव बनाएं"
                ],
                "mr": [
                    "प्रस्ताव तयार करा",
                    "नवीन प्रस्ताव जोडा",
                    "प्रस्ताव कसा तयार करावा",
                    "प्रस्ताव तयार करायचा आहे",
                    "प्रस्ताव नोंदणी करा",
                    "नवीन प्रस्ताव एंट्री",
                    "प्रस्ताव सुरू करा",
                    "प्रस्ताव तयार करणे",
                    "सिस्टममध्ये प्रस्ताव तयार करा",
                    "प्रस्ताव जोडा"
                ]
            },

            "edit_proposal": {
                "en": [
                    "edit proposal",
                    "modify proposal",
                    "update proposal",
                    "change proposal details",
                    "proposal edit option",
                    "how to edit proposal",
                    "edit existing proposal",
                    "update proposal information",
                    "proposal modification",
                    "edit proposal data"
                ],
                "hi": [
                    "प्रस्ताव संपादित करें",
                    "प्रस्ताव में बदलाव करें",
                    "प्रस्ताव अपडेट करें",
                    "प्रस्ताव विवरण बदलें",
                    "प्रस्ताव संशोधन",
                    "प्रस्ताव कैसे संपादित करें",
                    "मौजूदा प्रस्ताव संपादित करें",
                    "प्रस्ताव जानकारी अपडेट करें",
                    "प्रस्ताव डेटा बदलें",
                    "प्रस्ताव एडिट करना है"
                ],
                "mr": [
                    "प्रस्ताव संपादित करा",
                    "प्रस्ताव बदल करा",
                    "प्रस्ताव अपडेट करा",
                    "प्रस्ताव तपशील बदला",
                    "प्रस्ताव सुधारणा",
                    "प्रस्ताव कसा संपादित करावा",
                    "विद्यमान प्रस्ताव संपादित करा",
                    "प्रस्ताव माहिती अपडेट करा",
                    "प्रस्ताव डेटा बदला",
                    "प्रस्ताव एडिट करायचा आहे"
                ]
            },
            
            "proposal_landholding": {
                "en": [
                    "add landholding",
                    "landholding entry",
                    "add land details in proposal",
                    "enter landholding information",
                    "manage landholding",
                    "update landholding details",
                    "land parcel entry",
                    "add land record in proposal",
                    "land survey details entry",
                    "proposal landholding section"
                ],
                "hi": [
                    "भूमि विवरण जोड़ें",
                    "भूमि होल्डिंग प्रविष्टि",
                    "प्रस्ताव में भूमि विवरण जोड़ें",
                    "भूमि जानकारी दर्ज करें",
                    "भूमि रिकॉर्ड जोड़ें",
                    "भूमि सर्वे विवरण दर्ज करें",
                    "भूमि विवरण अपडेट करें",
                    "भूमि होल्डिंग प्रबंधन",
                    "प्रस्ताव भूमि अनुभाग",
                    "जमीन का विवरण भरें"
                ],
                "mr": [
                    "जमीन तपशील जोडा",
                    "जमीन होल्डिंग नोंद",
                    "प्रस्तावात जमीन तपशील जोडा",
                    "जमीन माहिती भरा",
                    "जमीन रेकॉर्ड जोडा",
                    "जमीन सर्वे तपशील भरा",
                    "जमीन तपशील अपडेट करा",
                    "जमीन होल्डिंग व्यवस्थापन",
                    "प्रस्ताव जमीन विभाग",
                    "जमीनचा तपशील भरा"
                ]
            },

            "section_11_covering_letter": {
                "en": [
                    "section 11 covering letter",
                    "open section 11 letter",
                    "section 11 approval letter",
                    "section 11 notification letter",
                    "preliminary notification section 11",
                    "kalama 11 manayata",
                    "section 11 document",
                    "open section 11 document",
                    "section 11 covering document",
                    "publication section 11 letter"
                ],
                "hi": [
                    "धारा 11 आवरण पत्र",
                    "धारा 11 पत्र खोलें",
                    "कलम 11 मान्यता पत्र",
                    "धारा 11 अधिसूचना पत्र",
                    "प्राथमिक अधिसूचना धारा 11",
                    "कलम 11 दस्तावेज़",
                    "धारा 11 पत्र देखें",
                    "कलम 11 मान्यता खोलें",
                    "धारा 11 कवरिंग लेटर",
                    "सेक्शन 11 पत्र"
                ],
                "mr": [
                    "कलम 11 आवरण पत्र",
                    "कलम 11 पत्र उघडा",
                    "कलम 11 मान्यता पत्र",
                    "कलम 11 अधिसूचना पत्र",
                    "प्रारंभिक अधिसूचना कलम 11",
                    "कलम 11 दस्तऐवज",
                    "कलम 11 पत्र पहा",
                    "कलम 11 मान्यता उघडा",
                    "सेक्शन 11 पत्र",
                    "कलम 11 कवरिंग लेटर"
                ]
            },

            "section_11": {
                "en": [
                    "section 11 details",
                    "open section 11",
                    "preliminary notification section 11",
                    "section 11 information",
                    "section 11 page",
                    "view section 11",
                    "section 11 notification details",
                    "open preliminary notification",
                    "section 11 main page",
                    "publication section 11"
                ],
                "hi": [
                    "धारा 11 विवरण",
                    "धारा 11 खोलें",
                    "प्रारंभिक अधिसूचना धारा 11",
                    "धारा 11 की जानकारी",
                    "धारा 11 पेज",
                    "धारा 11 देखें",
                    "धारा 11 अधिसूचना विवरण",
                    "प्रारंभिक अधिसूचना खोलें",
                    "सेक्शन 11 विवरण",
                    "धारा 11 मुख्य पृष्ठ"
                ],
                "mr": [
                    "कलम 11 तपशील",
                    "कलम 11 उघडा",
                    "प्रारंभिक अधिसूचना कलम 11",
                    "कलम 11 माहिती",
                    "कलम 11 पृष्ठ",
                    "कलम 11 पहा",
                    "कलम 11 अधिसूचना तपशील",
                    "प्रारंभिक अधिसूचना उघडा",
                    "सेक्शन 11 तपशील",
                    "कलम 11 मुख्य पृष्ठ"
                ]
            },

            "section_11_edit": {
                "en": [
                    "edit section 11",
                    "modify section 11",
                    "update section 11",
                    "edit section 11 details",
                    "change section 11 information",
                    "update preliminary notification section 11",
                    "edit section 11 notification",
                    "section 11 edit option",
                    "modify preliminary notification",
                    "section 11 update"
                ],
                "hi": [
                    "धारा 11 संपादित करें",
                    "धारा 11 अपडेट करें",
                    "धारा 11 में बदलाव करें",
                    "धारा 11 विवरण संपादित करें",
                    "प्रारंभिक अधिसूचना धारा 11 अपडेट करें",
                    "सेक्शन 11 एडिट करें",
                    "धारा 11 की जानकारी बदलें",
                    "धारा 11 संशोधित करें",
                    "धारा 11 संपादन",
                    "धारा 11 में परिवर्तन करें"
                ],
                "mr": [
                    "कलम 11 संपादित करा",
                    "कलम 11 अपडेट करा",
                    "कलम 11 बदल करा",
                    "कलम 11 तपशील संपादित करा",
                    "प्रारंभिक अधिसूचना कलम 11 अपडेट करा",
                    "सेक्शन 11 एडिट करा",
                    "कलम 11 माहिती बदला",
                    "कलम 11 सुधारणा करा",
                    "कलम 11 संपादन",
                    "कलम 11 मध्ये बदल करा"
                ]
            },

            "section_11_send_to_samanvay_officer": {
                "en": [
                    "send section 11 to samanvay officer",
                    "send to samanvay officer section 11",
                    "forward section 11 to officer",
                    "submit section 11 to samanvay",
                    "section 11 send option",
                    "send preliminary notification to officer",
                    "forward preliminary notification section 11",
                    "send section 11 for review",
                    "transfer section 11 to samanvay officer",
                    "section 11 submit to officer"
                ],
                "hi": [
                    "धारा 11 समन्वय अधिकारी को भेजें",
                    "धारा 11 अग्रेषित करें",
                    "सेक्शन 11 समन्वय अधिकारी को भेजें",
                    "प्रारंभिक अधिसूचना धारा 11 भेजें",
                    "धारा 11 समीक्षा के लिए भेजें",
                    "धारा 11 अधिकारी को सबमिट करें",
                    "धारा 11 फॉरवर्ड करें",
                    "धारा 11 समन्वय अधिकारी को ट्रांसफर करें",
                    "सेक्शन 11 भेजना है",
                    "धारा 11 भेजें"
                ],
                "mr": [
                    "कलम 11 समन्वय अधिकाऱ्यांना पाठवा",
                    "कलम 11 अग्रेषित करा",
                    "सेक्शन 11 समन्वय अधिकाऱ्यांना पाठवा",
                    "प्रारंभिक अधिसूचना कलम 11 पाठवा",
                    "कलम 11 पुनरावलोकनासाठी पाठवा",
                    "कलम 11 अधिकारीकडे सबमिट करा",
                    "कलम 11 फॉरवर्ड करा",
                    "कलम 11 ट्रान्सफर करा",
                    "सेक्शन 11 पाठवायचे आहे",
                    "कलम 11 पाठवा"
                ]
            },

            "land_record_realisation_send_to_tehsildar": {
                "en": [
                    "send land record realisation to tehsildar",
                    "forward land record to tehsildar",
                    "submit land record to tehsildar",
                    "send land record details",
                    "land record send option",
                    "realisation send to tehsildar",
                    "transfer land record to tehsildar",
                    "submit land record for verification",
                    "send land record information",
                    "forward land record realisation"
                ],
                "hi": [
                    "भूमि अभिलेख वसूली तहसीलदार को भेजें",
                    "भूमि रिकॉर्ड तहसीलदार को भेजें",
                    "भूमि अभिलेख भेजें",
                    "तहसीलदार को भूमि विवरण भेजें",
                    "भूमि रिकॉर्ड सबमिट करें",
                    "भूमि अभिलेख अग्रेषित करें",
                    "भूमि वसूली तहसीलदार को भेजें",
                    "भूमि रिकॉर्ड ट्रांसफर करें",
                    "भूमि जानकारी तहसीलदार को भेजें",
                    "भूमि अभिलेख अधिकारी को भेजें"
                ],
                "mr": [
                    "भूमिअभिलेख तहसीलदारांना पाठवा",
                    "जमीन रेकॉर्ड तहसीलदारांकडे पाठवा",
                    "भूमिअभिलेख पाठवा",
                    "तहसीलदारांना जमीन तपशील पाठवा",
                    "जमीन रेकॉर्ड सबमिट करा",
                    "भूमिअभिलेख अग्रेषित करा",
                    "जमीन वसूली तहसीलदारांना पाठवा",
                    "जमीन रेकॉर्ड ट्रान्सफर करा",
                    "जमीन माहिती तहसीलदारांना पाठवा",
                    "भूमिअभिलेख अधिकारीकडे पाठवा"
                ]
            },

            "send_publication_proposal_to_dslr_for_joint_calculation": {
                "en": [
                    "send publication proposal to dslr",
                    "send proposal to dslr officer",
                    "forward proposal to dslr",
                    "submit proposal for joint calculation",
                    "joint calculation send to dslr",
                    "send for joint measurement",
                    "forward publication proposal",
                    "transfer proposal to dslr",
                    "send proposal for joint survey",
                    "submit publication proposal to dslr"
                ],
                "hi": [
                    "प्रकाशन प्रस्ताव DSLR को भेजें",
                    "प्रस्ताव DSLR अधिकारी को भेजें",
                    "संयुक्त गणना हेतु प्रस्ताव भेजें",
                    "संयुक्त मापन के लिए भेजें",
                    "प्रस्ताव अग्रेषित करें DSLR को",
                    "प्रकाशन प्रस्ताव सबमिट करें",
                    "संयुक्त गणना के लिए प्रस्ताव ट्रांसफर करें",
                    "प्रस्ताव DSLR को फॉरवर्ड करें",
                    "संयुक्त सर्वे हेतु भेजें",
                    "प्रस्ताव DSLR अधिकारी को सबमिट करें"
                ],
                "mr": [
                    "प्रकाशन प्रस्ताव DSLR ला पाठवा",
                    "प्रस्ताव DSLR अधिकाऱ्यांना पाठवा",
                    "संयुक्त मोजणीसाठी प्रस्ताव पाठवा",
                    "संयुक्त गणनेसाठी पाठवा",
                    "प्रस्ताव अग्रेषित करा DSLR ला",
                    "प्रकाशन प्रस्ताव सबमिट करा",
                    "संयुक्त मोजणीसाठी ट्रान्सफर करा",
                    "प्रस्ताव DSLR कडे फॉरवर्ड करा",
                    "संयुक्त सर्वेसाठी पाठवा",
                    "प्रस्ताव DSLR अधिकाऱ्यांकडे पाठवा"
                ]
            },

            "assign_dro_for_publication_preliminary_notification": {
                "en": [
                    "assign dro",
                    "assign dro for publication",
                    "assign dro for preliminary notification",
                    "select dro officer",
                    "allocate dro",
                    "assign dro to publication proposal",
                    "dro assignment",
                    "set dro officer",
                    "choose dro",
                    "assign dro option"
                ],
                "hi": [
                    "डीआरओ नियुक्त करें",
                    "प्रकाशन के लिए डीआरओ नियुक्त करें",
                    "प्रारंभिक अधिसूचना के लिए डीआरओ असाइन करें",
                    "डीआरओ अधिकारी चुनें",
                    "डीआरओ आवंटित करें",
                    "डीआरओ सेट करें",
                    "डीआरओ चयन करें",
                    "प्रकाशन प्रस्ताव के लिए डीआरओ असाइन करें",
                    "डीआरओ नियुक्ति",
                    "डीआरओ असाइन करें"
                ],
                "mr": [
                    "डीआरओ नियुक्त करा",
                    "प्रकाशनासाठी डीआरओ नियुक्त करा",
                    "प्रारंभिक अधिसूचनेसाठी डीआरओ असाइन करा",
                    "डीआरओ अधिकारी निवडा",
                    "डीआरओ वाटप करा",
                    "डीआरओ सेट करा",
                    "डीआरओ निवडा",
                    "प्रकाशन प्रस्तावासाठी डीआरओ असाइन करा",
                    "डीआरओ नियुक्ती",
                    "डीआरओ असाइन करा"
                ]
            },

            "view_publication_proposal": {
                "en": [
                    "view publication proposal",
                    "view proposal details",
                    "open publication proposal",
                    "show publication proposal",
                    "proposal detail view",
                    "view preliminary notification proposal",
                    "see proposal information",
                    "open proposal details page",
                    "publication proposal details",
                    "view proposal information"
                ],
                "hi": [
                    "प्रकाशन प्रस्ताव देखें",
                    "प्रस्ताव विवरण देखें",
                    "प्रकाशन प्रस्ताव खोलें",
                    "प्रस्ताव की जानकारी देखें",
                    "प्रारंभिक अधिसूचना प्रस्ताव देखें",
                    "प्रस्ताव का विवरण देखें",
                    "प्रस्ताव विवरण पेज खोलें",
                    "प्रकाशन प्रस्ताव जानकारी",
                    "प्रस्ताव देखें",
                    "प्रस्ताव विवरण दिखाएं"
                ],
                "mr": [
                    "प्रकाशन प्रस्ताव पहा",
                    "प्रस्ताव तपशील पहा",
                    "प्रकाशन प्रस्ताव उघडा",
                    "प्रस्तावाची माहिती पहा",
                    "प्रारंभिक अधिसूचना प्रस्ताव पहा",
                    "प्रस्ताव तपशील पृष्ठ उघडा",
                    "प्रकाशन प्रस्ताव माहिती",
                    "प्रस्ताव पाहा",
                    "प्रस्ताव तपशील दाखवा",
                    "प्रस्ताव माहिती पहा"
                ]
            },

            "funds_required_for_the_proclamation_of_section_19": {
                "en": [
                    "funds required for section 19",
                    "section 19 fund requirement",
                    "fund request for section 19",
                    "required funds for proclamation of section 19",
                    "section 19 fund details",
                    "view section 19 fund demand",
                    "section 19 fund information",
                    "check funds for section 19",
                    "section 19 proclamation fund",
                    "funds needed for section 19"
                ],
                "hi": [
                    "धारा 19 के लिए आवश्यक निधि",
                    "धारा 19 निधि मांग",
                    "धारा 19 के लिए फंड अनुरोध",
                    "धारा 19 घोषणा हेतु निधि",
                    "धारा 19 फंड विवरण",
                    "धारा 19 के लिए आवश्यक राशि देखें",
                    "धारा 19 निधि जानकारी",
                    "धारा 19 निधि आवश्यकता",
                    "धारा 19 के लिए फंड देखें",
                    "धारा 19 निधि मांग विवरण"
                ],
                "mr": [
                    "कलम 19 साठी आवश्यक निधी",
                    "कलम 19 निधी मागणी",
                    "कलम 19 साठी निधी विनंती",
                    "कलम 19 घोषणा निधी",
                    "कलम 19 निधी तपशील",
                    "कलम 19 साठी लागणारा निधी",
                    "कलम 19 निधी माहिती",
                    "कलम 19 साठी निधी आवश्यकता",
                    "कलम 19 निधी मागणी तपशील",
                    "कलम 19 साठी निधी पहा"
                ]
            },

            "send_funds_required_for_the_proclamation_of_section_19_to_project_incharge": {
                "en": [
                    "send section 19 fund to project incharge",
                    "send section 19 fund request",
                    "forward section 19 fund demand",
                    "send funds required for section 19",
                    "send section 19 proclamation fund",
                    "send section 19 fund details to project incharge",
                    "submit section 19 fund request",
                    "send fund requirement to project incharge",
                    "forward fund request for section 19",
                    "send section 19 funds"
                ],
                "hi": [
                    "धारा 19 निधि प्रोजेक्ट इंचार्ज को भेजें",
                    "धारा 19 फंड अनुरोध भेजें",
                    "धारा 19 निधि मांग अग्रेषित करें",
                    "धारा 19 घोषणा निधि भेजें",
                    "धारा 19 के लिए निधि प्रोजेक्ट इंचार्ज को भेजें",
                    "धारा 19 निधि विवरण भेजें",
                    "धारा 19 फंड सबमिट करें",
                    "धारा 19 निधि आगे भेजें",
                    "धारा 19 निधि अनुरोध भेजना है",
                    "धारा 19 निधि प्रोजेक्ट इंचार्ज को अग्रेषित करें"
                ],
                "mr": [
                    "कलम 19 निधी प्रोजेक्ट इंचार्ज ला पाठवा",
                    "कलम 19 निधी मागणी पाठवा",
                    "कलम 19 निधी पुढे पाठवा",
                    "कलम 19 घोषणा निधी पाठवा",
                    "कलम 19 साठी निधी प्रोजेक्ट इंचार्ज कडे पाठवा",
                    "कलम 19 निधी तपशील पाठवा",
                    "कलम 19 निधी सबमिट करा",
                    "कलम 19 निधी विनंती पाठवा",
                    "कलम 19 निधी प्रोजेक्ट इंचार्ज ला अग्रेषित करा",
                    "कलम 19 निधी पुढे पाठवायचा आहे"
                ]
            },

            "funds_required_for_final_award": {
                "en": [
                    "funds required for final award",
                    "final award fund requirement",
                    "fund request for final award",
                    "final award fund details",
                    "view final award fund demand",
                    "final award fund information",
                    "check funds for final award",
                    "final award proclamation fund",
                    "funds needed for final award",
                    "final award fund status"
                ],
                "hi": [
                    "अंतिम पुरस्कार के लिए आवश्यक निधि",
                    "अंतिम पुरस्कार निधि मांग",
                    "अंतिम पुरस्कार के लिए फंड अनुरोध",
                    "अंतिम पुरस्कार निधि विवरण",
                    "अंतिम पुरस्कार के लिए आवश्यक राशि देखें",
                    "अंतिम पुरस्कार निधि जानकारी",
                    "अंतिम पुरस्कार निधि आवश्यकता",
                    "अंतिम पुरस्कार फंड देखें",
                    "अंतिम पुरस्कार निधि मांग विवरण",
                    "अंतिम पुरस्कार के लिए निधि स्थिति"
                ],
                "mr": [
                    "अंतिम निवाडा साठी आवश्यक निधी",
                    "अंतिम निवाडा निधी मागणी",
                    "अंतिम निवाडा साठी निधी विनंती",
                    "अंतिम निवाडा निधी तपशील",
                    "अंतिम निवाडा साठी लागणारा निधी",
                    "अंतिम निवाडा निधी माहिती",
                    "अंतिम निवाडा साठी निधी आवश्यकता",
                    "अंतिम निवाडा निधी मागणी तपशील",
                    "अंतिम निवाडा साठी निधी पहा",
                    "अंतिम निवाडा निधी स्थिती"
                ]
            },

            "send_funds_required_for_final_award_to_project_incharge": {
                "en": [
                    "send final award fund to project incharge",
                    "send final award fund request",
                    "forward final award fund demand",
                    "send funds required for final award",
                    "send final award fund details",
                    "submit final award fund request",
                    "forward fund request for final award",
                    "send final award funds",
                    "send final award fund requirement",
                    "transfer final award fund to project incharge"
                ],
                "hi": [
                    "अंतिम पुरस्कार निधि प्रोजेक्ट इंचार्ज को भेजें",
                    "अंतिम पुरस्कार फंड अनुरोध भेजें",
                    "अंतिम पुरस्कार निधि मांग अग्रेषित करें",
                    "अंतिम पुरस्कार निधि भेजें",
                    "अंतिम पुरस्कार के लिए निधि प्रोजेक्ट इंचार्ज को भेजें",
                    "अंतिम पुरस्कार निधि विवरण भेजें",
                    "अंतिम पुरस्कार फंड सबमिट करें",
                    "अंतिम पुरस्कार निधि आगे भेजें",
                    "अंतिम पुरस्कार निधि अनुरोध भेजना है",
                    "अंतिम पुरस्कार निधि प्रोजेक्ट इंचार्ज को अग्रेषित करें"
                ],
                "mr": [
                    "अंतिम निवाडा निधी प्रोजेक्ट इंचार्ज ला पाठवा",
                    "अंतिम निवाडा निधी मागणी पाठवा",
                    "अंतिम निवाडा निधी पुढे पाठवा",
                    "अंतिम निवाडा निधी पाठवा",
                    "अंतिम निवाडा साठी निधी प्रोजेक्ट इंचार्ज कडे पाठवा",
                    "अंतिम निवाडा निधी तपशील पाठवा",
                    "अंतिम निवाडा निधी सबमिट करा",
                    "अंतिम निवाडा निधी विनंती पाठवा",
                    "अंतिम निवाडा निधी प्रोजेक्ट इंचार्ज ला अग्रेषित करा",
                    "अंतिम निवाडा निधी पुढे पाठवायचा आहे"
                ]
            },

            "JMR": {
                "en": [
                    "open jmr",
                    "view jmr",
                    "show jmr",
                    "joint measurement list",
                    "open joint measurement",
                    "view joint measurement details",
                    "jmr details",
                    "jmr list",
                    "check jmr",
                    "joint measurement register",
                    "jmr records",
                    "joint measurement data"
                    "review the measurement",
                    "measurement information",
                    "measurement details",
                    "measurement-related details",
                    "assign someone to handle joint measurement",
                    "send measurement task to surveyor"
                ],
                "hi": [
                    "जेएमआर खोलें",
                    "जेएमआर देखें",
                    "संयुक्त मापन सूची देखें",
                    "संयुक्त मापन विवरण खोलें",
                    "जेएमआर विवरण",
                    "संयुक्त मापन रजिस्टर",
                    "जेएमआर सूची",
                    "संयुक्त मापन देखें",
                    "जेएमआर जानकारी",
                    "संयुक्त मापन विवरण देखें",
                    "संयुक्त मापन जानकारी",
                    "मापन विवरण जांच",
                    "संयुक्त मापन रिकॉर्ड"
                ],
                "mr": [
                    "जेएमआर उघडा",
                    "जेएमआर पहा",
                    "संयुक्त मोजणी सूची पहा",
                    "संयुक्त मोजणी तपशील उघडा",
                    "जेएमआर तपशील",
                    "संयुक्त मोजणी नोंदवही",
                    "जेएमआर सूची",
                    "संयुक्त मोजणी पहा",
                    "जेएमआर माहिती",
                    "संयुक्त मोजणी तपशील पहा",
                    "मोजणीची यादी",
                    "मोजणी तपशील पाहायचे",
                    "मोजणी संबंधित नोंदी",
                    "संयुक्त मोजणी डेटा",
                    "मोजणी नोंद"
                ]
            },

            "JMR_assign_to_surveyor": {
                "en": [
                    "assign jmr to surveyor",
                    "assign surveyor for jmr",
                    "allocate surveyor for joint measurement",
                    "send jmr to surveyor",
                    "set surveyor for jmr",
                    "jmr surveyor assignment",
                    "choose surveyor for joint measurement",
                    "appoint surveyor for jmr",
                    "add surveyor to jmr",
                    "forward jmr to surveyor"
                ],
                "hi": [
                    "जेएमआर सर्वेक्षक को असाइन करें",
                    "संयुक्त मापन के लिए सर्वेक्षक नियुक्त करें",
                    "जेएमआर सर्वेक्षक को भेजें",
                    "संयुक्त मापन हेतु सर्वेक्षक चुनें",
                    "जेएमआर के लिए सर्वेक्षक सेट करें",
                    "सर्वेक्षक आवंटित करें",
                    "जेएमआर सर्वेक्षक नियुक्ति",
                    "संयुक्त मापन के लिए सर्वेक्षक जोड़ें",
                    "सर्वेक्षक को जेएमआर दें",
                    "जेएमआर सर्वेक्षक को अग्रेषित करें"
                ],
                "mr": [
                    "जेएमआर सर्वेक्षकाला असाइन करा",
                    "संयुक्त मोजणीसाठी सर्वेक्षक नियुक्त करा",
                    "जेएमआर सर्वेक्षकाला पाठवा",
                    "संयुक्त मोजणीसाठी सर्वेक्षक निवडा",
                    "जेएमआर साठी सर्वेक्षक सेट करा",
                    "सर्वेक्षक वाटप करा",
                    "जेएमआर सर्वेक्षक नियुक्ती",
                    "संयुक्त मोजणीसाठी सर्वेक्षक जोडा",
                    "सर्वेक्षकाला जेएमआर द्या",
                    "जेएमआर सर्वेक्षकाकडे अग्रेषित करा"
                ]
            },

            "advance_payment_distribution": {
                "en": [
                    "open advance payment distribution",
                    "go to advance payment distribution",
                    "show advance payment distribution",
                    "navigate to advance payment distribution section",
                    "access advance payment distribution module",
                    "advance payment distribution page",
                    "where can I see advance payment distribution",
                    "take me to advance payment distribution",
                    "open advance payment details",
                    "show advance payment distribution details"
                ],
                "hi": [
                    "उधार भुगतान वितरण खोलें",
                    "उधार भुगतान वितरण में जाएं",
                    "उधार भुगतान वितरण सेक्शन दिखाएं",
                    "उधार भुगतान वितरण पेज खोलें",
                    "उधार भुगतान वितरण मॉड्यूल में जाएं",
                    "उधार भुगतान विवरण दिखाएं",
                    "उधार भुगतान वितरण कहाँ देख सकते हैं",
                    "उधार भुगतान वितरण पेज पर ले जाएं",
                    "उधार भुगतान वितरण जानकारी खोलें",
                    "उधार भुगतान वितरण सेक्शन एक्सेस करें"
                ],
                "mr": [
                    "आगाऊ मोबदला वाटप उघडा",
                    "आगाऊ मोबदला वाटप मध्ये जा",
                    "आगाऊ मोबदला वाटप विभाग दाखवा",
                    "आगाऊ मोबदला वाटप पृष्ठ उघडा",
                    "आगाऊ मोबदला वाटप मॉड्यूलमध्ये जा",
                    "आगाऊ मोबदला वाटप माहिती दाखवा",
                    "आगाऊ मोबदला वाटप कुठे पाहता येईल",
                    "आगाऊ मोबदला वाटप पृष्ठावर घ्या",
                    "आगाऊ मोबदला वाटप तपशील उघडा",
                    "आगाऊ मोबदला वाटप विभागात प्रवेश करा"
                ]
            },

            "objection_list": {
                "en": [
                    "how to view objection list",
                    "show objection list",
                    "where can I see objections",
                    "open objection list",
                    "check objection list",
                    "how to check objections",
                    "view objections in system",
                    "where are objections listed",
                    "show me objections",
                    "see the objection list",
                    "show the list of objections",
                    "how to open objection list page"
                ],
                "hi": [
                    "आपत्ति सूची कैसे देखें",
                    "आपत्ति सूची दिखाएं",
                    "आपत्तियां कहां देखें",
                    "ऑब्जेक्शन लिस्ट खोलें",
                    "आपत्तियां कैसे जांचें",
                    "सिस्टम में आपत्तियां कैसे देखें",
                    "आपत्ति सूची कहां मिलेगी",
                    "मुझे आपत्तियां दिखाएं",
                    "ऑब्जेक्शन लिस्ट कैसे खोलें",
                    "आपत्तियों की सूची कैसे देखें"
                ],
                "mr": [
                    "हरकतींची यादी कशी पाहावी",
                    "हरकतींची यादी दाखवा",
                    "हरकती कुठे पाहू शकतो",
                    "ऑब्जेक्शन लिस्ट उघडा",
                    "हरकती कशा तपासायच्या",
                    "सिस्टममध्ये हरकती कशा पाहायच्या",
                    "हरकतींची यादी कुठे आहे",
                    "मला हरकती दाखवा",
                    "ऑब्जेक्शन लिस्ट कशी उघडायची",
                    "हरकतींची यादी कशी तपासावी"
                ]
            },

            "section_15": {
                "en": [
                    "how to check section 15",
                    "how to view section 15 details",
                    "open section 15 notice",
                    "how to edit section 15 covering letter",
                    "where can I find section 15",
                    "show section 15 notice",
                    "how to open section 15 page",
                    "where is section 15 option",
                    "how to check section 15 notice",
                    "how to edit section 15"
                ],
                "hi": [
                    "धारा 15 कैसे देखें",
                    "धारा 15 की जानकारी कैसे देखें",
                    "धारा 15 नोटिस कैसे खोलें",
                    "धारा 15 कवरिंग लेटर कैसे संपादित करें",
                    "धारा 15 कहां मिलेगी",
                    "धारा 15 नोटिस दिखाएं",
                    "धारा 15 पेज कैसे खोलें",
                    "धारा 15 विकल्प कहां है",
                    "धारा 15 नोटिस कैसे देखें",
                    "धारा 15 कैसे संपादित करें"
                ],
                "mr": [
                    "कलम 15 कसे पाहावे",
                    "कलम 15 ची माहिती कशी पाहावी",
                    "कलम 15 नोटीस कशी उघडायची",
                    "कलम 15 कव्हरिंग लेटर कसे संपादित करावे",
                    "कलम 15 कुठे आहे",
                    "कलम 15 नोटीस दाखवा",
                    "कलम 15 पेज कसे उघडायचे",
                    "कलम 15 पर्याय कुठे आहे",
                    "कलम 15 नोटीस कशी पाहावी",
                    "कलम 15 कसे संपादित करावे"
                ]
            },

            "section_19_time_extention_proposal_details": {
                "en": [
                    "how to check section 19 time extension proposal details",
                    "show section 19 time extension proposal",
                    "where can I see section 19 proposal details",
                    "open section 19 time extension proposal",
                    "how to view section 19 extended date proposal",
                    "show proposal details for section 19 time extension",
                    "how to check proposal details in section 19 time extension",
                    "where is section 19 time extension proposal",
                    "how to open section 19 proposal details",
                    "view section 19 time extension details"
                ],
                "hi": [
                    "धारा 19 समय विस्तार प्रस्ताव विवरण कैसे देखें",
                    "धारा 19 समय विस्तार प्रस्ताव दिखाएं",
                    "धारा 19 प्रस्ताव विवरण कहां देखें",
                    "धारा 19 समय विस्तार प्रस्ताव कैसे खोलें",
                    "धारा 19 विस्तारित तारीख के साथ प्रस्ताव कैसे देखें",
                    "धारा 19 समय विस्तार का प्रस्ताव विवरण दिखाएं",
                    "धारा 19 समय विस्तार में प्रस्ताव विवरण कैसे देखें",
                    "धारा 19 समय विस्तार प्रस्ताव कहां है",
                    "धारा 19 प्रस्ताव विवरण कैसे खोलें",
                    "धारा 19 समय विस्तार विवरण कैसे देखें"
                ],
                "mr": [
                    "कलम 19 मुदतवाढ प्रस्तावाची माहिती कशी पाहावी",
                    "कलम 19 मुदतवाढ प्रस्ताव दाखवा",
                    "कलम 19 प्रस्तावाची माहिती कुठे पाहू शकतो",
                    "कलम 19 मुदतवाढ प्रस्ताव कसा उघडायचा",
                    "कलम 19 विस्तारित तारखेसह प्रस्ताव कसा पाहायचा",
                    "कलम 19 मुदतवाढ प्रस्तावाची माहिती दाखवा",
                    "कलम 19 मुदतवाढ मध्ये प्रस्तावाची माहिती कशी पाहावी",
                    "कलम 19 मुदतवाढ प्रस्ताव कुठे आहे",
                    "कलम 19 प्रस्तावाची माहिती कशी उघडायची",
                    "कलम 19 मुदतवाढ तपशील कसे पाहायचे"
                ]
            },

            "re_send_back_to_dslr": {
                "en": [
                    "resend to dslr",
                    "re send back to dslr",
                    "send back to dslr",
                    "return jmr to dslr",
                    "send measurement back to dslr",
                    "forward back to dslr",
                    "submit again to dslr",
                    "resubmit to dslr",
                    "send back joint measurement to dslr",
                    "return to dslr officer"
                ],
                "hi": [
                    "डीएसएलआर को वापस भेजें",
                    "डीएसएलआर को पुनः भेजें",
                    "संयुक्त मापन डीएसएलआर को वापस भेजें",
                    "डीएसएलआर को फिर से भेजें",
                    "डीएसएलआर को लौटाएं",
                    "मापन विवरण डीएसएलआर को वापस करें",
                    "डीएसएलआर को दोबारा सबमिट करें",
                    "डीएसएलआर अधिकारी को वापस भेजें",
                    "संयुक्त मापन पुनः डीएसएलआर को भेजें",
                    "डीएसएलआर को पुनः अग्रेषित करें"
                ],
                "mr": [
                    "डीएसएलआर ला परत पाठवा",
                    "डीएसएलआर ला पुन्हा पाठवा",
                    "संयुक्त मोजणी डीएसएलआर ला परत पाठवा",
                    "डीएसएलआर कडे परत पाठवा",
                    "मोजणी तपशील डीएसएलआर ला परत करा",
                    "डीएसएलआर ला पुन्हा सबमिट करा",
                    "डीएसएलआर अधिकाऱ्याला परत पाठवा",
                    "संयुक्त मोजणी पुन्हा डीएसएलआर ला पाठवा",
                    "डीएसएलआर कडे पुनः अग्रेषित करा",
                    "डीएसएलआर ला परत पाठवायचे आहे"
                ]
            },

            "Namuna_A": {
                "en": [
                    "open namuna a",
                    "go to namuna a",
                    "access namuna a module",
                    "navigate to namuna a section",
                    "open rehabilitation section",
                    "go to rehabilitation module",
                    "show namuna a page",
                    "take me to rehabilitation records",
                    "open rehabilitation management page",
                    "namuna a section access",
                    "rehabilitation page access",
                    "work in rehabilitation section.",
                    "reach rehabilitation module",
                    "rehabilitation management page",
                    "manage rehabilitation details"
                ],
                "hi": [
                    "नमुना ए खोलें",
                    "नमुना ए में जाएं",
                    "नमुना ए मॉड्यूल खोलें",
                    "पुनर्वास सेक्शन खोलें",
                    "पुनर्वास मॉड्यूल में जाएं",
                    "नमुना ए पेज पर जाएं",
                    "पुनर्वास विभाग दिखाएं",
                    "नमुना ए सेक्शन एक्सेस करें",
                    "पुनर्वास प्रबंधन पेज खोलें",
                    "नमुना ए विभाग खोलें"
                ],
                "mr": [
                    "नमुना अ उघडा",
                    "नमुना अ मध्ये जा",
                    "नमुना अ मॉड्यूल उघडा",
                    "पुनर्वसन विभाग उघडा",
                    "पुनर्वसन मॉड्यूलमध्ये जा",
                    "नमुना अ पृष्ठावर जा",
                    "पुनर्वसन विभाग दाखवा",
                    "नमुना अ विभागात प्रवेश करा",
                    "पुनर्वसन व्यवस्थापन पृष्ठ उघडा",
                    "नमुना अ सेक्शन उघडा",
                    "पुनर्वसन संबंधित पृष्ठ",
                    "पुनर्वसन संबंधित पृष्ठावर",
                    "पुनर्वसन नोंदी",
                    "पुनर्वसन माहिती असलेले पृष्ठ"
                ]
            },
        }

        all_texts = []
        for key, langs in self.intent_profiles.items():
            for lang, texts in langs.items():
                all_texts.extend(texts)

        self.embedder = SimpleEmbedder(all_texts)


        
        # Precompute embeddings
        # print("🔄 Computing embeddings...", file=sys.stderr)
        self.intent_profile_embeddings = {}
        for key, langs in self.intent_profiles.items():
            self.intent_profile_embeddings[key] = {}
            for lang, texts in langs.items():
                self.intent_profile_embeddings[key][lang] = [
                    # self.embedder.encode(text, convert_to_tensor=True)
                    self.embedder.encode(text)
                    for text in texts
                ]

    def normalize(self, text: str) -> str:
        if not text:
            return ""
        text = unicodedata.normalize("NFKC", text.lower())
        text = re.sub(r"[^\w\s\u0900-\u097F]", " ", text)
        return re.sub(r"\s+", " ", text).strip()

    def remove_ui_noise(self, text: str) -> str:
        ui_words = [
            "dashboard", "sidebar", "page", "screen",
            "button", "click", "menu",
            "डैशबोर्ड", "पेज", "बटन",
            "डॅशबोर्ड", "पृष्ठ", "बटण"
        ]
        text = self.normalize(text)
        for w in ui_words:
            text = text.replace(w, "")
        return re.sub(r"\s+", " ", text).strip()

    def detect_intent(self, cleaned: str, lang: str, allowed_keys=None):
        # q_emb = self.embedder.encode(cleaned, convert_to_tensor=True)
        q_emb = self.embedder.encode(cleaned)
        best_key = None
        best_score = 0.0
        score_details = {}

        for key, langs in self.intent_profile_embeddings.items():
            # Skip keys not allowed for this role
            if allowed_keys is not None and key not in allowed_keys:
                continue
            intent_embs = langs.get(lang)
            if intent_embs is None:
                continue

            # scores = [util.cos_sim(q_emb, intent_emb).item() for intent_emb in intent_embs]
            scores = [
                self.embedder.cosine_similarity(q_emb, intent_emb)
                for intent_emb in intent_embs
            ]
            max_score = max(scores) if scores else 0.0
            avg_score = sum(scores) / len(scores) if scores else 0.0
            combined_score = (0.7 * max_score) + (0.3 * avg_score)
            
            score_details[key] = {
                'max': max_score,
                'avg': avg_score,
                'combined': combined_score
            }

            if combined_score > best_score:
                best_score = combined_score
                best_key = key

        # Apply confidence margin
        sorted_scores = sorted(score_details.values(), key=lambda x: x['combined'], reverse=True)
        if len(sorted_scores) >= 2:
            score_gap = sorted_scores[0]['combined'] - sorted_scores[1]['combined']
            threshold_adjustment = 0.05 if score_gap < 0.05 else 0.0
        else:
            threshold_adjustment = 0.0

        return best_key, best_score, threshold_adjustment

    def has_section_21_1_4_marker(self, text: str) -> bool:
        markers = [
            "21(1),(4)", "21 1 4", "subsection 4", "clause 4",
            "उपधारा 4", "उपकलम 4", "उपकलम चार", "कलम 21(1),(4)"
        ]
        return any(m in text for m in markers)

    def get_fallback(self, language: str, role: str = None) -> str:
        """Return a role-aware fallback message."""
        role_label = self._role_labels.get(role, "Punarbhu") if role else "Punarbhu"
        template = self._fallback_templates.get(language, self._fallback_templates["en"])
        return template.format(role=role_label)

    # ---------------------------------------------------------------------------
    # Keyword signals for intents that are NOT available to certain roles.
    # If a question matches these keywords AND the intent key is not in the
    # role's allowed keys, we short-circuit and return None (→ fallback).
    # This is necessary because SimpleEmbedder is bag-of-words: "create project"
    # and "change project" share the word "project" and score similarly.
    # ---------------------------------------------------------------------------
    INTENT_KEYWORD_SIGNALS = {
        # intent_key : { lang: [keywords that strongly signal this intent] }
        "create_project": {
            "en": ["create project", "new project", "add project", "make project", "start project"],
            "hi": ["प्रोजेक्ट बनाएं", "नया प्रोजेक्ट", "प्रोजेक्ट जोड़ें", "प्रोजेक्ट बनाना", "प्रोजेक्ट शुरू"],
            "mr": ["प्रकल्प तयार करा", "नवीन प्रकल्प", "प्रकल्प जोडा", "प्रकल्प बनवा", "प्रकल्प सुरू"],
        },
        "add_user": {
            "en": ["add user", "create user", "new user", "register user"],
            "hi": ["उपयोगकर्ता जोड़ें", "नया उपयोगकर्ता", "यूजर जोड़ें"],
            "mr": ["वापरकर्ता जोडा", "नवीन वापरकर्ता"],
        },
        "add_sub_user": {
            "en": ["add sub user", "add subuser", "create sub user", "new sub user"],
            "hi": ["उप उपयोगकर्ता जोड़ें", "सब यूजर"],
            "mr": ["उप वापरकर्ता जोडा"],
        },
    }

    def _keyword_signals_forbidden_intent(self, cleaned: str, lang: str, allowed_keys) -> bool:
        """
        Returns True if the question contains strong keyword signals for an intent
        that is NOT allowed for the current role. This prevents the bag-of-words
        embedder from matching a similar-but-forbidden intent (e.g. 'create project'
        matching 'change project' just because they share the word 'project').
        """
        if allowed_keys is None:
            return False  # No role restriction, nothing to block
        for intent_key, lang_keywords in self.INTENT_KEYWORD_SIGNALS.items():
            if intent_key in allowed_keys:
                continue  # This intent IS allowed for this role, skip
            keywords = lang_keywords.get(lang, []) + lang_keywords.get("en", [])
            for kw in keywords:
                if kw.lower() in cleaned:
                    return True  # Forbidden intent detected
        return False

    def semantic_match(self, question: str, lang: str, role: str = None):
        if not question:
            return None

        # Determine which intent keys and response map to use for this role
        allowed_keys = self.role_allowed_keys.get(role) if role else None
        response_map = ROLE_RESPONSE_MAPS.get(role) if role else None

        cleaned = self.remove_ui_noise(self.normalize(question))

        # Guard: if the question contains keywords that strongly signal a forbidden
        # intent, return None immediately so the caller shows the fallback message.
        if self._keyword_signals_forbidden_intent(cleaned, lang, allowed_keys):
            return None

        intent_key, intent_score, threshold_adj = self.detect_intent(cleaned, lang, allowed_keys)

        # Priority boost for Section 21(1),(4)
        if intent_key == "check_and_download_section_21_1":
            if self.has_section_21_1_4_marker(cleaned):
                if allowed_keys is None or "check_and_download_section_21_1_4" in allowed_keys:
                    intent_key = "check_and_download_section_21_1_4"

        # Base thresholds
        threshold = 0.45
        if lang == "hi":
            threshold = 0.42
        elif lang == "mr":
            threshold = 0.40
        threshold += threshold_adj

        if not intent_key or intent_score < threshold:
            return None

        # Get answer ONLY from the role-specific map
        # Do NOT fall back to other roles' maps — that would return answers
        # for intents the current role is not allowed to access (e.g. LAO
        # asking about create_project should get the fallback, not Samanvay's answer).
        answer = ""
        if response_map:
            answer = response_map.get(intent_key, {}).get(lang) or response_map.get(intent_key, {}).get("en", "")

        # If the intent key is not in this role's map, treat it as no match
        # so the caller returns the role-specific fallback message.
        if not answer:
            return None

        return {
            "key": intent_key,
            "answer": answer,
            "score": round(intent_score, 2)
        }

    def process_chat(self, messages, language="en", role=None):
        """Process chat request - REQUIRED METHOD"""
        question = next(
            (m["content"] for m in reversed(messages) if m.get("role") == "user"),
            ""
        )

        result = self.semantic_match(question, language, role)

        if result:
            return {
                "message": {
                    "role": "assistant",
                    "content": result["answer"]
                },
                "answer_key": result["key"],
                "language": language
            }

        return {
            "message": {
                "role": "assistant",
                "content": self.get_fallback(language, role)
            },
            "answer_key": None,
            "language": language
        }

    def process_tts(self, text, lang="en"):
        """Generate text-to-speech and return base64 - REQUIRED METHOD"""
        tts = gTTS(text=text, lang=lang)
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(tmp.name)
        tmp.close()
        
        with open(tmp.name, "rb") as f:
            audio_data = base64.b64encode(f.read()).decode("utf-8")
        
        os.remove(tmp.name)
        return audio_data


# --------------------------------------------------
# MAIN LOOP - Process requests from Node.js
# --------------------------------------------------
def main():
    chatbot = BhusampadanChatbot()
    # print("✅ Chatbot worker ready", file=sys.stderr)
    
    # Signal ready to Node.js
    print(json.dumps({"status": "ready"}))
    sys.stdout.flush()
    
    # Process requests in a loop
    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
            action = request.get("action")
            req_id = request.get("_requestId")
            
            if action == "chat":
                result = chatbot.process_chat(
                    request.get("messages", []),
                    request.get("language", "en"),
                    request.get("role", None)
                )
                response = {"success": True, "data": result, "_requestId": req_id}
                print(json.dumps(response))
                
            elif action == "get_response_by_key":
                text = get_response_by_key(
                    request.get("answer_key"),
                    request.get("language", "en")
                )
                response = {"success": True, "data": {"text": text}, "_requestId": req_id}
                print(json.dumps(response))

                
            elif action == "tts":
                audio = chatbot.process_tts(
                    request.get("text", ""),
                    request.get("lang", "en")
                )
                response = {"success": True, "data": {"audio": audio}, "_requestId": req_id}
                print(json.dumps(response))
                
            elif action == "ping":
                response = {"success": True, "data": {"status": "alive"}, "_requestId": req_id}
                print(json.dumps(response))
                
            else:
                response = {"success": False, "error": "Unknown action", "_requestId": req_id}
                print(json.dumps(response))
                
            sys.stdout.flush()
            
        except Exception as e:
            response = {"success": False, "error": str(e), "_requestId": req_id if 'req_id' in locals() else None}
            print(json.dumps(response))
            sys.stdout.flush()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("👋 Chatbot worker shutting down", file=sys.stderr)
    except Exception as e:
        print(f"❌ Worker error: {str(e)}", file=sys.stderr)
        sys.exit(1)