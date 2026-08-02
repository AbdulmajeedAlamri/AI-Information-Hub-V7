from pathlib import Path

APP_NAME = "AI Information Hub V10"
APP_TAGLINE = "منصة عربية ذكية للأخبار والشخصيات والكيانات والتحليل"

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "database" / "hub.db"

OLLAMA_MODEL = "qwen2.5:3b"
MAX_ARTICLE_CHARS = 14000
MAX_CHAT_MESSAGES = 10
HTTP_TIMEOUT = 12
HTTP_RETRIES = 2
CACHE_TTL_SECONDS = 3600

COUNTRIES = {
    "السعودية": ("SA", "SA:ar"),
    "الإمارات": ("AE", "AE:ar"),
    "مصر": ("EG", "EG:ar"),
    "الولايات المتحدة": ("US", "US:en"),
    "المملكة المتحدة": ("GB", "GB:en"),
    "فرنسا": ("FR", "FR:fr"),
    "ألمانيا": ("DE", "DE:de"),
    "الهند": ("IN", "IN:en"),
    "اليابان": ("JP", "JP:ja"),
}

CATEGORIES = {
    "بحث مخصص": {"ar": "", "en": ""},
    "🔥 عاجل": {"ar": "أخبار عاجلة", "en": "breaking news"},
    "📈 رائج": {"ar": "الأخبار الرائجة", "en": "trending news"},
    "🤖 الذكاء الاصطناعي": {"ar": "الذكاء الاصطناعي", "en": "artificial intelligence"},
    "💻 التقنية": {"ar": "أخبار التقنية", "en": "technology news"},
    "💰 الاقتصاد": {"ar": "الاقتصاد والأسواق", "en": "economy markets"},
    "⚽ الرياضة": {"ar": "أخبار الرياضة", "en": "sports news"},
    "🏥 الصحة": {"ar": "أخبار الصحة", "en": "health news"},
    "🌍 العالم": {"ar": "الأخبار العالمية", "en": "world news"},
    "🛰️ العلوم": {"ar": "العلوم والفضاء", "en": "science space"},
}
