import re
import unicodedata
from typing import Dict, List

CANONICAL_INTENTS: Dict[str, List[str]] = {
    "AFFIRMATIVE": [
        # Devanagari (Hindi, Bundelkhandi, Nimadi)
        "हाँ", "हा", "हाँजी", "हाजी", "हऊ", "हौ", "हो", "सही", "सही है", "सई", "सई है",
        "ठीक", "ठीक है", "शुरू", "शुरू करो", "शुरू करें", "बिल्कुल", "जरूर", "चलेगा",
        "पक्का", "पक्का करें", "पक्को करो", "हा करो", "हाँ करो", "नामांकन", "पुष्टि",
        "हाँ नामांकन पक्का करें", "नामांकन पक्का करें",
        # Gurmukhi
        "ਹਾਂ", "ਹਾਂਜੀ", "ਆਹੋ", "ਠੀਕ", "ਠੀਕ ਹੈ", "ਸ਼ੁਰੂ", "ਪੱਕਾ",
        # Gujarati
        "હા", "હાજી", "બરાબર", "શરૂ", "પાકું",
        # Romanized / English
        "haan", "ha", "haa", "haanji", "haji", "hau", "haun", "ho", "sahi", "sahi hai",
        "sai", "sai hai", "theek", "theek hai", "thik", "thik hai", "yes", "yep", "yeah",
        "sure", "ok", "okay", "start", "shuru", "karo", "chalo", "bilkul", "pakka",
        "confirm", "enroll", "enrollment", "yes confirm enrollment", "proceed", "done", "pukka", "1"
    ],
    "NEGATIVE": [
        "नहीं", "ना", "नाहीं", "नाहि", "कोनी", "नथी", "रुकिए", "रुको", "बाद में", "मत करो",
        "ਬਾਅਦ ਵਿੱਚ", "ਨਹੀਂ", "ਨਾ", "નથી",
        "nahi", "nahin", "na", "no", "nope", "cancel", "stop", "change", "badlo", "dobara", "2"
    ],
    "CHANGE_COURSE": [
        "कोर्स बदलें", "बदलें", "दूसरा", "चेंज", "change", "change course", "another", "select again"
    ],
    "TRADE_BUSINESS": [
        "दुकान", "व्यवसाय", "व्यापार", "बिजनेस", "किराना", "स्टोर", "बिक्री", "मुनाफा", "सेल्स",
        "shop", "business", "store", "retail", "kirana", "dukan", "vyapar", "trade", "sales", "merchant"
    ],
    "TRADE_SOLAR": [
        "सोलर", "सौर", "सूरज", "धूप", "सोलर पैनल", "सोलर प्लेट", "सोलर पट्टी", "सूर्यमित्र",
        "solar", "panel", "suraj", "dhoop", "suryamitra", "plate", "patti", "solar plant", "pv", "sun"
    ],
    "TRADE_TAILORING": [
        "सिलाई", "दर्जी", "कपड़ा", "कपड़े", "कुर्ता", "सिलाई काम", "कटिंग",
        "silai", "darji", "kapda", "kapde", "kurta", "tailor", "stitching", "sewing", "cutting"
    ],
    "TRADE_ELECTRICAL": [
        "बिजली", "तार", "वायरिंग", "करंट", "इलेक्ट्रीशियन", "एमसीबी", "मोटर", "लाइन", "बत्ती",
        "bijli", "electric", "electrician", "wire", "taar", "karent", "light", "mcb", "wiring", "motor"
    ],
    "TRADE_AGRICULTURE": [
        "खेती", "किसान", "फसल", "जैविक", "खाद", "डेयरी", "पशुपालन",
        "kheti", "kisan", "fasal", "agriculture", "farming", "dairy", "compost", "jaivik"
    ]
}

STAGE_PROMPTS: Dict[str, Dict[str, str]] = {
    "GREETING": {
        "hindi": "नमस्ते! प्रधानमंत्री अनुसूचित जाति अभ्युदय योजना (PM-AJAY) आजीविका सहायक में आपका स्वागत है। क्या हम बातचीत शुरू करें?",
        "bundelkhandi": "राम-राम! PM-AJAY आजीविका साथी में आपको स्वागत है। का हम बातचीत शुरू करें?",
        "nimadi": "राम-राम जी! PM-AJAY आजीविका सहायक मां तमारो स्वागत छे। का बातचीत शुरू करिये?",
        "punjabi": "ਸਤਿ ਸ਼੍ਰੀ ਅਕਾਲ ਜੀ! PM-AJAY ਆਜੀਵਿਕਾ ਸਹਾਇਕ ਵਿੱਚ ਤੁਹਾਡਾ ਸੁਆਗਤ ਹੈ। ਕੀ ਅਸੀਂ ਗੱਲਬਾਤ ਸ਼ੁਰੂ ਕਰੀਏ?",
        "gujarati": "નમસ્તે! PM-AJAY આજીવિકા સહાયકમાં આપનું સ્વાગત છે. શું આપણે વાતચીત શરૂ કરીએ?"
    },
    "ASK_NAME": {
        "hindi": "कृपया अपना शुभ नाम बताएं?",
        "bundelkhandi": "आपको शुभ नांव का है?",
        "nimadi": "तमारो शुभ नाम काई छे?",
        "punjabi": "ਕਿਰਪਾ ਕਰਕੇ ਆਪਣਾ ਸ਼ੁਭ ਨਾਮ ਦੱਸੋ ਜੀ?",
        "gujarati": "કૃપા કરીને આપનું શુભ નામ જણાવો?"
    },
    "ASK_LOCATION": {
        "hindi": "आप किस गाँव और ब्लॉक में रहते हैं?",
        "bundelkhandi": "आप कौन गाँव और ब्लॉक में रहत हो?",
        "nimadi": "तमे कया गाँव अने ब्लॉक मां रहो छो?",
        "punjabi": "ਤੁਸੀਂ ਕਿਹੜੇ ਪਿੰਡ ਅਤੇ ਬਲਾਕ ਵਿੱਚ ਰਹਿੰਦੇ ਹੋ?",
        "gujarati": "તમે કયા ગામ અને બ્લોકમાં રહો છો?"
    },
    "ASK_EDUCATION": {
        "hindi": "आपकी पढ़ाई-लिखाई कहाँ तक हुई है? (नीचे से चुनें या बोलें)",
        "bundelkhandi": "पढ़ाई-लिखाई कहाँ तक भई है?",
        "nimadi": "भणाई-लिखाई क्यां तक थई छे?",
        "punjabi": "ਤੁਹਾਡੀ ਪੜ੍ਹਾਈ ਕਿੱਥੋਂ ਤੱਕ ਹੋਈ ਹੈ ਜੀ?",
        "gujarati": "તમે કેટલો અભ્યાਸ કર્યો છે?"
    },
    "ASK_WORK": {
        "hindi": "अभी आप क्या काम करते हैं और कौन-सा हुनर सीखना या आगे बढ़ाना चाहते हैं?",
        "bundelkhandi": "अभी का काम-धंधा करत हो और का हुनर सीखन चहत हो?",
        "nimadi": "अज-काल सु काम करो छो अने सु हुनर सीखवू छे?",
        "punjabi": "ਅੱਜ-ਕੱਲ੍ਹ ਕੀ ਕੰਮ ਕਰਦੇ ਹੋ ਅਤੇ ਕਿਹੜਾ ਹੁਨਰ ਸਿੱਖਣਾ ਚਾਹੁੰਦੇ ਹੋ?",
        "gujarati": "હાલમાં તમે શું કામ કરો છો અને કયું હુનર શીખવા માંગો છો?"
    },
    "CONFIRM_ENROLL": {
        "hindi": "क्या आप अपने गाँव के इस सामूहिक बैच में अपना नामांकन पक्का करना चाहते हैं?",
        "bundelkhandi": "का आप अपने गाँव के ई सामूहिक बैच में अपनो नाम पक्को करन चहत हो?",
        "nimadi": "का तमे तमारा गाँव ना आ सामूहिक बैच मां नामांकन पक्को करवा मांगो छो?",
        "punjabi": "ਕੀ ਤੁਸੀਂ ਆਪਣੇ ਪਿੰਡ ਦੇ ਇਸ ਸਮੂਹਿਕ ਬੈਚ ਵਿੱਚ ਆਪਣਾ ਦਾਖਲਾ ਪੱਕਾ ਕਰਨਾ ਚਾਹੁੰਦੇ ਹੋ?",
        "gujarati": "શું તમે તમારા ગામના આ સામૂહિક બેચમાં તમારું નામાંકન કન્ફર્મ કરવા માંગો છો?"
    }
}


class DialectEngine:
    @classmethod
    def normalize_string(cls, text: str) -> str:
        if not text:
            return ""
        normalized = unicodedata.normalize('NFKD', str(text))
        cleaned = re.sub(r'[^\w\s]', ' ', normalized)
        return ' '.join(cleaned.lower().split())

    @classmethod
    def is_affirmative(cls, text: str) -> bool:
        cleaned = cls.normalize_string(text)
        words = cleaned.split()
        for token in CANONICAL_INTENTS["AFFIRMATIVE"]:
            norm_token = cls.normalize_string(token)
            if norm_token in words or f" {norm_token} " in f" {cleaned} " or cleaned == norm_token or norm_token in cleaned:
                return True
        return False

    @classmethod
    def is_change_course(cls, text: str) -> bool:
        cleaned = cls.normalize_string(text)
        for token in CANONICAL_INTENTS["CHANGE_COURSE"]:
            if cls.normalize_string(token) in cleaned:
                return True
        return False

    @classmethod
    def is_negative(cls, text: str) -> bool:
        cleaned = cls.normalize_string(text)
        words = cleaned.split()
        for token in CANONICAL_INTENTS["NEGATIVE"]:
            norm_token = cls.normalize_string(token)
            if norm_token in words or f" {norm_token} " in f" {cleaned} ":
                return True
        return False

    @classmethod
    def extract_trade(cls, text: str) -> str:
        cleaned = cls.normalize_string(text)
        for token in CANONICAL_INTENTS["TRADE_BUSINESS"]:
            if cls.normalize_string(token) in cleaned:
                return "retail_business"
        for token in CANONICAL_INTENTS["TRADE_TAILORING"]:
            if cls.normalize_string(token) in cleaned:
                return "tailoring"
        for token in CANONICAL_INTENTS["TRADE_ELECTRICAL"]:
            if cls.normalize_string(token) in cleaned:
                return "electrician"
        for token in CANONICAL_INTENTS["TRADE_AGRICULTURE"]:
            if cls.normalize_string(token) in cleaned:
                return "agriculture"
        for token in CANONICAL_INTENTS["TRADE_SOLAR"]:
            if cls.normalize_string(token) in cleaned:
                return "solar_installer"
        return "retail_business"

    @classmethod
    def get_prompt(cls, stage: str, dialect: str = "hindi") -> str:
        prompts = STAGE_PROMPTS.get(stage, STAGE_PROMPTS["GREETING"])
        return prompts.get(dialect, prompts["hindi"])