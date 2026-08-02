from __future__ import annotations

import streamlit as st

from components.common import page_header
from services.person_service import search_person
from utils.i18n import current_language, direction, tr
from utils.storage import add_history, toggle_favorite
from utils.text import safe_plain


def _tags(values: list[str], empty: str) -> str:
    if not values:
        return safe_plain(empty)
    return '<div class="meta">' + ''.join(f'<span>{safe_plain(value)}</span>' for value in values[:10]) + '</div>'


def render_people() -> None:
    ui_language = current_language()
    page_header(
        tr("👤 معلومات الشخصيات", "👤 People Intelligence", ui_language),
        tr(
            "الإنجازات، الشركات، المناصب، الشبكات الاجتماعية، الجوائز، التعليم، وروابط المصادر.",
            "Achievements, companies, roles, social profiles, awards, education, and source links.",
            ui_language,
        ),
    )

    result_language = st.selectbox(
        tr("لغة المعلومات", "Information language", ui_language),
        ["ar", "en"],
        format_func=lambda value: tr("العربية", "Arabic", ui_language) if value == "ar" else tr("الإنجليزية", "English", ui_language),
    )
    name = st.text_input(tr("اسم الشخصية", "Person name", ui_language), placeholder=tr("مثال: إيلون ماسك", "Example: Elon Musk", ui_language))

    if st.button(tr("🔎 البحث", "🔎 Search", ui_language), type="primary", use_container_width=True):
        if not name.strip():
            st.warning(tr("اكتب اسم الشخصية أولًا.", "Enter a person name first.", ui_language))
        else:
            with st.spinner(tr("جارٍ جمع المعلومات...", "Collecting information...", ui_language)):
                st.session_state.person_result = search_person(name, result_language)
                st.session_state.person_result_language = result_language
                add_history("person", name)

    data = st.session_state.get("person_result")
    if not data:
        st.info(tr("اكتب اسم شخصية عامة.", "Enter the name of a public figure.", ui_language))
        return
    if not data.get("found"):
        st.warning(data.get("message", tr("لم يتم العثور على معلومات.", "No information was found.", ui_language)))
        return

    if st.button(tr("⭐ حفظ في المفضلة", "⭐ Save to favorites", ui_language)):
        toggle_favorite({"id": data.get("id"), "title": data.get("full_name"), "type": "person", "image_url": data.get("image_url")})

    result_language = st.session_state.get("person_result_language", result_language)
    result_direction = direction(result_language)
    unavailable = tr("غير متوفر", "Not available", result_language)
    image_column, info_column = st.columns([0.9, 2.1], gap="large")
    with image_column:
        if data.get("image_url"):
            st.image(data["image_url"], use_container_width=True)
    with info_column:
        st.markdown(
            f'<div class="profile-card glass {result_direction}"><h2>👤 {safe_plain(data.get("full_name"))}</h2><p class="muted">{safe_plain(data.get("description"))}</p></div>',
            unsafe_allow_html=True,
        )
        age = data.get("age")
        rows = [
            (tr("🎂 تاريخ الميلاد", "🎂 Birth date", result_language), data.get("birth_date") or unavailable),
            (tr("⏳ العمر", "⏳ Age", result_language), (f"{age} سنة" if result_language == "ar" else f"{age} years") if age is not None else unavailable),
            (tr("💼 المهنة", "💼 Occupation", result_language), _tags(data.get("occupations", []), unavailable)),
            (tr("🏛️ المناصب", "🏛️ Positions", result_language), _tags(data.get("positions", []), unavailable)),
            (tr("🌍 الجنسية", "🌍 Citizenship", result_language), _tags(data.get("citizenships", []), unavailable)),
            (tr("📍 مكان الميلاد", "📍 Birthplace", result_language), _tags(data.get("birthplaces", []), unavailable)),
            (tr("🏢 جهات العمل", "🏢 Employers", result_language), _tags(data.get("employers", []), unavailable)),
            (tr("🎓 التعليم", "🎓 Education", result_language), _tags(data.get("education", []), unavailable)),
            (tr("🏆 الجوائز", "🏆 Awards", result_language), _tags(data.get("awards", []), unavailable)),
            (tr("🏭 الشركات", "🏭 Companies", result_language), _tags(data.get("companies", []), unavailable)),
        ]
        for label, value in rows:
            st.markdown(f'<div class="analysis-card glass {result_direction}"><h3>{label}</h3><div>{value}</div></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="analysis-card glass {result_direction}"><h3>{tr("📖 معلومات عامة","📖 Overview",result_language)}</h3><p>{safe_plain(data.get("summary"))}</p></div>', unsafe_allow_html=True)
    st.markdown(f"### 🕒 {tr('الخط الزمني','Timeline',ui_language)}")
    if data.get("timeline"):
        for item in data["timeline"]:
            st.markdown(f'<div class="timeline-card glass {result_direction}"><div class="timeline-item"><strong>{safe_plain(item.get("date"))}</strong><div>{safe_plain(item.get("event"))}</div></div></div>', unsafe_allow_html=True)
    else:
        st.info(tr("لا تتوفر أحداث زمنية كافية.", "No sufficient timeline events are available.", ui_language))

    st.markdown(f"### 🌐 {tr('الشبكات والروابط','Profiles and links',ui_language)}")
    links = []
    for website in data.get("websites", []): links.append((tr("الموقع الرسمي", "Official website", ui_language), website))
    for username in data.get("twitter", []): links.append(("X / Twitter", f"https://x.com/{username}"))
    for username in data.get("instagram", []): links.append(("Instagram", f"https://instagram.com/{username}"))
    for username in data.get("facebook", []): links.append(("Facebook", f"https://facebook.com/{username}"))
    if data.get("page_url"): links.append(("Wikipedia", data["page_url"]))
    if links:
        for label, url in links: st.link_button(label, url, use_container_width=True)
    else:
        st.info(tr("لا تتوفر روابط رسمية.", "No official links are available.", ui_language))
