from __future__ import annotations

import streamlit as st

from services.auth_service import current_identity, logout
from utils.i18n import current_language, t
from utils.navigation import go_to
from utils.text import safe_plain


def render_sidebar() -> None:
    language = current_language()
    identity = current_identity()
    with st.sidebar:
        st.markdown(
            '<div class="sidebar-brand"><div class="brand-row"><div class="brand-mark">A</div><div><h3>Aurora Intelligence</h3><p>AI INFORMATION HUB · V11</p></div></div></div>',
            unsafe_allow_html=True,
        )
        if identity.get("picture"):
            st.image(identity["picture"], width=54)
        display_name = identity.get("name") or ("مستخدم" if language == "ar" else "User")
        st.markdown(
            f'<div class="user-shell"><strong>{safe_plain(display_name)}</strong><span class="user-email muted" title="{safe_plain(identity.get("email", ""))}">{safe_plain(identity.get("email", ""))}</span><small><span class="online-dot"></span> {t("الحساب متصل بالسحابة")}</small></div>',
            unsafe_allow_html=True,
        )
        items = {
            f"⌂  {t('الرئيسية')}": "home", f"▦  {t('لوحة التحكم')}": "dashboard",
            f"◉  {t('الأخبار')}": "news", f"♙  {t('الشخصيات')}": "people",
            f"⇄  {t('المقارنات')}": "compare", f"◇  {t('الكيانات')}": "entities",
            f"✦  {t('المساعد الذكي')}": "ai_chat", f"☆  {t('حسابي')}": "account",
            f"⚙  {t('الإعدادات')}": "settings",
        }
        current = next((label for label, value in items.items() if value == st.session_state.page), next(iter(items)))
        selected = st.radio("Navigation", list(items), index=list(items).index(current), label_visibility="collapsed")
        if items[selected] != st.session_state.page:
            go_to(items[selected])
        st.divider()
        if st.button(f"↪ {t('تسجيل الخروج')}", use_container_width=True):
            logout()
        st.caption("AURORA V11 · Google · Supabase")
