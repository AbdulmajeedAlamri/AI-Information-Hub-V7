from __future__ import annotations

import streamlit as st

from components.common import home_hero
from database.db import dashboard_counts
from services.auth_service import current_identity
from utils.i18n import current_language, direction
from utils.navigation import go_to
from utils.text import safe_plain


def _section(title: str, subtitle: str) -> None:
    st.markdown(f'<div class="section-heading"><div><span class="section-dot"></span><h2>{safe_plain(title)}</h2></div><p>{safe_plain(subtitle)}</p></div>', unsafe_allow_html=True)


def render_home() -> None:
    language = current_language(); rtl = direction(language); identity = current_identity()
    home_hero()
    try:
        counts = dashboard_counts()
    except Exception:
        counts = {"history": 0, "favorites": 0, "chats": 0, "analyses": 0}

    if language == "ar":
        eyebrow = "موجز مساحة العمل"
        greeting = f"مرحبًا، {identity.get('name') or 'بك'}"
        intro = "لوحة قيادة مصممة لتضع البحث والتحليل والتقارير أمامك دون تشتيت."
        metrics = [("⌕", "عمليات البحث", counts.get("history", 0)), ("☆", "العناصر المحفوظة", counts.get("favorites", 0)), ("✦", "المحادثات", counts.get("chats", 0)), ("▤", "التحليلات", counts.get("analyses", 0))]
        quick_title, quick_sub = "ابدأ مهمة جديدة", "اختصارات إلى أكثر المسارات استخدامًا"
        quick = [("◉", "رصد الأخبار", "ابحث حسب الموضوع والدولة والتاريخ ثم حلّل وصدّر النتائج.", "news"), ("◇", "تحليل كيان", "أنشئ ملفًا مختصرًا لشركة أو دولة أو حدث.", "entities"), ("⇄", "مقارنة ذكية", "قارن بين شخصيات أو جهات أو دول في عرض واضح.", "compare")]
        all_title, all_sub, open_text = "منظومة القدرات", "كل أدوات البحث والمعرفة في مركز واحد", "فتح"
        cards = [("▦", "لوحة التحكم", "نبض النشاط، السجل، العناصر المحفوظة، وحالة النظام.", "dashboard"), ("◉", "الأخبار", "بحث زمني، تحليل، حفظ، وتصدير.", "news"), ("♙", "الشخصيات", "سير، مناصب، تعليم، وروابط موثقة.", "people"), ("⇄", "المقارنات", "مقارنات منظمة وسهلة القراءة.", "compare"), ("◇", "الكيانات", "شركات، دول، وأحداث من مصادر عامة.", "entities"), ("✦", "المساعد الذكي", "محادثات محفوظة داخل حسابك.", "ai_chat"), ("☆", "مركز الحساب", "المفضلة، السجل، والملف الشخصي.", "account"), ("⚙", "الإعدادات", "اللغة، المظهر، وجاهزية الخدمات.", "settings")]
    else:
        eyebrow = "Workspace briefing"; greeting = f"Welcome, {identity.get('name') or 'there'}"; intro = "A focused command center that keeps research, analysis, and reporting within reach."
        metrics = [("⌕", "Searches", counts.get("history", 0)), ("☆", "Saved items", counts.get("favorites", 0)), ("✦", "Conversations", counts.get("chats", 0)), ("▤", "Analyses", counts.get("analyses", 0))]
        quick_title, quick_sub = "Launch a workflow", "Jump into the tasks you use most"
        quick = [("◉", "Monitor news", "Search by topic, country, and date, then analyze and export.", "news"), ("◇", "Explore an entity", "Create a concise profile for a company, country, or event.", "entities"), ("⇄", "Build a comparison", "Compare people, organizations, or countries in a clear view.", "compare")]
        all_title, all_sub, open_text = "Capability system", "Research and intelligence tools in one command center", "Open"
        cards = [("▦", "Dashboard", "Activity pulse, history, saved work, and system status.", "dashboard"), ("◉", "News", "Time-based research, analysis, saving, and export.", "news"), ("♙", "People", "Biographies, roles, education, and verified links.", "people"), ("⇄", "Comparisons", "Structured and readable side-by-side analysis.", "compare"), ("◇", "Entities", "Companies, countries, and events from public sources.", "entities"), ("✦", "AI Assistant", "Conversations saved to your cloud account.", "ai_chat"), ("☆", "Account center", "Favorites, history, and profile.", "account"), ("⚙", "Settings", "Language, appearance, and service readiness.", "settings")]

    st.markdown(f'<div class="welcome-card glass {rtl}"><div><div class="eyebrow">{safe_plain(eyebrow)}</div><h2>{safe_plain(greeting)}</h2><p class="muted">{safe_plain(intro)}</p></div><div class="welcome-orb">✦</div></div>', unsafe_allow_html=True)
    cols = st.columns(4, gap="medium")
    for col, (icon, label, value) in zip(cols, metrics):
        with col:
            st.markdown(f'<div class="home-metric glass {rtl}"><div class="metric-icon">{icon}</div><div><strong>{value}</strong><span>{safe_plain(label)}</span></div></div>', unsafe_allow_html=True)

    _section(quick_title, quick_sub)
    cols = st.columns(3, gap="large")
    for col, (icon, title, desc, page) in zip(cols, quick):
        with col:
            st.markdown(f'<div class="quick-card glass {rtl}"><div class="quick-top"><div class="feature-icon">{icon}</div><span>AURORA FLOW</span></div><h3>{safe_plain(title)}</h3><p>{safe_plain(desc)}</p></div>', unsafe_allow_html=True)
            if st.button(f"{open_text} {title}", key=f"quick_{page}", type="primary", use_container_width=True):
                go_to(page)

    _section(all_title, all_sub)
    for start in range(0, len(cards), 4):
        cols = st.columns(4, gap="medium")
        for col, (icon, title, desc, page) in zip(cols, cards[start:start + 4]):
            with col:
                st.markdown(f'<div class="feature-card glass {rtl}"><div class="feature-card-top"><div class="feature-icon">{icon}</div><span>EXPLORE</span></div><h3>{safe_plain(title)}</h3><p>{safe_plain(desc)}</p></div>', unsafe_allow_html=True)
                if st.button(open_text, key=f"home_{page}", use_container_width=True):
                    go_to(page)
