from __future__ import annotations

import streamlit as st

from components.common import page_header
from services.entity_service import get_entity_profile
from utils.i18n import current_language, direction, tr
from utils.storage import add_history
from utils.text import safe_plain, safe_text


def render_entities() -> None:
    ui_language = current_language()
    ui_direction = direction(ui_language)
    page_header(
        tr("🏢 تحليل الكيانات", "🏢 Entity Analysis", ui_language),
        tr("تحليل شركة أو دولة أو حدث اعتمادًا على مصادر عامة.", "Analyze a company, country, or event using public sources.", ui_language),
    )

    entity_type = st.selectbox(
        tr("نوع الكيان", "Entity type", ui_language),
        ["company", "country", "event"],
        format_func=lambda value: {
            "company": tr("شركة", "Company", ui_language),
            "country": tr("دولة", "Country", ui_language),
            "event": tr("حدث", "Event", ui_language),
        }[value],
    )
    result_language = st.selectbox(
        tr("لغة النتيجة", "Result language", ui_language),
        ["ar", "en"],
        format_func=lambda value: tr("العربية", "Arabic", ui_language) if value == "ar" else tr("الإنجليزية", "English", ui_language),
    )
    entity_name = st.text_input(
        tr(f"اسم { {'company':'الشركة','country':'الدولة','event':'الحدث'}[entity_type] }", f"{entity_type.title()} name", ui_language)
    )

    if st.button(tr("🔎 البحث والتحليل", "🔎 Search and analyze", ui_language), type="primary", use_container_width=True):
        if len(entity_name.strip()) < 2:
            st.warning(tr("اكتب اسم شركة أو دولة أو حدث بشكل واضح.", "Enter a clear company, country, or event name.", ui_language))
        else:
            with st.spinner(tr("جارٍ جمع المعلومات وتحليلها...", "Collecting and analyzing information...", ui_language)):
                data = get_entity_profile(entity_name.strip(), result_language)
                st.session_state.entity_result = data
                st.session_state.entity_result_language = result_language
                add_history("entity", entity_name.strip())

    data = st.session_state.get("entity_result")
    if not data:
        st.info(tr("اكتب اسم شركة أو دولة أو حدث.", "Enter a company, country, or event name.", ui_language))
        return
    if not data.get("found"):
        st.warning(data.get("message", tr("لم يتم العثور على معلومات واضحة.", "No clear information was found.", ui_language)))
        return

    result_language = st.session_state.get("entity_result_language", result_language)
    result_direction = "rtl" if result_language == "ar" else "ltr"
    st.markdown(
        f'<div class="entity-card glass {result_direction}"><h2>{safe_plain(data.get("title") or entity_name)}</h2><p>{safe_text(data.get("summary"), result_language)}</p></div>',
        unsafe_allow_html=True,
    )
    details = data.get("details") or {}
    if details:
        columns = st.columns(2)
        for index, (key, value) in enumerate(details.items()):
            with columns[index % 2]:
                st.markdown(
                    f'<div class="analysis-card glass {result_direction}"><h3>{safe_plain(key)}</h3><p>{safe_text(value, result_language)}</p></div>',
                    unsafe_allow_html=True,
                )
    if data.get("page_url"):
        st.link_button(tr("المصدر", "Source", ui_language), data["page_url"], use_container_width=True)
