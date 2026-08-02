from __future__ import annotations

import streamlit as st


def go_to(page: str) -> None:
    st.session_state.page = page
    st.query_params["page"] = page
    st.rerun()
