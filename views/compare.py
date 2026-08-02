from __future__ import annotations

import streamlit as st

from components.common import page_header
from services.entity_service import search_entity
from services.person_service import search_person
from utils.i18n import current_language, direction, tr
from utils.storage import add_history
from utils.text import safe_plain


def _person_card(data: dict, language: str) -> None:
    if not data.get("found"):
        st.warning(data.get("message", tr("تعذر جلب البيانات.", "Unable to retrieve data.", language)))
        return
    if data.get("image_url"): st.image(data["image_url"], use_container_width=True)
    unavailable = tr("غير متوفر", "Not available", language)
    fields = {
        tr("العمر", "Age", language): data.get("age") or unavailable,
        tr("المهنة", "Occupation", language): ", ".join(data.get("occupations", [])[:5]) or unavailable,
        tr("المناصب", "Positions", language): ", ".join(data.get("positions", [])[:5]) or unavailable,
        tr("التعليم", "Education", language): ", ".join(data.get("education", [])[:5]) or unavailable,
        tr("الجوائز", "Awards", language): ", ".join(data.get("awards", [])[:5]) or unavailable,
    }
    details = "".join(f"<p><strong>{safe_plain(label)}:</strong> {safe_plain(value)}</p>" for label, value in fields.items())
    st.markdown(f'<div class="entity-card glass {direction(language)}"><h2>{safe_plain(data.get("full_name"))}</h2><p>{safe_plain(data.get("description"))}</p>{details}</div>', unsafe_allow_html=True)


def _entity_card(data: dict, language: str) -> None:
    if not data.get("found"):
        st.warning(data.get("message", tr("تعذر جلب البيانات.", "Unable to retrieve data.", language)))
        return
    if data.get("image_url"): st.image(data["image_url"], use_container_width=True)
    st.markdown(f'<div class="entity-card glass {direction(language)}"><h2>{safe_plain(data.get("title"))}</h2><p>{safe_plain(data.get("summary"))}</p></div>', unsafe_allow_html=True)
    if data.get("page_url"): st.link_button(tr("فتح المصدر", "Open source", language), data["page_url"], use_container_width=True)


def render_compare() -> None:
    language = current_language()
    page_header(
        tr("⚖️ مركز المقارنات", "⚖️ Comparison Center", language),
        tr("قارن شخصيتين أو شركتين أو دولتين دون أن يتوقف الموقع عند ضغط المصادر.", "Compare two people, companies, or countries with resilient source handling.", language),
    )
    mode = st.radio(
        tr("نوع المقارنة", "Comparison type", language),
        ["people", "companies", "countries"], horizontal=True, key="compare_mode_widget",
        format_func=lambda value: {"people":tr("شخصيتان","People",language),"companies":tr("شركتان","Companies",language),"countries":tr("دولتان","Countries",language)}[value],
    )
    left_name = st.text_input(tr("الطرف الأول", "First side", language), key="compare_left_input")
    right_name = st.text_input(tr("الطرف الثاني", "Second side", language), key="compare_right_input")
    if st.button(tr("تنفيذ المقارنة", "Run comparison", language), type="primary", use_container_width=True, key="compare_submit_button"):
        if not left_name.strip() or not right_name.strip():
            st.warning(tr("اكتب اسم الطرفين أولًا.", "Enter both names first.", language))
        else:
            with st.spinner(tr("جارٍ جمع معلومات المقارنة...", "Collecting comparison data...", language)):
                if mode == "people":
                    left, right = search_person(left_name.strip(), language), search_person(right_name.strip(), language)
                else:
                    left, right = search_entity(left_name.strip(), language), search_entity(right_name.strip(), language)
                st.session_state["compare_left_result"] = left
                st.session_state["compare_right_result"] = right
                st.session_state["compare_result_mode"] = mode
                add_history("compare", f"{left_name} vs {right_name}")
    left, right = st.session_state.get("compare_left_result"), st.session_state.get("compare_right_result")
    result_mode = st.session_state.get("compare_result_mode")
    if not left or not right:
        st.info(tr("اكتب الطرفين ثم اضغط تنفيذ المقارنة.", "Enter both sides, then run the comparison.", language))
        return
    st.markdown(f"### {tr('نتيجة المقارنة','Comparison result',language)}")
    columns = st.columns(2, gap="large")
    with columns[0]: _person_card(left, language) if result_mode == "people" else _entity_card(left, language)
    with columns[1]: _person_card(right, language) if result_mode == "people" else _entity_card(right, language)
    if st.button(tr("مسح نتيجة المقارنة", "Clear comparison", language), use_container_width=True):
        for key in ("compare_left_result","compare_right_result","compare_result_mode"): st.session_state.pop(key, None)
        st.rerun()
