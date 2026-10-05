import math
from typing import Dict, Any, Tuple, List
from app.dialect_engine import DialectEngine

# Standard NSQF-aligned catalogue for MP region
COURSE_CATALOG = [
    {
        "id": "RET/Q0101",
        "trade_key": "retail_business",
        "title": "Micro-Enterprise Retailer & Store Management",
        "sector": "Retail Commerce",
        "nsqf_level": 4,
        "duration": "300 Hours",
        "track": "SETUP",
        "keywords": ["दुकान", "किराना", "retail", "shop", "business", "store", "व्यापार"]
    },
    {
        "id": "ELE/Q5901",
        "trade_key": "solar_installer",
        "title": "Solar PV Rooftop Installer & Technician",
        "sector": "Electrical & Green Energy",
        "nsqf_level": 4,
        "duration": "350 Hours",
        "track": "BOTH",
        "keywords": ["सोलर", "solar", "panel", "bijli", "electric", "wiring"]
    },
    {
        "id": "CON/Q0602",
        "trade_key": "electrician",
        "title": "Domestic Wiring & Maintenance Electrician",
        "sector": "Infrastructure & Electrical",
        "nsqf_level": 4,
        "duration": "320 Hours",
        "track": "BOTH",
        "keywords": ["बिजली", "wiring", "electrician", "line", "repair"]
    },
    {
        "id": "AMH/Q1947",
        "trade_key": "tailoring",
        "title": "Self-Employed Tailor & Garment Maker",
        "sector": "Apparel & Handicrafts",
        "nsqf_level": 3,
        "duration": "280 Hours",
        "track": "SETUP",
        "keywords": ["सिलाई", "कपड़ा", "tailor", "cutting", "stitching", "boutique"]
    },
    {
        "id": "AGR/Q1202",
        "trade_key": "agriculture",
        "title": "Organic Vermicompost Producer & Agro-Dealer",
        "sector": "Agriculture & Allied",
        "nsqf_level": 3,
        "duration": "200 Hours",
        "track": "SETUP",
        "keywords": ["खेती", "खाद", "vermicompost", "kisan", "agri", "organic"]
    }
]


def calculate_course_matches(session: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Computes a deterministic match score (0-100%) for all catalog courses
    based on candidate trade aspiration, education, occupation, and center radius.
    """
    user_trade = session.get("aspired_trade", "")
    user_occ = str(session.get("current_occupation", "")).lower()
    user_edu = session.get("nsqf_eligible_level", 4)
    user_intent = session.get("livelihood_intent", "SETUP")
    dist = session.get("center_dist", 3.2)

    scored_courses = []

    for c in COURSE_CATALOG:
        score = 0.0

        # Factor 1: Trade & Keyword Alignment (Max 45 pts)
        if c["trade_key"] == user_trade:
            score += 45.0
        elif any(kw in user_occ for kw in c["keywords"]):
            score += 35.0
        else:
            score += 15.0

        # Factor 2: Education vs NSQF Alignment (Max 25 pts)
        if user_edu >= c["nsqf_level"]:
            score += 25.0
        else:
            score += 18.0  # Supported via RPL entry waiver

        # Factor 3: Livelihood Track Model Match (Max 15 pts)
        if c["track"] == "BOTH" or c["track"] == user_intent:
            score += 15.0
        else:
            score += 8.0

        # Factor 4: Spatial Distance Score (Max 15 pts)
        if dist <= 5.0:
            score += 15.0
        elif dist <= 15.0:
            score += 10.0
        else:
            score += 4.0

        match_pct = min(98, int(score))

        scored_courses.append({
            "id": c["id"],
            "trade_key": c["trade_key"],
            "title": c["title"],
            "sector": c["sector"],
            "nsqf_level": c["nsqf_level"],
            "duration": c["duration"],
            "match_score": match_pct,
            "center": session.get("center", "Gram Panchayat Bhawan")
        })

    # Sort descending by match score
    scored_courses.sort(key=lambda x: x["match_score"], reverse=True)
    return scored_courses


class ConversationalOrchestrator:

    @staticmethod
    def advance_dialogue(
        session: Dict[str, Any],
        user_utterance: str,
        dialect: str = "hindi"
    ) -> Tuple[str, Dict[str, Any], bool, List[str], List[Dict[str, Any]]]:
        step = session.get("current_step", "GREETING")
        options: List[str] = []
        courses: List[Dict[str, Any]] = []
        is_finished = False

        # 0. GREETING
        if step == "GREETING":
            if DialectEngine.is_affirmative(user_utterance):
                session["current_step"] = "SLOT_1_NAME"
                prompt = "धन्यवाद! कृपया अपना पूरा नाम बताइए?"
                options = []
            elif DialectEngine.is_negative(user_utterance):
                prompt = "कोई बात नहीं। PM-AJAY नामांकन सहायता के लिए आप कभी भी पुनः संपर्क कर सकते हैं।"
                is_finished = True
            else:
                prompt = "नमस्ते! PM-AJAY आजीविका व कौशल मैपिंग पोर्टल में आपका स्वागत है। क्या हम पंजीकरण शुरू करें?"
                options = ["हाँ, शुरू करें", "नहीं, बाद में"]

        # SLOT 1: NAME
        elif step == "SLOT_1_NAME":
            clean_name = user_utterance.replace("मेरा नाम", "").replace("is", "").replace("naam", "").strip(" .:,")
            session["full_name"] = clean_name if len(clean_name) > 1 else "आवेदक"
            session["current_step"] = "SLOT_2_3_DISTRICT_BLOCK"
            prompt = f"नमस्ते {session['full_name']} जी! आप मध्य प्रदेश के किस जिले और तहसील/ब्लॉक से हैं?"
            options = ["Bhopal - Phanda", "Bhopal - Berasia", "Raisen - Mandideep"]

        # SLOTS 2 & 3: LOCATION & RADIUS GATE
        elif step == "SLOT_2_3_DISTRICT_BLOCK":
            text = user_utterance.lower()
            if "berasia" in text:
                session["district"], session["block"] = "Bhopal", "Berasia"
                session["lat"], session["lon"] = 23.6338, 77.4334
                session["center"] = "Janpad Skill Hub Berasia"
                session["center_dist"] = 4.2
            elif "mandideep" in text or "raisen" in text:
                session["district"], session["block"] = "Raisen", "Mandideep"
                session["lat"], session["lon"] = 23.0722, 77.5186
                session["center"] = "Gram Panchayat Bhawan Mandideep"
                session["center_dist"] = 6.8
            else:
                session["district"], session["block"] = "Bhopal", "Phanda"
                session["lat"], session["lon"] = 23.2599, 77.4126
                session["center"] = "Gram Panchayat Bhawan Ratanpur"
                session["center_dist"] = 3.2

            session["village"] = session["block"]
            session["radius_status"] = "GREEN" if session["center_dist"] <= 15.0 else "RED"

            session["current_step"] = "SLOT_4_SCHOOLING"
            prompt = (
                f"निकटतम केंद्र '{session['center']}' की दूरी {session['center_dist']} Km है "
                f"({'15 Km सीमा के भीतर - Green' if session['radius_status'] == 'GREEN' else '15 Km से बाहर - Red'})। "
                f"आपकी स्कूली शिक्षा (Schooling) कहाँ तक हुई है?"
            )
            options = ["12वीं पास", "10वीं पास", "8वीं पास", "5वीं पास", "कोई औपचारिक शिक्षा नहीं"]

        # SLOT 4: SCHOOLING -> NSQF DETERMINATION
        elif step == "SLOT_4_SCHOOLING":
            session["formal_education"] = user_utterance.strip()
            if "12" in user_utterance or "स्नातक" in user_utterance:
                session["nsqf_eligible_level"] = 4
            elif "10" in user_utterance:
                session["nsqf_eligible_level"] = 3
            else:
                session["nsqf_eligible_level"] = 2

            session["current_step"] = "SLOT_5_CURRENT_WORK"
            prompt = f"आपकी शिक्षा अनुसार आप NSQF Level {session['nsqf_eligible_level']} तक के पात्र हैं। आप वर्तमान में क्या काम (Current Work) करते हैं?"
            options = ["दुकान / रिटेल स्टोर", "खेती / किसानी", "सिलाई / कटिंग", "बिजली वायरिंग", "मजदूरी / अन्य"]

        # SLOT 5: CURRENT WORK -> SLOT 6: TRADE
        elif step == "SLOT_5_CURRENT_WORK":
            session["current_occupation"] = user_utterance.strip()
            session["current_step"] = "SLOT_6_DESIRE_TRADE"
            prompt = "आप किस क्षेत्र में आगे बढ़ना चाहते हैं (Desire Trade: Agri, Electrics, Dookandari)?"
            options = [
                "दुकानदारी व व्यापार (Dookandari)",
                "इलेक्ट्रिकल व सोलर (Electrics)",
                "सिलाई व गारमेंट (Tailoring)",
                "जैविक खेती व कम्पोस्ट (Agri)",
                "अन्य अनुपलब्ध कोर्स"
            ]

        # SLOT 6: TRADE SELECTION & DYNAMIC MATCH SCORING
        elif step == "SLOT_6_DESIRE_TRADE":
            if "अन्य" in user_utterance or "अनुपलब्ध" in user_utterance:
                prompt = "यह ट्रेड केंद्र पर उपलब्ध नहीं है। कृपया उपलब्ध सूची में से ट्रेड चुनें:"
                options = ["दुकानदारी व व्यापार", "इलेक्ट्रिकल व सोलर", "सिलाई व गारमेंट", "जैविक खेती व कम्पोस्ट"]
                return prompt, session, False, options, []

            trade_key = DialectEngine.extract_trade(user_utterance)
            session["aspired_trade"] = trade_key

            session["current_step"] = "SLOT_7_JOB_OR_SETUP"
            prompt = "आप प्रशिक्षण लेकर नौकरी करना चाहते हैं या स्वयं की दुकान/व्यवसाय (Job or Own Setup)?"
            options = ["स्वयं का व्यवसाय (Own Setup)", "नौकरी (Job Placement)", "दोनों विकल्प (Both Options)"]

        # SLOT 7: JOB / SETUP
        elif step == "SLOT_7_JOB_OR_SETUP":
            session["livelihood_intent"] = "SETUP" if "व्यवसाय" in user_utterance or "Setup" in user_utterance else "JOB"
            session["current_step"] = "SLOT_8_TIME_LIMIT"
            prompt = "प्रशिक्षण के लिए आप प्रतिदिन कितना समय दे सकते हैं (Time Limit)?"
            options = ["रोजाना 2-4 घंटे (Morning Batch)", "रोजाना 4-6 घंटे (Regular Batch)"]

        # SLOT 8: TIME LIMIT -> SLOT 9: SC STATUS
        elif step == "SLOT_8_TIME_LIMIT":
            session["availability_window"] = user_utterance.strip()
            session["current_step"] = "SLOT_9_SC_STATUS"
            prompt = "PM-AJAY 50% सरकारी अनुदान हेतु: क्या आप अनुसूचित जाति (SC Status) वर्ग से हैं?"
            options = ["हाँ, SC वर्ग से हूँ", "नहीं, अन्य वर्ग"]

        # SLOT 9: SC STATUS -> MULTI-COURSE RECOMMENDATION DISPLAY
        elif step == "SLOT_9_SC_STATUS":
            session["sc_status_verified"] = DialectEngine.is_affirmative(user_utterance) or "हाँ" in user_utterance
            session["oral_rpl_score"] = 0.95
            session["current_step"] = "SELECT_RECOMMENDED_COURSE"

            courses = calculate_course_matches(session)
            top_course = courses[0]
            session["selected_course"] = top_course

            prompt = (
                f"आपके कौशल प्रोफाइल, शिक्षा व स्थान के आधार पर शीर्ष कोर्स विकल्प तैयार हैं:\n"
                f"• सबसे उपयुक्त: '{top_course['title']}' (Match {top_course['match_score']}%)\n"
                f"दाहिनी ओर दिए गए विकल्पों में से अपना पसंदीदा कोर्स चुनें या पुष्टि करें।"
            )
            options = [f"चुनें: {c['title']} (Match {c['match_score']}%)" for c in courses[:3]]

        # COURSE SELECTION CONFIRMATION
        elif step in ["SELECT_RECOMMENDED_COURSE", "CONFIRM_ENROLLMENT"]:
            for c in COURSE_CATALOG:
                if c["id"] in user_utterance or c["title"] in user_utterance or c["trade_key"] in user_utterance:
                    session["selected_course"] = next((x for x in calculate_course_matches(session) if x["id"] == c["id"]), c)
                    break

            if DialectEngine.is_affirmative(user_utterance) or "पक्का" in user_utterance or "चुनें" in user_utterance:
                session["enrollment_confirmed"] = True
                session["current_step"] = "COMPLETED"
                is_finished = True
                prompt = (
                    f"बधाई हो! '{session['selected_course']['title']}' में आपका नामांकन 15/20 के सामूहिक बैच में दर्ज हो चुका है। "
                    "नीचे दिए गए बटन से अपना 1-पेज MoSJE Form-1 Appraisal Dossier PDF डाउनलोड करें।"
                )
                options = ["दस्तावेज़ डाउनलोड करें (PDF)"]
                courses = calculate_course_matches(session)
            else:
                courses = calculate_course_matches(session)
                prompt = "कृपया दिए गए विकल्पों में से अपना पसंदीदा कोर्स चुनें:"
                options = [f"चुनें: {c['title']} (Match {c['match_score']}%)" for c in courses[:3]]

        return prompt, session, is_finished, options, courses