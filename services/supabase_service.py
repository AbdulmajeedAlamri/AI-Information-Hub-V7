from __future__ import annotations

import streamlit as st
from supabase import Client, create_client


class SupabaseConfigurationError(RuntimeError):
    pass


def is_supabase_configured() -> bool:
    try:
        section = st.secrets["supabase"]
        return bool(section.get("url") and section.get("secret_key"))
    except (KeyError, FileNotFoundError):
        return False


@st.cache_resource(show_spinner=False)
def get_admin_client() -> Client:
    if not is_supabase_configured():
        raise SupabaseConfigurationError(
            "إعدادات Supabase غير موجودة في .streamlit/secrets.toml"
        )

    return create_client(
        st.secrets["supabase"]["url"],
        st.secrets["supabase"]["secret_key"],
    )
