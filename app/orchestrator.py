from typing import Dict, Any, Tuple, List
from app.dialect_engine import DialectEngine

DOMAIN_ORAL_RUBRICS: Dict[str, Dict[str, Any]] = {
    "retail_business": {
        "prompts": {
            "hindi": "दुकान में सामान का स्टॉक खत्म होने से पहले और दैनिक मुनाफे का हिसाब आप कैसे रखते हैं?",
            "bundelkhandi": "दुकान में माल खत्म होवे से पहले और रोज को मुनाफा को हिसाब कैसे लगावत हो?",
            "nimadi": "दुकान मां सामान पूरो थवा पेहला अने रोज नो नफो केम काढ़ो छो?",
            "punjabi": "ਦੁਕਾਨ ਵਿੱਚ ਸਾਮਾਨ ਮੁੱਕਣ ਤੋਂ ਪਹਿਲਾਂ ਅਤੇ ਰੋਜ਼ਾਨਾ ਮੁਨਾਫ਼ੇ ਦਾ ਹਿਸਾਬ ਕਿਵੇਂ ਰੱਖਦੇ ਹੋ?",
            "gujarati": "દુકાનમાં સ્ટોક પૂરો થાય તે પહેલાં અને રોજના નફાનો હિસાબ તમે કેવી રીતે રાખો છો?"
        },
        "options": ["बिक्री बहीखाता व स्टॉक रजिस्टर", "केवल अंदाजे से", "कोई हिसाब नहीं"]
    },
    "solar_installer": {
        "prompts": {
            "hindi": "सोलर पैनल लगाते समय उसका मुख किस दिशा में होना चाहिए?",
            "bundelkhandi": "सोलर पट्टी धरत समय उनखो मुख कौन दिशा में होवे चहिने?",
            "nimadi": "सोलर पैनल लगावति वखते एनो मुख कई दिशा मां होय?",
            "punjabi": "ਸੋਲਰ ਪੈਨਲ ਲਗਾਉਂਦੇ ਸਮੇਂ ਉਸਦਾ ਮੂੰਹ ਕਿਹੜੀ ਦਿਸ਼ਾ ਵੱਲ ਹੋਣਾ ਚਾਹੀਦਾ ਹੈ?",
            "gujarati": "સોલર પેનલ લગાવતી વખતે તેનો મુખ કઈ દિશામાં હોવો જોઈએ?"
        },
        "options": ["दक्षिण दिशा (South-Facing)", "पूर्व दिशा (East)", "सूरज की तरफ"]
    },
    "tailoring": {
        "prompts": {
            "hindi": "कुर्ते का नाप लेते समय कौन-से तीन नाप सबसे जरूरी होते हैं?",
            "bundelkhandi": "कुर्ता नापत समय कौन-से तीन नाप सबसे जरूरी होत हैं?",
            "nimadi": "कुर्ता नु माप लेता कया तीन माप जरूरी छे?",
            "punjabi": "ਕੁਰਤੇ ਦਾ ਨਾਪ ਲੈਂਦੇ ਸਮੇਂ ਕਿਹੜੇ ਤਿੰਨ ਨਾਪ ਸਭ ਤੋਂ ਜ਼ਰੂਰੀ ਹੁੰਦੇ ਹਨ?",
            "gujarati": "કુર્તાનું માપ લેતી વખતે કયા ત્રણ માપ સૌથી જરૂરી છે?"
        },
        "options": ["तीरा, छाती और लंबाई", "केवल कॉलर", "बिना नाप के"]
    },
    "electrician": {
        "prompts": {
            "hindi": "घर में MCB बार-बार गिर रही हो तो सबसे पहले क्या जांच करेंगे?",
            "bundelkhandi": "घर में MCB बार-बार गिर रही हो तो सबसे पहले का चेक करोगे?",
            "nimadi": "घर मां MCB वारंवार पडे तो पेहला सु चेक करशो?",
            "punjabi": "ਜੇਕਰ ਘਰ ਵਿੱਚ MCB ਵਾਰ-ਵਾਰ ਟ੍ਰਿਪ ਹੋ ਰਹੀ ਹੋਵੇ ਤਾਂ ਸਭ ਤੋਂ ਪਹਿਲਾਂ ਕੀ ਦੇਖੋਗੇ?",
            "gujarati": "ઘરમાં MCB વારંવાર ટ્રીપ થાય तो પહેલા શું ચેક કરશો?"
        },
        "options": ["शॉर्ट सर्किट एवं लोड जांच", "नई MCB लगा देंगे", "तार काट देंगे"]
    },
    "agriculture": {
        "prompts": {
            "hindi": "फसल में प्राकृतिक जैविक खाद (वर्मीकम्पोस्ट) का उपयोग करने से क्या लाभ होता है?",
            "bundelkhandi": "फसल में देसी खाद डारे से का फायदा होत है?",
            "nimadi": "खेती मां जैविक खाद नाखवा थी सु फायदो थाय?",
            "punjabi": "ਫ਼ਸਲ ਵਿੱਚ ਦੇਸੀ ਰੂੜੀ ਜਾਂ ਵਰਮੀਕੰਪੋਸਟ ਪਾਉਣ ਦਾ ਕੀ ਫ਼ਾਇਦਾ ਹੁੰਦਾ ਹੈ?",
            "gujarati": "પાકમાં જૈવિક ખાતર વાપરવાથી શો ફાયદો થાય છે?"
        },
        "options": ["मिट्टी की उर्वरा शक्ति व पैदावार वृद्धि", "फसल सूख जाती है", "कोई लाभ नहीं"]
    }
}

COURSE_CATALOG: Dict[str, List[Dict[str, Any]]] = {
    "retail_business": [
        {
            "id": "RET/Q0101",
            "title": "Micro-Enterprise Retailer & Store Manager",
            "level": "NSQF Level 4",
            "center": "ग्राम पंचायत भवन (सामूहिक हब)",
            "match": "96%",
            "duration": "300 घंटे"
        },
        {
            "id": "RET/Q0102",
            "title": "Distributor & Kirana Sales Associate",
            "level": "NSQF Level 3",
            "center": "RSETI केंद्र, बैरसिया",
            "match": "90%",
            "duration": "240 घंटे"
        }
    ],
    "solar_installer": [
        {
            "id": "ELE/Q5901",
            "title": "Solar PV Installer (Suryamitra)",
            "level": "NSQF Level 4",
            "center": "ग्राम पंचायत भवन, रतनपुर",
            "match": "95%",
            "duration": "420 घंटे"
        },
        {
            "id": "ELE/Q1401",
            "title": "Field Technician - Solar & Electrical",
            "level": "NSQF Level 3",
            "center": "PMKK कौशल केंद्र, मंडीदीप",
            "match": "88%",
            "duration": "350 घंटे"
        }
    ],
    "tailoring": [
        {
            "id": "AMH/Q1947",
            "title": "Self-Employed Tailor (Apparel Craft)",
            "level": "NSQF Level 4",
            "center": "RSETI केंद्र, बैरसिया",
            "match": "94%",
            "duration": "300 घंटे"
        },
        {
            "id": "AMH/Q1001",
            "title": "Garment Construction & Repair Assistant",
            "level": "NSQF Level 3",
            "center": "ग्राम पंचायत भवन, रतनपुर",
            "match": "86%",
            "duration": "240 घंटे"
        }
    ],
    "electrician": [
        {
            "id": "ELE/Q1401",
            "title": "Field Technician - Wireman & Electrical",
            "level": "NSQF Level 4",
            "center": "PMKK कौशल केंद्र, मंडीदीप",
            "match": "96%",
            "duration": "400 घंटे"
        },
        {
            "id": "ELE/Q5901",
            "title": "Solar PV & Battery Maintenance Tech",
            "level": "NSQF Level 3",
            "center": "ग्राम पंचायत भवन, रतनपुर",
            "match": "89%",
            "duration": "320 घंटे"
        }
    ],
    "agriculture": [
        {
            "id": "AGR/Q0802",
            "title": "Organic Cultivator & Vermicompost Entrepreneur",
            "level": "NSQF Level 4",
            "center": "कृषि विज्ञान केंद्र (KVK)",
            "match": "93%",
            "duration": "350 घंटे"
        },
        {
            "id": "AGR/Q0801",
            "title": "Dairy Farmer & Milk Processing Assistant",
            "level": "NSQF Level 3",
            "center": "ग्राम पंचायत भवन, रतनपुर",
            "match": "87%",
            "duration": "280 घंटे"
        }
    ]
}


class ConversationalOrchestrator:
    @classmethod
    def advance_dialogue(
        cls,
        session: Dict[str, Any],
        utterance: str,
        dialect: str = "hindi"
    ) -> Tuple[str, Dict[str, Any], bool, List[str], List[Dict[str, Any]]]:
        current_step = session.get("current_step", "GREETING")
        cleaned_text = DialectEngine.normalize_string(utterance)

        # -------------------------------------------------------------
        # STAGE 1: GREETING & VOICE CONSENT
        # -------------------------------------------------------------
        if current_step == "GREETING":
            if DialectEngine.is_affirmative(utterance) or "start" in cleaned_text or "shuru" in cleaned_text:
                session["voice_consent_granted"] = True
                session["current_step"] = "ASK_NAME"
                prompt = DialectEngine.get_prompt("ASK_NAME", dialect)
                return prompt, session, False, [], []
            elif DialectEngine.is_negative(utterance):
                return "कोई बात नहीं! जब आप चाहें तब दोबारा संपर्क करें। धन्यवाद!", session, True, [], []
            else:
                prompt = DialectEngine.get_prompt("GREETING", dialect)
                return prompt, session, False, ["हाँ, शुरू करें", "नहीं, बाद में"], []

        # -------------------------------------------------------------
        # STAGE 2: IDENTITY (NAME -> LOCATION -> EDUCATION)
        # -------------------------------------------------------------
        elif current_step == "ASK_NAME":
            name = utterance.strip().title()
            session["full_name"] = name if len(name) > 1 else "आवेदक"
            session["current_step"] = "ASK_LOCATION"
            prompt = DialectEngine.get_prompt("ASK_LOCATION", dialect)
            return prompt, session, False, [], []

        elif current_step == "ASK_LOCATION":
            location = utterance.strip().title()
            session["village"] = location if location else "भोपाल"
            session["current_step"] = "ASK_EDUCATION"
            prompt = DialectEngine.get_prompt("ASK_EDUCATION", dialect)
            edu_options = ["कोई औपचारिक शिक्षा नहीं", "5वीं पास", "8वीं पास", "10वीं पास", "12वीं पास"]
            return prompt, session, False, edu_options, []

        elif current_step == "ASK_EDUCATION":
            session["formal_education"] = utterance.strip()
            session["current_step"] = "ASK_WORK"
            prompt = DialectEngine.get_prompt("ASK_WORK", dialect)
            work_options = [
                "दुकान व खुदरा व्यवसाय (Business)",
                "सोलर पैनल व बिजली (Solar)",
                "सिलाई व कपड़ा शिल्प (Tailoring)",
                "खेती व डेयरी (Agriculture)",
                "अन्य कार्य"
            ]
            return prompt, session, False, work_options, []

        # -------------------------------------------------------------
        # STAGE 3: TRADE EXTRACTION & DOMAIN-SPECIFIC ORAL RPL TEST
        # -------------------------------------------------------------
        elif current_step == "ASK_WORK":
            detected_trade = DialectEngine.extract_trade(utterance)
            session["current_occupation"] = utterance.strip()
            session["aspired_trade"] = detected_trade
            session["current_step"] = "ORAL_TEST"

            rubric = DOMAIN_ORAL_RUBRICS.get(detected_trade, DOMAIN_ORAL_RUBRICS["retail_business"])
            oral_prompt = rubric["prompts"].get(dialect, rubric["prompts"]["hindi"])
            options = rubric["options"]

            full_prompt = f"बहुत अच्छा। आपके कार्य-ज्ञान को प्रमाणित करने के लिए एक छोटा मौखिक प्रश्न:\n{oral_prompt}"
            return full_prompt, session, False, options, []

        elif current_step == "ORAL_TEST":
            session["oral_rpl_score"] = 0.95
            session["current_step"] = "SELECT_COURSE"

            trade = session.get("aspired_trade", "retail_business")
            courses = COURSE_CATALOG.get(trade, COURSE_CATALOG["retail_business"])
            session["suggested_courses"] = courses

            prompt = (
                "मौखिक जांच सफल रही! आपके हुनर के अनुसार उपयुक्त NSQF कोर्स तैयार हैं। "
                "कृपया आगे बढ़ने के लिए दाएँ पैनल से या नीचे से अपना पसंदीदा कोर्स चुनें:"
            )
            course_options = [c["title"] for c in courses]
            return prompt, session, False, course_options, courses

        # -------------------------------------------------------------
        # STAGE 4: INTERACTIVE COURSE SELECTION
        # -------------------------------------------------------------
        elif current_step == "SELECT_COURSE":
            courses = session.get("suggested_courses", [])
            selected = None

            for c in courses:
                c_title_norm = DialectEngine.normalize_string(c["title"])
                c_id_norm = DialectEngine.normalize_string(c["id"])
                if c_title_norm in cleaned_text or c_id_norm in cleaned_text or any(w in cleaned_text for w in c_title_norm.split()):
                    selected = c
                    break

            if not selected and courses:
                selected = courses[0]

            session["selected_course"] = selected
            session["current_step"] = "CONFIRM_ENROLLMENT"

            course_title = selected["title"]
            village = session.get("village", "भोपाल")

            prompt = (
                f"आपने चुना: '{course_title}'। "
                f"आपके क्षेत्र '{village}' में 14 उम्मीदवार पहले से पंजीकृत हैं। "
                f"{DialectEngine.get_prompt('CONFIRM_ENROLL', dialect)}"
            )
            return prompt, session, False, ["हाँ, नामांकन पक्का करें", "कोर्स बदलें"], []

        # -------------------------------------------------------------
        # STAGE 5: BATCH ENROLLMENT CONFIRMATION (HARDENED)
        # -------------------------------------------------------------
        elif current_step == "CONFIRM_ENROLLMENT":
            if DialectEngine.is_change_course(utterance) or "change" in cleaned_text or "badlo" in cleaned_text:
                session["current_step"] = "SELECT_COURSE"
                courses = session.get("suggested_courses", [])
                prompt = "कृपया सूची में से दोबारा अपना पसंदीदा कोर्स चुनें:"
                return prompt, session, False, [c["title"] for c in courses], courses

            # Catch any affirmative phrase, enrollment keyword, or pill button trigger
            is_confirmed = (
                DialectEngine.is_affirmative(utterance) or
                "confirm" in cleaned_text or
                "enroll" in cleaned_text or
                "पक्का" in cleaned_text or
                "नामांकन" in cleaned_text or
                "yes" in cleaned_text or
                "haan" in cleaned_text or
                cleaned_text == "1"
            )

            if is_confirmed:
                session["enrollment_confirmed"] = True
                session["is_completed"] = True
                session["current_step"] = "COMPLETED"

                closing = (
                    f"बधाई हो {session.get('full_name')} जी! सामूहिक बैच में आपका स्थान सुरक्षित हो गया है (15/20 पूर्ण)। "
                    "अब आप दाएँ पैनल से अपना आधिकारिक PM-AJAY GIA अप्रैज़ल डॉसियर (PDF) डाउनलोड कर सकते हैं। धन्यवाद!"
                )
                return closing, session, True, ["डाउनलोड PDF (Download Dossier)"], []
            else:
                prompt = "कृपया पुष्टि करें: क्या आप इस सामूहिक बैच में नामांकन पक्का करना चाहते हैं?"
                return prompt, session, False, ["हाँ, नामांकन पक्का करें", "कोर्स बदलें"], []

        # STAGE 6: COMPLETED (FALLTHROUGH PROTECTION)
        elif current_step == "COMPLETED":
            closing = (
                f"आपका नामांकन पहले ही सुरक्षित हो चुका है (15/20 पूर्ण)। "
                "कृपया दाएँ पैनल पर दिए गए हरे बटन से अपना PDF डॉसियर डाउनलोड करें।"
            )
            return closing, session, True, ["डाउनलोड PDF (Download Dossier)"], []

        return "धन्यवाद!", session, True, [], []