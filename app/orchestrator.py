# app/orchestrator.py
import re
from typing import Dict, Any, Tuple, List

SLOT_FLOW = [
    "formal_education",
    "traditional_trade",
    "employment_type",
    "mobility_radius_km"
]

STEP_CONFIG = {
    "formal_education": {
        "hi": "नमस्ते! आपका PM-AJAY आजीविका सहायक में स्वागत है। कृपया बताएं कि आपकी पढ़ाई-लिखाई कहाँ तक हुई है?",
        "en": "Welcome to the PM-AJAY Livelihood Assistant. What is your highest educational qualification?",
        "options": [
            {
                "idx": "1",
                "label_hi": "अनपढ़ / स्कूल नहीं गए",
                "label_en": "No Formal Schooling",
                "value": "No Formal Education",
                "natural_matches": ["no schooling", "uneducated", "illiterate", "स्कूल नहीं", "अनपढ़", "बिना पढ़े", "none"]
            },
            {
                "idx": "2",
                "label_hi": "5वीं पास",
                "label_en": "5th Pass",
                "value": "5th Pass",
                "natural_matches": ["5th", "5वीं", "पांचवीं", "primary", "कक्षा 5", "class 5"]
            },
            {
                "idx": "3",
                "label_hi": "8वीं पास",
                "label_en": "8th Pass",
                "value": "8th Pass",
                "natural_matches": ["8th", "8वीं", "आठवीं", "middle", "कक्षा 8", "class 8"]
            },
            {
                "idx": "4",
                "label_hi": "10वीं पास",
                "label_en": "10th Pass",
                "value": "10th Pass",
                "natural_matches": ["10th", "10वीं", "दसवीं", "matric", "कक्षा 10", "class 10", "secondary"]
            },
            {
                "idx": "5",
                "label_hi": "12वीं पास",
                "label_en": "12th Pass",
                "value": "12th Pass",
                "natural_matches": ["12th", "12वीं", "बारहवीं", "inter", "कक्षा 12", "class 12", "higher secondary"]
            }
        ]
    },
    "traditional_trade": {
        "hi": "धन्यवाद। आपके परिवार में पारंपरिक रूप से क्या काम होता आया है, या अभी आप क्या काम करते हैं?",
        "en": "Thank you. What is your traditional family trade or your current livelihood activity?",
        "options": [
            {
                "idx": "1",
                "label_hi": "चमड़ा व जूता निर्माण",
                "label_en": "Leathercraft & Footwear",
                "value": "leather",
                "natural_matches": ["leather", "चमड़ा", "जूता", "चप्पल", "मोची", "footwear", "shoes"]
            },
            {
                "idx": "2",
                "label_hi": "सिलाई व परिधान",
                "label_en": "Tailoring & Garments",
                "value": "tailoring",
                "natural_matches": ["tailoring", "सिलाई", "दर्जी", "कपड़ा", "garment", "apparel", "sewing"]
            },
            {
                "idx": "3",
                "label_hi": "जैविक खाद व कृषि",
                "label_en": "Organic Agri & Compost",
                "value": "organic_fertilizer",
                "natural_matches": ["farming", "खाद", "वर्मीकंपोस्ट", "खेती", "कृषि", "organic", "compost"]
            },
            {
                "idx": "4",
                "label_hi": "भवन व राजमिस्त्री",
                "label_en": "Masonry & Construction",
                "value": "construction",
                "natural_matches": ["construction", "राजमिस्त्री", "मजदूरी", "मिस्त्री", "cement", "mason"]
            },
            {
                "idx": "5",
                "label_hi": "बिजली व सौर उपकरण",
                "label_en": "Electrical & Solar",
                "value": "electrical",
                "natural_matches": ["electrical", "बिजली", "वायरिंग", "सोलर", "electrician", "solar"]
            }
        ]
    },
    "employment_type": {
        "hi": "आप आगे खुद का व्यवसाय/दुकान शुरू करना चाहते हैं (पूंजीगत अनुदान सहित), या नियमित नौकरी करना चाहते हैं?",
        "en": "Would you prefer starting your own enterprise/shop (with capital subsidy) or regular wage employment?",
        "options": [
            {
                "idx": "1",
                "label_hi": "खुद का काम / उद्यम",
                "label_en": "Self-Employed Enterprise",
                "value": "SELF_EMPLOYED",
                "natural_matches": ["self", "enterprise", "खुद का", "दुकान", "व्यवसाय", "बिजनेस", "उद्यम", "own business"]
            },
            {
                "idx": "2",
                "label_hi": "मासिक नौकरी",
                "label_en": "Wage Employment / Job",
                "value": "WAGE_EMPLOYED",
                "natural_matches": ["wage", "job", "नौकरी", "कंपनी", "महीने", "salary", "कारखाना", "monthly"]
            }
        ]
    },
    "mobility_radius_km": {
        "hi": "प्रशिक्षण या रोजगार के लिए आप अपने गाँव/कस्बे से कितनी दूरी तक जा सकते हैं?",
        "en": "How far are you willing to travel from your village or town for training or work?",
        "options": [
            {
                "idx": "1",
                "label_hi": "गाँव के अंदर (5 किमी)",
                "label_en": "Within Village (Under 5 km)",
                "value": 5,
                "natural_matches": ["5", "5km", "5 किमी", "पास", "गाँव", "लोकल", "nearby"]
            },
            {
                "idx": "2",
                "label_hi": "15 किमी तक (ब्लॉक)",
                "label_en": "Within 15 km (Block Level)",
                "value": 15,
                "natural_matches": ["15", "15km", "15 किमी", "आसपास", "ब्लॉक"]
            },
            {
                "idx": "3",
                "label_hi": "35 किमी या शहर",
                "label_en": "Within 35 km (District City)",
                "value": 35,
                "natural_matches": ["35", "35km", "35 किमी", "शहर", "कहीं भी", "बाहर", "anywhere"]
            }
        ]
    }
}

class ConversationManager:
    @staticmethod
    def get_current_step(slots: Dict[str, Any]) -> str:
        for slot in SLOT_FLOW:
            if slots.get(slot) is None or slots.get(slot) == "":
                return slot
        return "COMPLETED"

    @classmethod
    def extract_slots(cls, text: str, current_slots: Dict[str, Any]) -> Dict[str, Any]:
        raw_text = text.strip()
        lowered = raw_text.lower()
        updated = dict(current_slots)
        active_step = cls.get_current_step(updated)

        if active_step not in STEP_CONFIG:
            return updated

        step_opts = STEP_CONFIG[active_step]["options"]

        # PRIORITY 1: Explicit Index Match ("1", "2", "3", etc.)
        for opt in step_opts:
            if raw_text == opt["idx"]:
                updated[active_step] = opt["value"]
                return updated

        # PRIORITY 2: Exact Value Match
        for opt in step_opts:
            if lowered == str(opt["value"]).lower():
                updated[active_step] = opt["value"]
                return updated

        # PRIORITY 3: Natural Language Matches for the Active Step
        for opt in step_opts:
            for phrase in opt["natural_matches"]:
                if re.search(rf"\b{re.escape(phrase)}\b", lowered, re.IGNORECASE):
                    updated[active_step] = opt["value"]
                    return updated

        # PRIORITY 4: Multi-Entity Global Fallback Scanning
        if not updated.get("formal_education"):
            if any(k in lowered for k in ["no schooling", "uneducated", "illiterate", "स्कूल नहीं", "अनपढ़"]):
                updated["formal_education"] = "No Formal Education"
            elif re.search(r"\b(5th|5वीं|पांचवीं)\b", lowered) or "class 5" in lowered:
                updated["formal_education"] = "5th Pass"
            elif re.search(r"\b(8th|8वीं|आठवीं)\b", lowered) or "class 8" in lowered:
                updated["formal_education"] = "8th Pass"
            elif re.search(r"\b(10th|10वीं|दसवीं|matric)\b", lowered) or "class 10" in lowered:
                updated["formal_education"] = "10th Pass"
            elif re.search(r"\b(12th|12वीं|बारहवीं|inter)\b", lowered) or "class 12" in lowered:
                updated["formal_education"] = "12th Pass"

        if not updated.get("traditional_trade"):
            trade_dictionary = {
                "leather": ["चमड़ा", "जूता", "चप्पल", "मोची", "leather", "footwear"],
                "tailoring": ["सिलाई", "दर्जी", "कपड़ा", "tailor", "sewing", "garment"],
                "organic_fertilizer": ["खाद", "वर्मीकंपोस्ट", "organic", "खेती", "compost"],
                "construction": ["राजमिस्त्री", "मजदूरी", "मिस्त्री", "cement", "mason"],
                "electrical": ["बिजली", "वायरिंग", "solar", "electric", "electrician"]
            }
            for trade, keywords in trade_dictionary.items():
                if any(k in lowered for k in keywords):
                    updated["traditional_trade"] = trade
                    break

        if not updated.get("employment_type"):
            if any(k in lowered for k in ["खुद का", "दुकान", "बिजनेस", "व्यवसाय", "self", "enterprise", "own business"]):
                updated["employment_type"] = "SELF_EMPLOYED"
            elif any(k in lowered for k in ["नौकरी", "कंपनी", "wage", "job", "महीने", "salary"]):
                updated["employment_type"] = "WAGE_EMPLOYED"

        if not updated.get("mobility_radius_km"):
            nums = re.findall(r"\b\d+\b", lowered)
            if any(k in lowered for k in ["km", "किमी", "किलोमीटर", "दूर", "miles"]) and nums:
                updated["mobility_radius_km"] = min(int(nums[0]), 100)

        return updated

    @classmethod
    def get_next_prompt(cls, slots: Dict[str, Any], lang: str = "hi") -> Tuple[str, str, List[Dict[str, Any]], bool]:
        step = cls.get_current_step(slots)
        if step != "COMPLETED":
            cfg = STEP_CONFIG[step]
            prompt = cfg.get(lang, cfg["en"])
            options = []
            for opt in cfg.get("options", []):
                options.append({
                    "idx": opt["idx"],
                    "label": opt.get(f"label_{lang}", opt["label_hi"]),
                    "value": opt["value"]
                })
            return step, prompt, options, False

        completion_msg = (
            "आपकी सभी जानकारियां दर्ज हो गई हैं। आपके पारंपरिक कौशल और NSQF मानकों के आधार पर PM-AJAY GIA पूंजीगत अनुदान और प्रशिक्षण केंद्रों की गणना पूरी हो गई है।"
            if lang == "hi" else
            "All your details have been recorded. NSQF-aligned livelihood pathways, training centers, and PM-AJAY GIA capital subsidies have been calculated."
        )
        return "COMPLETED", completion_msg, [], True