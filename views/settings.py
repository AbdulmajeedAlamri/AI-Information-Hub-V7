from __future__ import annotations

import streamlit as st

from components.common import page_header
from services.health_service import check_ollama, check_wikipedia
from services.llm_service import cloud_ai_configured
from utils.i18n import current_language, tr


def _preference_selectors() -> None:
    language = current_language()
    left, right = st.columns(2)
    with left:
        selected_language = st.selectbox(
            tr("اللغة", "Language", language),
            options=["ar", "en"],
            format_func=lambda value: "العربية" if value == "ar" else "English",
            index=0 if language == "ar" else 1,
            key="settings_language_selector",
        )
    with right:
        selected_theme = st.selectbox(
            tr("المظهر", "Appearance", language),
            options=["dark", "light"],
            format_func=lambda value: tr("داكن", "Dark", language) if value == "dark" else tr("فاتح", "Light", language),
            index=0 if st.session_state.get("theme", "dark") == "dark" else 1,
            key="settings_theme_selector",
        )

    changed = False
    if selected_language != st.session_state.get("language"):
        st.session_state.language = selected_language
        changed = True
    if selected_theme != st.session_state.get("theme"):
        st.session_state.theme = selected_theme
        changed = True
    if changed:
        st.rerun()


def render_settings() -> None:
    language = current_language()
    page_header(
        tr("⚙️ الإعدادات والاستعداد للنشر", "⚙️ Settings and launch readiness", language),
        tr("المظهر، الخدمات، SEO، Analytics، والدومين.", "Appearance, services, SEO, analytics, and domain settings.", language),
    )
    _preference_selectors()
    language = current_language()

    st.caption(tr(
        "يتم تطبيق اللغة والمظهر مباشرة، وتظل الإعدادات محفوظة خلال جلستك الحالية.",
        "Language and appearance apply immediately and remain saved for the current session.",
        language,
    ))

    st.markdown(f"### {tr('فحص الخدمات','Service checks',language)}")
    if cloud_ai_configured():
        st.success(tr("مزود الذكاء الاصطناعي السحابي مُعدّ.", "Cloud AI provider is configured.", language))
    else:
        st.warning(tr("المساعد الذكي يحتاج قسم [ai] في Secret File على Render.", "AI chat needs an [ai] section in the Render Secret File.", language))

    if st.button(tr("تشغيل الفحص", "Run checks", language)):
        for checker in (check_ollama, check_wikipedia):
            ok, message = checker()
            st.success(message) if ok else st.warning(message)
    else:
        st.info(tr("الفحص اختياري لتجنب إبطاء الصفحة.", "Checks are optional to keep this page fast.", language))

    st.markdown("### SEO")
    seo_text = (
        "Title: AI Information Hub\n"
        "Description: منصة عربية لتحليل الأخبار والشخصيات والكيانات بالذكاء الاصطناعي.\n"
        "Keywords: أخبار، تحليل، ذكاء اصطناعي، شخصيات، شركات، دول."
        if language == "ar" else
        "Title: AI Information Hub\n"
        "Description: An intelligence workspace for news, people, entities, and AI-assisted analysis.\n"
        "Keywords: news, analysis, artificial intelligence, people, companies, countries."
    )
    st.code(seo_text)

    st.markdown("### Google Analytics")
    st.caption(tr(
        "سيتم ربط Measurement ID في الخطوة النهائية مع الدومين.",
        "The Measurement ID can be connected when the custom domain is ready.",
        language,
    ))

    st.markdown(f"### {tr('جاهزية المرحلة النهائية','Final-stage readiness',language)}")
    st.write(
        "- قاعدة البيانات تعمل على Supabase/PostgreSQL.\n- تسجيل الدخول عبر Google.\n- ربط الدومين وHTTPS.\n- Google Analytics وSearch Console.\n- استخدام مزود ذكاء اصطناعي سحابي للإنتاج بدل Ollama المحلي."
        if language == "ar" else
        "- Database on Supabase/PostgreSQL.\n- Google sign-in.\n- Custom domain and HTTPS.\n- Google Analytics and Search Console.\n- A cloud AI provider for production instead of local Ollama."
    )
