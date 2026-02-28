"""
Multi-language Knowledge base for Punarbhu website
Contains accurate information in English, Hindi, and Marathi
"""
import re
import unicodedata

# ====================================================================
# ENGLISH KNOWLEDGE BASE
# ====================================================================
Punarbhu_KNOWLEDGE_EN = """
=== Punarbhu - OFFICIAL INFORMATION ===

Website Name: Punarbhu (पुनर्भू  )
Official Website URL: https://punarbhu.safevaults.in

=== OFFICE INFORMATION ===
Office Name: Buldhana Collector Office
Location: Buldhana, Maharashtra, India

Office Hours:
- Monday to Friday: 10:00 AM to 5:30 PM
- Saturday: 10:00 AM to 2:00 PM
- Sunday: Closed
- Public Holidays: Closed

=== ABOUT Punarbhu ===
Punarbhu is a land records management system for Buldhana District.
It provides digital access to land records, property information, and related government services.

=== SERVICES PROVIDED ===
1. Land Records Viewing
2. Property Registration Information
3. Land Ownership Verification
4. Certificate Services (7/12 Extract, Property Card)
5. Online Application Submission
6. Land Maps and Survey Information

=== CONTACT INFORMATION ===
Office: Buldhana Collector Office
District: Buldhana
State: Maharashtra
Country: India
Website: https://punarbhu.safevaults.in
"""

# ====================================================================
# HINDI KNOWLEDGE BASE
# ====================================================================
Punarbhu_KNOWLEDGE_HI = """
=== पुनर्भू   - आधिकारिक जानकारी ===

वेबसाइट का नाम: पुनर्भू  
आधिकारिक वेबसाइट URL: https://punarbhu.safevaults.in

=== कार्यालय की जानकारी ===
कार्यालय का नाम: बुलढाणा जिलाधिकारी कार्यालय
स्थान: बुलढाणा, महाराष्ट्र, भारत

कार्यालय समय:
- सोमवार से शुक्रवार: सुबह 10:00 बजे से शाम 5:30 बजे तक
- शनिवार: सुबह 10:00 बजे से दोपहर 2:00 बजे तक
- रविवार: बंद
- सार्वजनिक अवकाश: बंद

=== पुनर्भू   के बारे में ===
पुनर्भू   बुलढाणा जिले के लिए भूमि अभिलेख प्रबंधन  है।
यह भूमि अभिलेख, संपत्ति की जानकारी और संबंधित सरकारी सेवाओं तक डिजिटल पहुंच प्रदान करती है।

=== प्रदान की जाने वाली सेवाएं ===
1. भूमि अभिलेख देखना
2. संपत्ति पंजीकरण की जानकारी
3. भूमि स्वामित्व सत्यापन
4. प्रमाणपत्र सेवाएं (7/12 उद्धरण, संपत्ति कार्ड)
5. ऑनलाइन आवेदन जमा करना
6. भूमि मानचित्र और सर्वेक्षण जानकारी

=== संपर्क जानकारी ===
कार्यालय: बुलढाणा जिलाधिकारी कार्यालय
जिला: बुलढाणा
राज्य: महाराष्ट्र
देश: भारत
वेबसाइट: https://punarbhu.safevaults.in
"""

# ====================================================================
# MARATHI KNOWLEDGE BASE
# ====================================================================
Punarbhu_KNOWLEDGE_MR = """
=== पुनर्भू   - अधिकृत माहिती ===

संकेतस्थळाचे नाव: पुनर्भू  
अधिकृत संकेतस्थळ URL: https://punarbhu.safevaults.in

=== कार्यालयाची माहिती ===
कार्यालयाचे नाव: बुलढाणा जिल्हाधिकारी कार्यालय
स्थान: बुलढाणा, महाराष्ट्र, भारत

कार्यालयाचे वेळ:
- सोमवार ते शुक्रवार: सकाळी 10:00 ते संध्याकाळी 5:30
- शनिवार: सकाळी 10:00 ते दुपारी 2:00
- रविवार: बंद
- सार्वजनिक सुट्ट्या: बंद

=== पुनर्भू  बद्दल ===
पुनर्भू   बुलढाणा जिल्ह्यासाठी जमीन नोंदी व्यवस्थापन  आहे।
ही जमीन नोंदी, मालमत्ता माहिती आणि संबंधित सरकारी सेवांमध्ये डिजिटल प्रवेश प्रदान करते।

=== प्रदान केलेल्या सेवा ===
1. जमीन नोंदी पाहणे
2. मालमत्ता नोंदणी माहिती
3. जमीन मालकी पडताळणी
4. प्रमाणपत्र सेवा (7/12 उतारा, मालमत्ता कार्ड)
5. ऑनलाइन अर्ज सादर करणे
6. जमीन नकाशे आणि सर्वेक्षण माहिती

=== संपर्क माहिती ===
कार्यालय: बुलढाणा जिल्हाधिकारी कार्यालय
जिल्हा: बुलढाणा
राज्य: महाराष्ट्र
देश: भारत
संकेतस्थळ: https://punarbhu.safevaults.in
"""

# ====================================================================
# LANGUAGE MAPPING
# ====================================================================
KNOWLEDGE_BASES = {
    'en': Punarbhu_KNOWLEDGE_EN,
    'hi': Punarbhu_KNOWLEDGE_HI,
    'mr': Punarbhu_KNOWLEDGE_MR
}

# ====================================================================
# RESPONSE KEYS MAP - SAMANVAY OFFICER
# Keys accessible by Samanvay Officer
# ====================================================================
RESPONSE_KEYS_MAP_SAMANVAY_OFFICER = {
    'dashboard_change_project' : {
        'en' : 'on dashboard click on change project.',
        'hi' : 'डॅशबोर्ड पर प्रकल्प बदला पर क्लिक करें।',
        'mr' : 'डॅशबोर्डवरील प्रकल्प बदलावर क्लिक करा.'
    },

    'dashboard_all_document' : {
        'en' : 'on dashboard click on All Document so you can see all pdf documents you can view and download all as zip',
        'hi' : 'डॅशबोर्ड पर All Document पर क्लिक करें ताकि आप सभी पीडीएफ दस्तावेज़ देख सकें और उन्हें ज़िप फ़ाइल के रूप में डाउनलोड कर सकें।',
        'mr' : 'डॅशबोर्डवरील All Document वर क्लिक करा जेणेकरून तुम्हाला सर्व पीडीएफ डॉक्युमेंट्स दिसतील आणि तुम्ही ते सर्व झिप म्हणून पाहू आणि डाउनलोड करू शकाल.'
    },

    'dashboard_proposal_progress_status' : {
        'en' : 'on dashboard you can see Section 11,Section 12,Section 15,Section 19,Section 21,Section 23 and Payment so click any one for check any progress status.',
        'hi' : 'डॅशबोर्ड पर आप Section 11,Section 12,Section 15,Section 19,Section 21,Section 23 आणि Payment देखू शकता. कोणत्याही एकावर क्लिक करा ताकि कोणतीही प्रगतीची स्थिती तपासू शकता.',
        'mr' : 'डॅशबोर्डवरील आप Section 11,Section 12,Section 15,Section 19,Section 21,Section 23 आणि Payment देखू शकता. कोणत्याही एकावर क्लिक करा ताकि कोणतीही प्रगतीची स्थिती तपासू शकता.'
    },

    'add_user' : {
        'en' : 'On sidebar go to Administration -> User Management -> Click on Add button fill the form and click on Add User',
        'hi' : 'साइडबार में जाकर प्रशासन -> वापरकर्ता व्यवस्थापन पर जाएं -> जोडा बटन पर क्लिक करें, फॉर्म भरें और Add User पर क्लिक करें।',
        'mr' : 'साइडबारवरील प्रशासन -> वापरकर्ता व्यवस्थापन विभागात जा -> जोडा बटणावर क्लिक करा, फॉर्म भरा आणि Add User बटणावर क्लिक करा.'
    },

    'add_sub_user' : {
        'en' : 'On sidebar go to Administration -> Sub-User Management -> Click on Add Sub-User button fill the form and click on Add Sub-User button',
        'hi' : 'साइडबार में जाकर प्रशासन -> उप-वापरकर्ता व्यवस्थापन पर जाएं -> उप-वापरकर्ता जोड़ा बटन पर क्लिक करें, फॉर्म भरें और जोड़े पर क्लिक करें।',
        'mr' : 'साइडबारवरील प्रशासन -> उप-वापरकर्ता व्यवस्थापन विभागात जा -> उप-वापरकर्ता जोडा बटणावर क्लिक करा, फॉर्म भरा आणि जोड़ा बटणावर क्लिक करा.'
    },

    'create_project': {
        'en': 'On Sidebar go to Create/Edit Project -> Click on New Project button fill the form and select category.\n',
        'hi': 'साइडबार पर प्रकल्प व्यवस्थापन  -> नविन प्रकल्प बटन पर क्लिक करें, फॉर्म भरें और श्रेणी का चयन करें।\n',
        'mr': 'साइडबार वर प्रकल्प व्यवस्थापन -> नवीन प्रकल्प बटणावर क्लिक करा फॉर्म भरा आणि श्रेणी निवडा.\n',
    },

    'edit_project': {
        'en': 'Go to Create/Edit Project and click on Edit button.',
        'hi': 'प्रकल्प व्यवस्थापन में जाएं और संपादित बटन पर क्लिक करें।',
        'mr': 'प्रकल्प व्यवस्थापन विभागात जा आणि संपादन करा बटणावर क्लिक करा.',
    },

    'proposal_landholding' : {
        'en' : 'Go to Create/Edit Proposal and click on Landholding :\n 1) for see Details of Land To be Acquire like:\n -Appendix 4 \n -Appendix 5 \n -Appendix 7 \n -download Land Acquisition Officer Appointment \n -All Documents(नमुना "क" : भूसंपादन प्रस्ताव) \n -send to Respected Collector\n -send back to Project Incharge',
        'hi' : 'प्रस्ताव प्रबंधन में जाएं और Landholding पर क्लिक करें:\n 1) अधिग्रहित की जाने वाली भूमि का विवरण देखने के लिए, जैसे:\n -परिशिष्ट 4 \n -परिशिष्ट 5 \n -परिशिष्ट 7 \n -भूमि अधिग्रहण अधिकारी नियुक्ति डाउनलोड करें \n -सभी दस्तावेज़ (नमुना "क": भूसंपादन प्रस्ताव) \n -सम्मानित कलेक्टर को भेजें\n -Project Incharge को वापस भेजें',
        'mr' : 'भूसंपादन प्रस्ताव मध्ये जा आणि Landholding वर क्लिक करा:\n 1) संपादनासाठी प्रस्तावित जमिनीचा तपशील पाहा, जैसे:\n -परिशिष्ट 4 \n -परिशिष्ट 5 \n -परिशिष्ट 7 \n-भूसंपादन अधिकारी नियुक्ती पत्र डाउनलोड करा \n -सर्व दस्तावेज (नमुना "क": भूसंपादन प्रस्ताव) \n - मा.जिल्हाधिकारी यांच्याकडे पाठवा\n -Project Incharge परत पाठवा',
    },

    'section_11_covering_letter' : {
        'en' : 'Go to Publication Preliminary Notification and click on कलम 11 मान्यता so Section 11 Covering Letter will open.',
        'hi' : 'प्राथमिक अधिसूचना पर जाएं और कलम 11 मान्यता पर क्लिक करें ताकि धारा 11 आवरण पत्र खुल जाए।',
        'mr' : 'प्रारंभिक अधिसूचना वर जा आणि कलम 11 मान्यता वर क्लिक करा जेणेकरून कलम 11 मान्यता उघडेल.'
    },
}

# ====================================================================
# RESPONSE KEYS MAP - LAO (Land Acquisition Officer)
# Keys accessible by LAO
# ====================================================================
RESPONSE_KEYS_MAP_LAO = {
    'dashboard_change_project' : {
        'en' : 'on dashboard click on change project.',
        'hi' : 'डॅशबोर्ड पर प्रकल्प बदला पर क्लिक करें।',
        'mr' : 'डॅशबोर्डवरील प्रकल्प बदलावर क्लिक करा.'
    },

    'dashboard_all_document' : {
        'en' : 'on dashboard click on All Document so you can see all pdf documents you can view and download all as zip',
        'hi' : 'डॅशबोर्ड पर All Document पर क्लिक करें ताकि आप सभी पीडीएफ दस्तावेज़ देख सकें और उन्हें ज़िप फ़ाइल के रूप में डाउनलोड कर सकें।',
        'mr' : 'डॅशबोर्डवरील All Document वर क्लिक करा जेणेकरून तुम्हाला सर्व पीडीएफ डॉक्युमेंट्स दिसतील आणि तुम्ही ते सर्व झिप म्हणून पाहू आणि डाउनलोड करू शकाल.'
    },

    'dashboard_proposal_progress_status' : {
        'en' : 'on dashboard you can see Section 11,Section 12,Section 15,Section 19,Section 21,Section 23 and Payment so click any one for check any progress status.',
        'hi' : 'डॅशबोर्ड पर आप Section 11,Section 12,Section 15,Section 19,Section 21,Section 23 आणि Payment देखू शकता. कोणत्याही एकावर क्लिक करा ताकि कोणतीही प्रगतीची स्थिती तपासू शकता.',
        'mr' : 'डॅशबोर्डवरील आप Section 11,Section 12,Section 15,Section 19,Section 21,Section 23 आणि Payment देखू शकता. कोणत्याही एकावर क्लिक करा ताकि कोणतीही प्रगतीची स्थिती तपासू शकता.'
    },

    'add_sub_user' : {
        'en' : 'On sidebar Administration -> go to Sub-User Management -> Click on Add Sub-User button fill the form and click on Add Sub-User button',
        'hi' : 'साइडबार में जाकर प्रशासन -> उप-वापरकर्ता व्यवस्थापन पर जाएं -> उप-वापरकर्ता जोड़ा बटन पर क्लिक करें, फॉर्म भरें और जोड़े पर क्लिक करें।',
        'mr' : 'साइडबारवरील प्रशासन -> उप-वापरकर्ता व्यवस्थापन विभागात जा -> उप-वापरकर्ता जोडा बटणावर क्लिक करा, फॉर्म भरा आणि जोड़ा बटणावर क्लिक करा.'
    },

    'proposal_landholding' : {
        'en' : 'Go to Create/Edit Proposal and click on Landholding :\n 1) for see Details of Land To be Acquire like:\n -All Documents(नमुना "क" : भूसंपादन प्रस्ताव)',
        'hi' : 'प्रस्ताव प्रबंधन में जाएं और Landholding पर क्लिक करें:\n 1) अधिग्रहित की जाने वाली भूमि का विवरण देखने के लिए, जैसे:\n  -सभी दस्तावेज़ (नमुना "क": भूसंपादन प्रस्ताव)',
        'mr' : 'भूसंपादन प्रस्ताव मध्ये जा आणि Landholding वर क्लिक करा:\n 1) संपादनासाठी प्रस्तावित जमिनीचा तपशील पाहा, जैसे:\n -सर्व दस्तावेज (नमुना "क": भूसंपादन प्रस्ताव)'
    },
    
}

# ====================================================================
# RESPONSE KEYS MAP - PROJECT INCHARGE
# Keys accessible by Project Incharge Officer
# ====================================================================
RESPONSE_KEYS_MAP_PROJECT_INCHARGE = {
    'dashboard_change_project' : {
        'en' : 'on dashboard click on change project.',
        'hi' : 'डॅशबोर्ड पर प्रकल्प बदला पर क्लिक करें।',
        'mr' : 'डॅशबोर्डवरील प्रकल्प बदलावर क्लिक करा.'
    },

    'dashboard_all_document' : {
        'en' : 'on dashboard click on All Document so you can see all pdf documents you can view and download all as zip',
        'hi' : 'डॅशबोर्ड पर All Document पर क्लिक करें ताकि आप सभी पीडीएफ दस्तावेज़ देख सकें और उन्हें ज़िप फ़ाइल के रूप में डाउनलोड कर सकें।',
        'mr' : 'डॅशबोर्डवरील All Document वर क्लिक करा जेणेकरून तुम्हाला सर्व पीडीएफ डॉक्युमेंट्स दिसतील आणि तुम्ही ते सर्व झिप म्हणून पाहू आणि डाउनलोड करू शकाल.'
    },

    'dashboard_proposal_progress_status' : {
        'en' : 'on dashboard you can see Section 11,Section 12,Section 15,Section 19,Section 21,Section 23 and Payment so click any one for check any progress status.',
        'hi' : 'डॅशबोर्ड पर आप Section 11,Section 12,Section 15,Section 19,Section 21,Section 23 आणि Payment देखू शकता. कोणत्याही एकावर क्लिक करा ताकि कोणतीही प्रगतीची स्थिती तपासू शकता.',
        'mr' : 'डॅशबोर्डवरील आप Section 11,Section 12,Section 15,Section 19,Section 21,Section 23 आणि Payment देखू शकता. कोणत्याही एकावर क्लिक करा ताकि कोणतीही प्रगतीची स्थिती तपासू शकता.'
    },

    'add_sub_user' : {
        'en' : 'On sidebar Administration -> go to Sub-User Management -> Click on Add Sub-User button fill the form and click on Add Sub-User button',
        'hi' : 'साइडबार में जाकर प्रशासन -> उप-वापरकर्ता व्यवस्थापन पर जाएं -> उप-वापरकर्ता जोड़ा बटन पर क्लिक करें, फॉर्म भरें और जोड़े पर क्लिक करें।',
        'mr' : 'साइडबारवरील प्रशासन -> उप-वापरकर्ता व्यवस्थापन विभागात जा -> उप-वापरकर्ता जोडा बटणावर क्लिक करा, फॉर्म भरा आणि जोड़ा बटणावर क्लिक करा.'
    },

    'edit_project': {
        'en': 'Go to Create/Edit Project and click on Edit button.',
        'hi': 'प्रकल्प व्यवस्थापन में जाएं और संपादित बटन पर क्लिक करें।',
        'mr': 'प्रकल्प व्यवस्थापन विभागात जा आणि संपादन करा बटणावर क्लिक करा.',
    },

    'create_proposal': {
        'en' : 'Go to Proposal and click on Add Proposal button fill the form and click on save button.',
        'hi' : 'प्रस्ताव में जाएं और प्रस्ताव जोड़ें बटन पर क्लिक करें, फॉर्म भरें और सहेजें पर क्लिक करें।',
        'mr' : 'प्रस्ताव मध्ये जा आणि नवीन प्रस्ताव बटणावर क्लिक करा, फॉर्म भरा आणि सेव्ह करा बटणावर क्लिक करा.'
    },

    'edit_proposal' : {
        'en' : 'Go to Proposal and click on Edit button.',
        'hi' : 'प्रस्ताव में जाएं और संपादित बटन पर क्लिक करें।',
        'mr' : 'प्रस्ताव मध्ये जा आणि संपादित करा बटणावर क्लिक करा.'
    },
}

# ====================================================================
# RESPONSE KEYS MAP - SURVEYOR
# Keys accessible by Surveyor
# ====================================================================
RESPONSE_KEYS_MAP_SURVEYOR = {
    'dashboard_change_project' : {
        'en' : 'on dashboard click on change project.',
        'hi' : 'डॅशबोर्ड पर प्रकल्प बदला पर क्लिक करें।',
        'mr' : 'डॅशबोर्डवरील प्रकल्प बदलावर क्लिक करा.'
    },

    'dashboard_all_document' : {
        'en' : 'on dashboard click on All Document so you can see all pdf documents you can view and download all as zip',
        'hi' : 'डॅशबोर्ड पर All Document पर क्लिक करें ताकि आप सभी पीडीएफ दस्तावेज़ देख सकें और उन्हें ज़िप फ़ाइल के रूप में डाउनलोड कर सकें।',
        'mr' : 'डॅशबोर्डवरील All Document वर क्लिक करा जेणेकरून तुम्हाला सर्व पीडीएफ डॉक्युमेंट्स दिसतील आणि तुम्ही ते सर्व झिप म्हणून पाहू आणि डाउनलोड करू शकाल.'
    },

    'add_sub_user' : {
        'en' : 'On sidebar Administration -> go to Sub-User Management -> Click on Add Sub-User button fill the form and click on Add Sub-User button',
        'hi' : 'साइडबार में जाकर प्रशासन -> उप-वापरकर्ता व्यवस्थापन पर जाएं -> उप-वापरकर्ता जोड़ा बटन पर क्लिक करें, फॉर्म भरें और जोड़े पर क्लिक करें।',
        'mr' : 'साइडबारवरील प्रशासन -> उप-वापरकर्ता व्यवस्थापन विभागात जा -> उप-वापरकर्ता जोडा बटणावर क्लिक करा, फॉर्म भरा आणि जोड़ा बटणावर क्लिक करा.'
    },

}

# ====================================================================
# RESPONSE KEYS MAP - DSLR
# Keys accessible by DSLR Officer
# ====================================================================
RESPONSE_KEYS_MAP_DSLR = {
    'dashboard_change_project' : {
        'en' : 'on dashboard click on change project.',
        'hi' : 'डॅशबोर्ड पर प्रकल्प बदला पर क्लिक करें।',
        'mr' : 'डॅशबोर्डवरील प्रकल्प बदलावर क्लिक करा.'
    },

    'dashboard_all_document' : {
        'en' : 'on dashboard click on All Document so you can see all pdf documents you can view and download all as zip',
        'hi' : 'डॅशबोर्ड पर All Document पर क्लिक करें ताकि आप सभी पीडीएफ दस्तावेज़ देख सकें और उन्हें ज़िप फ़ाइल के रूप में डाउनलोड कर सकें।',
        'mr' : 'डॅशबोर्डवरील All Document वर क्लिक करा जेणेकरून तुम्हाला सर्व पीडीएफ डॉक्युमेंट्स दिसतील आणि तुम्ही ते सर्व झिप म्हणून पाहू आणि डाउनलोड करू शकाल.'
    },

    'dashboard_proposal_progress_status' : {
        'en' : 'on dashboard you can see Section 11,Section 12,Section 15,Section 19,Section 21,Section 23 and Payment so click any one for check any progress status.',
        'hi' : 'डॅशबोर्ड पर आप Section 11,Section 12,Section 15,Section 19,Section 21,Section 23 आणि Payment देखू शकता. कोणत्याही एकावर क्लिक करा ताकि कोणतीही प्रगतीची स्थिती तपासू शकता.',
        'mr' : 'डॅशबोर्डवरील आप Section 11,Section 12,Section 15,Section 19,Section 21,Section 23 आणि Payment देखू शकता. कोणत्याही एकावर क्लिक करा ताकि कोणतीही प्रगतीची स्थिती तपासू शकता.'
    },
    
    'add_sub_user' : {
        'en' : 'On sidebar Administration -> go to Sub-User Management -> Click on Add Sub-User button fill the form and click on Add Sub-User button',
        'hi' : 'साइडबार में जाकर प्रशासन -> उप-वापरकर्ता व्यवस्थापन पर जाएं -> उप-वापरकर्ता जोड़ा बटन पर क्लिक करें, फॉर्म भरें और जोड़े पर क्लिक करें।',
        'mr' : 'साइडबारवरील प्रशासन -> उप-वापरकर्ता व्यवस्थापन विभागात जा -> उप-वापरकर्ता जोडा बटणावर क्लिक करा, फॉर्म भरा आणि जोड़ा बटणावर क्लिक करा.'
    },
    
}

# ====================================================================
# RESPONSE KEYS MAP - TEHSILDAR
# Keys accessible by Tehsildar
# ====================================================================
RESPONSE_KEYS_MAP_TEHSILDAR = {
    'dashboard_change_project' : {
        'en' : 'on dashboard click on change project.',
        'hi' : 'डॅशबोर्ड पर प्रकल्प बदला पर क्लिक करें।',
        'mr' : 'डॅशबोर्डवरील प्रकल्प बदलावर क्लिक करा.'
    },

    'dashboard_all_document' : {
        'en' : 'on dashboard click on All Document so you can see all pdf documents you can view and download all as zip',
        'hi' : 'डॅशबोर्ड पर All Document पर क्लिक करें ताकि आप सभी पीडीएफ दस्तावेज़ देख सकें और उन्हें ज़िप फ़ाइल के रूप में डाउनलोड कर सकें।',
        'mr' : 'डॅशबोर्डवरील All Document वर क्लिक करा जेणेकरून तुम्हाला सर्व पीडीएफ डॉक्युमेंट्स दिसतील आणि तुम्ही ते सर्व झिप म्हणून पाहू आणि डाउनलोड करू शकाल.'
    },
    
    'add_sub_user' : {
        'en' : 'On sidebar Administration -> go to Sub-User Management -> Click on Add Sub-User button fill the form and click on Add Sub-User button',
        'hi' : 'साइडबार में जाकर प्रशासन -> उप-वापरकर्ता व्यवस्थापन पर जाएं -> उप-वापरकर्ता जोड़ा बटन पर क्लिक करें, फॉर्म भरें और जोड़े पर क्लिक करें।',
        'mr' : 'साइडबारवरील प्रशासन -> उप-वापरकर्ता व्यवस्थापन विभागात जा -> उप-वापरकर्ता जोडा बटणावर क्लिक करा, फॉर्म भरा आणि जोड़ा बटणावर क्लिक करा.'
    },
}

# ====================================================================
# RESPONSE KEYS MAP - DRO
# Keys accessible by DRO Officer
# ====================================================================
RESPONSE_KEYS_MAP_DRO = {
    'dashboard_change_project' : {
        'en' : 'on dashboard click on change project.',
        'hi' : 'डॅशबोर्ड पर प्रकल्प बदला पर क्लिक करें।',
        'mr' : 'डॅशबोर्डवरील प्रकल्प बदलावर क्लिक करा.'
    },

    'dashboard_all_document' : {
        'en' : 'on dashboard click on All Document so you can see all pdf documents you can view and download all as zip',
        'hi' : 'डॅशबोर्ड पर All Document पर क्लिक करें ताकि आप सभी पीडीएफ दस्तावेज़ देख सकें और उन्हें ज़िप फ़ाइल के रूप में डाउनलोड कर सकें।',
        'mr' : 'डॅशबोर्डवरील All Document वर क्लिक करा जेणेकरून तुम्हाला सर्व पीडीएफ डॉक्युमेंट्स दिसतील आणि तुम्ही ते सर्व झिप म्हणून पाहू आणि डाउनलोड करू शकाल.'
    },

    'dashboard_proposal_progress_status' : {
        'en' : 'on dashboard you can see Section 11,Section 12,Section 15,Section 19,Section 21,Section 23 and Payment so click any one for check any progress status.',
        'hi' : 'डॅशबोर्ड पर आप Section 11,Section 12,Section 15,Section 19,Section 21,Section 23 आणि Payment देखू शकता. कोणत्याही एकावर क्लिक करा ताकि कोणतीही प्रगतीची स्थिती तपासू शकता.',
        'mr' : 'डॅशबोर्डवरील आप Section 11,Section 12,Section 15,Section 19,Section 21,Section 23 आणि Payment देखू शकता. कोणत्याही एकावर क्लिक करा ताकि कोणतीही प्रगतीची स्थिती तपासू शकता.'
    },

    'add_sub_user' : {
        'en' : 'On sidebar Administration -> go to Sub-User Management -> Click on Add Sub-User button fill the form and click on Add Sub-User button',
        'hi' : 'साइडबार में जाकर प्रशासन -> उप-वापरकर्ता व्यवस्थापन पर जाएं -> उप-वापरकर्ता जोड़ा बटन पर क्लिक करें, फॉर्म भरें और जोड़े पर क्लिक करें।',
        'mr' : 'साइडबारवरील प्रशासन -> उप-वापरकर्ता व्यवस्थापन विभागात जा -> उप-वापरकर्ता जोडा बटणावर क्लिक करा, फॉर्म भरा आणि जोड़ा बटणावर क्लिक करा.'
    },
    
}

# ====================================================================
# RESPONSE KEYS MAP - COLLECTOR
# Keys accessible by Collector
# ====================================================================
RESPONSE_KEYS_MAP_COLLECTOR = {
    'dashboard_change_project' : {
        'en' : 'on dashboard click on change project.',
        'hi' : 'डॅशबोर्ड पर प्रकल्प बदला पर क्लिक करें।',
        'mr' : 'डॅशबोर्डवरील प्रकल्प बदलावर क्लिक करा.'
    },

    'dashboard_all_document' : {
        'en' : 'on dashboard click on All Document so you can see all pdf documents you can view and download all as zip',
        'hi' : 'डॅशबोर्ड पर All Document पर क्लिक करें ताकि आप सभी पीडीएफ दस्तावेज़ देख सकें और उन्हें ज़िप फ़ाइल के रूप में डाउनलोड कर सकें।',
        'mr' : 'डॅशबोर्डवरील All Document वर क्लिक करा जेणेकरून तुम्हाला सर्व पीडीएफ डॉक्युमेंट्स दिसतील आणि तुम्ही ते सर्व झिप म्हणून पाहू आणि डाउनलोड करू शकाल.'
    },

    'dashboard_proposal_progress_status' : {
        'en' : 'on dashboard you can see Section 11,Section 12,Section 15,Section 19,Section 21,Section 23 and Payment so click any one for check any progress status.',
        'hi' : 'डॅशबोर्ड पर आप Section 11,Section 12,Section 15,Section 19,Section 21,Section 23 आणि Payment देखू शकता. कोणत्याही एकावर क्लिक करा ताकि कोणतीही प्रगतीची स्थिती तपासू शकता.',
        'mr' : 'डॅशबोर्डवरील आप Section 11,Section 12,Section 15,Section 19,Section 21,Section 23 आणि Payment देखू शकता. कोणत्याही एकावर क्लिक करा ताकि कोणतीही प्रगतीची स्थिती तपासू शकता.'
    },

    'add_user' : {
        'en' : 'On sidebar go to Administration -> User Management -> Click on Add button fill the form and click on Add User',
        'hi' : 'साइडबार में जाकर प्रशासन -> वापरकर्ता व्यवस्थापन पर जाएं -> जोडा बटन पर क्लिक करें, फॉर्म भरें और Add User पर क्लिक करें।',
        'mr' : 'साइडबारवरील प्रशासन -> वापरकर्ता व्यवस्थापन विभागात जा -> जोडा बटणावर क्लिक करा, फॉर्म भरा आणि Add User बटणावर क्लिक करा.'
    },

    'add_sub_user' : {
        'en' : 'On sidebar Administration -> go to Sub-User Management -> Click on Add Sub-User button fill the form and click on Add Sub-User button',
        'hi' : 'साइडबार में जाकर प्रशासन -> उप-वापरकर्ता व्यवस्थापन पर जाएं -> उप-वापरकर्ता जोड़ा बटन पर क्लिक करें, फॉर्म भरें और जोड़े पर क्लिक करें।',
        'mr' : 'साइडबारवरील प्रशासन -> उप-वापरकर्ता व्यवस्थापन विभागात जा -> उप-वापरकर्ता जोडा बटणावर क्लिक करा, फॉर्म भरा आणि जोड़ा बटणावर क्लिक करा.'
    },
    
    'create_project': {
        'en': 'On Sidebar go to Create/Edit Project -> Click on New Project button fill the form and select category.\n',
        'hi': 'साइडबार पर प्रकल्प व्यवस्थापन  -> नविन प्रकल्प बटन पर क्लिक करें, फॉर्म भरें और श्रेणी का चयन करें।\n',
        'mr': 'साइडबार वर प्रकल्प व्यवस्थापन -> नवीन प्रकल्प बटणावर क्लिक करा फॉर्म भरा आणि श्रेणी निवडा.\n',
    },

    'edit_project': {
        'en': 'Go to Create/Edit Project and click on Edit button.',
        'hi': 'प्रकल्प व्यवस्थापन में जाएं और संपादित बटन पर क्लिक करें।',
        'mr': 'प्रकल्प व्यवस्थापन विभागात जा आणि संपादन करा बटणावर क्लिक करा.',
    },

    'create_proposal': {
        'en' : 'Go to Proposal and click on Add Proposal button fill the form and click on save button.',
        'hi' : 'प्रस्ताव में जाएं और प्रस्ताव जोड़ें बटन पर क्लिक करें, फॉर्म भरें और सहेजें पर क्लिक करें।',
        'mr' : 'प्रस्ताव मध्ये जा आणि नवीन प्रस्ताव बटणावर क्लिक करा, फॉर्म भरा आणि सेव्ह करा बटणावर क्लिक करा.'
    },

    'edit_proposal' : {
        'en' : 'Go to Proposal and click on Edit button.',
        'hi' : 'प्रस्ताव में जाएं और संपादित बटन पर क्लिक करें।',
        'mr' : 'प्रस्ताव मध्ये जा आणि संपादित करा बटणावर क्लिक करा.'
    },

    'proposal_landholding' : {
        'en' : 'Go to Create/Edit Proposal and click on Landholding :\n 1) for see Details of Land To be Acquire like:\n -download Land Acquisition Officer Appointment \n -All Documents(नमुना "क" : भूसंपादन प्रस्ताव) \n -Back to Samanvay \n -Assign LAO Officer',
        'hi' : 'प्रस्ताव प्रबंधन में जाएं और Landholding पर क्लिक करें:\n 1) अधिग्रहित की जाने वाली भूमि का विवरण देखने के लिए, जैसे:\n -भूमि अधिग्रहण अधिकारी नियुक्ति डाउनलोड करें \n -सभी दस्तावेज़ (नमुना "क": भूसंपादन प्रस्ताव) \n -Back to Samanvay \n -LAO अधिकारी नियुक्त करा ',
        'mr' : 'भूसंपादन प्रस्ताव मध्ये जा आणि Landholding वर क्लिक करा:\n 1) संपादनासाठी प्रस्तावित जमिनीचा तपशील पाहा, जैसे:\n -भूसंपादन अधिकारी नियुक्ती पत्र डाउनलोड करा \n -सर्व दस्तावेज (नमुना "क": भूसंपादन प्रस्ताव) \n -Back to Samanvay \n-LAO अधिकारी नियुक्त करा ',
    },
}

def get_knowledge_base(language: str = 'en') -> str:
    """Get knowledge base for specified language"""
    return KNOWLEDGE_BASES.get(language, Punarbhu_KNOWLEDGE_EN)

def get_response_by_key(answer_key: str, language: str = 'en', role: str = None) -> str:
    """
    Get response by key in specified language.
    Optionally filter by role. Supported roles: 'samanvay_officer', 'lao', 'project_incharge',
    'surveyor', 'dslr', 'tehsildar', 'dro', 'collector'.
    Falls back to searching all role maps if key is not found in the given role map.
    """
    ROLE_MAP = {
        'samanvay_officer': RESPONSE_KEYS_MAP_SAMANVAY_OFFICER,
        'lao': RESPONSE_KEYS_MAP_LAO,
        'project_incharge': RESPONSE_KEYS_MAP_PROJECT_INCHARGE,
        'surveyor': RESPONSE_KEYS_MAP_SURVEYOR,
        'dslr': RESPONSE_KEYS_MAP_DSLR,
        'tehsildar': RESPONSE_KEYS_MAP_TEHSILDAR,
        'dro': RESPONSE_KEYS_MAP_DRO,
        'collector': RESPONSE_KEYS_MAP_COLLECTOR,
    }
    if role and role in ROLE_MAP:
        role_map = ROLE_MAP[role]
        if answer_key in role_map:
            return role_map[answer_key].get(language, role_map[answer_key]['en'])
    # Fallback: search all role maps
    for _, role_map in ROLE_MAP.items():
        if answer_key in role_map:
            return role_map[answer_key].get(language, role_map[answer_key]['en'])
    return None


def get_response_by_key_for_role(answer_key: str, role: str, language: str = 'en') -> str:
    """
    Get response by key strictly for a specific role and language.
    Returns None if the key is not accessible for the given role.
    Supported roles: 'samanvay_officer', 'lao', 'project_incharge',
    'surveyor', 'dslr', 'tehsildar', 'dro', 'collector'
    """
    ROLE_MAP = {
        'samanvay_officer': RESPONSE_KEYS_MAP_SAMANVAY_OFFICER,
        'lao': RESPONSE_KEYS_MAP_LAO,
        'project_incharge': RESPONSE_KEYS_MAP_PROJECT_INCHARGE,
        'surveyor': RESPONSE_KEYS_MAP_SURVEYOR,
        'dslr': RESPONSE_KEYS_MAP_DSLR,
        'tehsildar': RESPONSE_KEYS_MAP_TEHSILDAR,
        'dro': RESPONSE_KEYS_MAP_DRO,
        'collector': RESPONSE_KEYS_MAP_COLLECTOR,
    }
    role_map = ROLE_MAP.get(role)
    if role_map is None or answer_key not in role_map:
        return None
    return role_map[answer_key].get(language, role_map[answer_key]['en'])

def search_knowledge(query: str, language: str = 'en') -> str:
    """
    Search for relevant knowledge based on the query.
    Returns only relevant snippets, not the entire knowledge base.
    """
    if not query:
        if language == 'hi':
            return "पुनर्भू   - बुलढाणा जिलाधिकारी कार्यालय की आधिकारिक भूमि अभिलेख ।"
        elif language == 'mr':
            return "पुनर्भू   - बुलढाणा जिल्हाधिकारी कार्यालयाची अधिकृत जमीन नोंदी ."
        else:
            return "Punarbhu - Official land records system of Buldhana Collector Office."
            
    # Normalize query
    def _normalize_query(q: str) -> str:
        if not q:
            return ""
        s = unicodedata.normalize('NFKC', q)
        s = s.lower()
        s = re.sub(r"[^\w\s\u0900-\u097F]", " ", s)
        return re.sub(r"\s+", " ", s).strip()

    query = _normalize_query(query)

    # Return minimal context
    if language == 'hi':
        return """पुनर्भू  - बुलढाणा जिलाधिकारी कार्यालय
    संपर्क: https://punarbhu.safevaults.in
    कार्यालय समय: सोमवार-शुक्रवार 10:00-17:30"""
    elif language == 'mr':
        return """पुनर्भू  - बुलढाणा जिल्हाधिकारी कार्यालय
    संपर्क: https://punarbhu.safevaults.in
    कार्यालय वेळ: सोमवार-शुक्रवार 10:00-17:30"""
    else:
        return """Punarbhu - Buldhana Collector Office
    Contact: https://punarbhu.safevaults.in
    Office Hours: Monday-Friday 10:00-17:30"""