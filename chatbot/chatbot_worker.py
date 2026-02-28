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

    def semantic_match(self, question: str, lang: str, role: str = None):
        if not question:
            return None

        # Determine which intent keys and response map to use for this role
        allowed_keys = self.role_allowed_keys.get(role) if role else None
        response_map = ROLE_RESPONSE_MAPS.get(role) if role else None

        cleaned = self.remove_ui_noise(self.normalize(question))
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

        # Get answer from role-specific map, fall back to any available map
        answer = ""
        if response_map:
            answer = response_map.get(intent_key, {}).get(lang) or response_map.get(intent_key, {}).get("en", "")
        if not answer:
            for rmap in ROLE_RESPONSE_MAPS.values():
                answer = rmap.get(intent_key, {}).get(lang) or rmap.get(intent_key, {}).get("en", "")
                if answer:
                    break

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