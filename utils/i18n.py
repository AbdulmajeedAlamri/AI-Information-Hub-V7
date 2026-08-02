from __future__ import annotations

import streamlit as st

_TRANSLATIONS = {
    "en": {
        "الرئيسية": "Home", "لوحة التحكم": "Dashboard", "الأخبار": "News",
        "الشخصيات": "People", "المقارنات": "Comparisons", "الكيانات": "Entities",
        "المساعد الذكي": "AI Assistant", "حسابي": "My Account", "الإعدادات": "Settings",
        "الحساب متصل بالسحابة": "Cloud account connected", "تسجيل الخروج": "Sign out",
        "الإعدادات والاستعداد للنشر": "Settings and launch readiness",
        "المظهر، الخدمات، SEO، Analytics، والدومين.": "Appearance, services, SEO, analytics, and domain settings.",
        "المظهر": "Appearance", "داكن": "Dark", "فاتح": "Light", "اللغة": "Language",
        "العربية": "Arabic", "الإنجليزية": "English", "فحص الخدمات": "Service checks",
        "جاهزية المرحلة النهائية": "Final-stage readiness",
        "العودة إلى الرئيسية": "Back to home",
        "تعذر تحميل هذه الصفحة مؤقتًا. جرّب تحديث الصفحة أو العودة للرئيسية.": "This page could not be loaded temporarily. Refresh or return home.",
    }
}

_COUNTRIES_EN = {
    "السعودية":"Saudi Arabia","الإمارات":"United Arab Emirates","مصر":"Egypt",
    "الولايات المتحدة":"United States","المملكة المتحدة":"United Kingdom",
    "فرنسا":"France","ألمانيا":"Germany","الهند":"India","اليابان":"Japan",
}
_CATEGORIES_EN = {
    "بحث مخصص":"Custom search","🔥 عاجل":"🔥 Breaking","📈 رائج":"📈 Trending",
    "🤖 الذكاء الاصطناعي":"🤖 Artificial intelligence","💻 التقنية":"💻 Technology",
    "💰 الاقتصاد":"💰 Economy","⚽ الرياضة":"⚽ Sports","🏥 الصحة":"🏥 Health",
    "🌍 العالم":"🌍 World","🛰️ العلوم":"🛰️ Science",
}

def current_language() -> str:
    value = str(st.session_state.get("language", "ar"))
    return value if value in {"ar", "en"} else "ar"

def tr(ar: str, en: str, language: str | None = None) -> str:
    return ar if (language or current_language()) == "ar" else en

def t(text: str, language: str | None = None) -> str:
    lang = language or current_language()
    return text if lang == "ar" else _TRANSLATIONS.get("en", {}).get(text, text)

def direction(language: str | None = None) -> str:
    return "rtl" if (language or current_language()) == "ar" else "ltr"

def country_label(value: str, language: str | None = None) -> str:
    return value if (language or current_language()) == "ar" else _COUNTRIES_EN.get(value, value)

def category_label(value: str, language: str | None = None) -> str:
    return value if (language or current_language()) == "ar" else _CATEGORIES_EN.get(value, value)
