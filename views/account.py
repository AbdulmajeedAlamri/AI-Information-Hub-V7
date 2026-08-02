from __future__ import annotations

import streamlit as st

from components.common import page_header
from database.db import (
    clear_history_db, delete_chat_session, get_favorites_db, get_history_db,
    list_chat_sessions, load_profile_db, load_user_settings, remove_favorite_db,
    save_profile_db, save_user_settings,
)
from services.auth_service import current_identity, logout
from utils.i18n import current_language, tr
from utils.text import safe_plain


def render_account() -> None:
    language = current_language()
    page_header(
        tr("⭐ مركز حسابي", "⭐ Account Center", language),
        tr("ملفك الشخصي ومفضلاتك وسجل بحثك ومحادثاتك وإعداداتك.", "Your profile, favorites, search history, conversations, and settings.", language),
    )
    profile = load_profile_db(); identity = current_identity()
    tabs = st.tabs([
        tr("👤 الملف الشخصي", "👤 Profile", language),
        tr("⭐ المفضلة", "⭐ Favorites", language),
        tr("🕘 سجل البحث", "🕘 Search history", language),
        tr("🤖 المحادثات", "🤖 Conversations", language),
        tr("⚙️ الإعدادات", "⚙️ Settings", language),
    ])

    with tabs[0]:
        columns = st.columns([1, 3])
        with columns[0]:
            image = profile.get("avatar_url") or identity.get("picture")
            if image: st.image(image, use_container_width=True)
        with columns[1]:
            st.markdown(f"### {safe_plain(profile.get('name') or identity.get('name'))}")
            st.caption(profile.get("email") or identity.get("email"))
            st.write(f"{tr('نوع الحساب','Account type',language)}: {profile.get('role', 'user')}")
            if profile.get("created_at"): st.caption(f"{tr('تاريخ إنشاء الحساب','Created at',language)}: {profile['created_at']}")
        name = st.text_input(tr("الاسم", "Name", language), value=profile.get("name", ""), key="cloud_profile_name")
        st.text_input(tr("البريد", "Email", language), value=profile.get("email", ""), disabled=True)
        bio = st.text_area(tr("نبذة", "Bio", language), value=profile.get("bio", ""), key="cloud_profile_bio")
        if st.button(tr("حفظ الملف", "Save profile", language), type="primary", use_container_width=True):
            save_profile_db({"name": name, "bio": bio})
            st.success(tr("تم حفظ بيانات الحساب.", "Profile saved.", language)); st.rerun()

    with tabs[1]:
        favorites = get_favorites_db()
        if favorites:
            for index, row in enumerate(favorites):
                item = row.get("payload") or {}; identity_key = str(row.get("item_key") or "")
                with st.container(border=True):
                    st.markdown(f"### {safe_plain(row.get('title') or item.get('title'))}")
                    st.caption(safe_plain(item.get("source") or row.get("item_type") or ""))
                    columns = st.columns([3, 1])
                    with columns[0]:
                        if item.get("link"): st.link_button(tr("فتح المصدر", "Open source", language), item["link"], use_container_width=True)
                    with columns[1]:
                        if st.button(tr("حذف", "Delete", language), key=f"delete_favorite_{index}_{identity_key}", use_container_width=True):
                            remove_favorite_db(identity_key); st.success(tr("تم حذف العنصر من المفضلة.", "Item removed from favorites.", language)); st.rerun()
        else: st.info(tr("لا توجد عناصر محفوظة.", "No saved items.", language))

    with tabs[2]:
        history = get_history_db(100)
        if history:
            st.dataframe(history, use_container_width=True, hide_index=True)
            if st.button(tr("مسح سجل البحث", "Clear search history", language), use_container_width=True):
                clear_history_db(); st.success(tr("تم مسح سجل البحث.", "Search history cleared.", language)); st.rerun()
        else: st.info(tr("سجل البحث فارغ.", "Search history is empty.", language))

    with tabs[3]:
        sessions = list_chat_sessions(100)
        if sessions:
            for session in sessions:
                with st.container(border=True):
                    columns = st.columns([4, 1])
                    with columns[0]:
                        st.markdown(f"### {safe_plain(session.get('title'))}"); st.caption(session.get("updated_at", ""))
                    with columns[1]:
                        if st.button(tr("حذف", "Delete", language), key=f"delete_chat_{session['id']}", use_container_width=True):
                            delete_chat_session(str(session["id"])); st.success(tr("تم حذف المحادثة.", "Conversation deleted.", language)); st.rerun()
        else: st.info(tr("لا توجد محادثات محفوظة.", "No saved conversations.", language))

    with tabs[4]:
        settings = load_user_settings()
        theme = st.radio(tr("المظهر", "Appearance", language), ["dark", "light"], horizontal=True,
                         format_func=lambda value: tr("داكن", "Dark", language) if value == "dark" else tr("فاتح", "Light", language),
                         index=0 if st.session_state.get("theme", settings.get("theme", "dark")) == "dark" else 1)
        selected_language = st.radio(tr("اللغة", "Language", language), ["ar", "en"], horizontal=True,
                                     format_func=lambda value: "العربية" if value == "ar" else "English",
                                     index=0 if st.session_state.get("language", settings.get("language", "ar")) == "ar" else 1)
        if st.button(tr("حفظ الإعدادات", "Save settings", language), type="primary", use_container_width=True):
            save_user_settings({"theme": theme, "language": selected_language, "preferences": settings.get("preferences", {})})
            st.session_state.theme = theme; st.session_state.language = selected_language
            st.success(tr("تم حفظ الإعدادات.", "Settings saved.", language)); st.rerun()
        st.divider()
        if st.button(tr("🚪 تسجيل الخروج", "🚪 Sign out", language), use_container_width=True): logout()
