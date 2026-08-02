from __future__ import annotations

import streamlit as st


VALID_PAGES = {
    "home", "dashboard", "news", "people", "compare",
    "entities", "ai_chat", "account", "settings",
}


def initialise_state() -> None:
    requested_page = str(st.query_params.get("page", "home"))
    if requested_page not in VALID_PAGES:
        requested_page = "home"

    defaults = {
        "page": requested_page,
        "theme": "dark",
        "language": "ar",
        "favorites": [],
        "history": [],
        "profile": {"name": "", "email": "", "bio": ""},
        "news_results": [],
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # Keep refreshes and copied links on the same internal page.
    if st.session_state.page != requested_page and "page" in st.query_params:
        st.session_state.page = requested_page
