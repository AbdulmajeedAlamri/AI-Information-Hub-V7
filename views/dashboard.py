from __future__ import annotations

import pandas as pd
import streamlit as st

from components.common import page_header
from database.db import dashboard_counts, get_history_db, list_chat_sessions
from services.auth_service import current_identity
from services.health_service import check_ollama, check_wikipedia
from utils.i18n import current_language, direction


def render_dashboard() -> None:
    lang=current_language(); rtl=direction(lang); identity=current_identity()
    if lang=="ar":
        title=f"◫ لوحة {identity.get('name') or 'التحكم'}"; subtitle="نبض نشاطك، عمليات البحث، العناصر المحفوظة وحالة مساحة العمل.";
        labels=[("⌕","إجمالي البحث","history"),("◉","أبحاث الأخبار","news"),("♙","أبحاث الشخصيات","people"),("☆","المفضلة","favorites"),("✦","المحادثات","chats"),("▤","التحليلات","analyses")]
        health_title="جاهزية مساحة العمل"; health_caption="الفحوصات الخارجية اختيارية لتبقى الصفحة سريعة."; check="تشغيل الفحص"; dist="توزيع عمليات البحث"; recent="آخر عمليات البحث"; chats="آخر المحادثات"; empty="لا توجد بيانات حتى الآن."
    else:
        title=f"◫ {identity.get('name') or 'Your'} dashboard"; subtitle="A pulse check for searches, saved work, conversations, and workspace readiness.";
        labels=[("⌕","Total searches","history"),("◉","News research","news"),("♙","People research","people"),("☆","Favorites","favorites"),("✦","Conversations","chats"),("▤","Analyses","analyses")]
        health_title="Workspace readiness"; health_caption="External checks are optional to keep this page fast."; check="Run checks"; dist="Search distribution"; recent="Recent searches"; chats="Recent conversations"; empty="No data yet."
    page_header(title,subtitle)
    try: counts=dashboard_counts()
    except Exception as exc:
        st.warning("تعذر تحميل بعض الإحصائيات مؤقتًا." if lang=="ar" else "Some metrics are temporarily unavailable."); counts={k:0 for k in ["history","news","people","favorites","chats","analyses"]}
    for start in range(0,len(labels),3):
        cols=st.columns(3,gap="medium")
        for col,(icon,label,key) in zip(cols,labels[start:start+3]):
            with col: st.markdown(f'<div class="stat-card glass {rtl}"><span class="muted">{icon} {label}</span><h2>{counts.get(key,0)}</h2></div>',unsafe_allow_html=True)
    st.markdown(f"### {health_title}"); st.caption(health_caption)
    if st.button(check,use_container_width=True):
        cols=st.columns(2)
        for col,checker in zip(cols,[check_ollama,check_wikipedia]):
            try: ok,message=checker()
            except Exception as exc: ok,message=False,str(exc)
            with col: st.success(message) if ok else st.warning(message)
    else:
        labels_ready=["● App live","● Supabase connected","● External checks on demand"] if lang=="en" else ["● التطبيق يعمل","● Supabase متصل","● الفحص الخارجي عند الطلب"]
        st.markdown('<div class="service-strip glass '+rtl+'">'+''.join(f'<span>{x}</span>' for x in labels_ready)+'</div>',unsafe_allow_html=True)
    try: history=get_history_db(100)
    except Exception: history=[]
    if history:
        frame=pd.DataFrame(history)
        if "search_type" in frame.columns: st.markdown(f"### {dist}"); st.bar_chart(frame["search_type"].value_counts())
        st.markdown(f"### {recent}"); visible=[c for c in ["search_type","query","created_at"] if c in frame.columns]; st.dataframe(frame[visible].head(20),use_container_width=True,hide_index=True)
    else: st.info(empty)
    st.markdown(f"### {chats}")
    try: sessions=list_chat_sessions(5)
    except Exception: sessions=[]
    if sessions: st.dataframe(pd.DataFrame(sessions),use_container_width=True,hide_index=True)
    else: st.info(empty)
