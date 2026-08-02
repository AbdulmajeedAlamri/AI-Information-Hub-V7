from __future__ import annotations

import logging
import streamlit as st

from assets.styles import apply_styles
from components.sidebar import render_sidebar
from database.db import initialise_database
from services.auth_service import is_auth_configured, render_login_screen, sync_current_user
from services.supabase_service import is_supabase_configured
from utils.i18n import current_language, t
from utils.state import initialise_state
from views.account import render_account
from views.ai_chat import render_ai_chat
from views.compare import render_compare
from views.dashboard import render_dashboard
from views.entities import render_entities
from views.home import render_home
from views.news import render_news
from views.people import render_people
from views.settings import render_settings

logging.basicConfig(level=logging.INFO,format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger=logging.getLogger("ai_information_hub")

st.set_page_config(page_title="Aurora Intelligence V11",page_icon="✦",layout="wide",initial_sidebar_state="expanded",menu_items={"Get help":None,"Report a bug":None,"About":"Aurora Intelligence V11 — Intelligence Workspace."})
initialise_state(); apply_styles(st.session_state.theme,current_language())

if not is_auth_configured():
    st.error("إعدادات تسجيل الدخول غير متاحة على الخادم. تحقق من secrets.toml في Render."); st.stop()
if not getattr(st.user,"is_logged_in",False): render_login_screen(); st.stop()
if not is_supabase_configured(): st.error("إعدادات Supabase غير موجودة. راجع قسم [supabase] في secrets.toml."); st.stop()
try: sync_current_user()
except Exception as exc: logger.exception("User sync failed"); st.error("تعذر تهيئة حسابك السحابي مؤقتًا. حدّث الصفحة أو حاول بعد قليل."); st.stop()
try: initialise_database()
except Exception as exc: logger.exception("Database initialization failed"); st.error("تعذر تهيئة مساحة البيانات مؤقتًا."); st.stop()
render_sidebar()
routes={"home":render_home,"dashboard":render_dashboard,"news":render_news,"people":render_people,"compare":render_compare,"entities":render_entities,"ai_chat":render_ai_chat,"account":render_account,"settings":render_settings}
try: routes.get(st.session_state.page,render_home)()
except Exception:
    logger.exception("Page rendering failed: %s",st.session_state.page)
    st.error(t("تعذر تحميل هذه الصفحة مؤقتًا. جرّب تحديث الصفحة أو العودة للرئيسية."))
    if st.button(t("العودة إلى الرئيسية"),type="primary"):
        st.session_state.page="home"; st.query_params["page"]="home"; st.rerun()
st.markdown('<div class="app-footer">Aurora Intelligence V11 · Intelligence Workspace</div>',unsafe_allow_html=True)
