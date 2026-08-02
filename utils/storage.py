from __future__ import annotations

from datetime import datetime
import streamlit as st

from database.db import add_favorite_db, add_history_db, get_favorites_db, remove_favorite_db


def add_history(kind: str, query: str) -> None:
    item = {
        "kind": kind,
        "query": query,
        "time": datetime.now().isoformat(timespec="seconds"),
    }
    st.session_state.history.insert(0, item)
    st.session_state.history = st.session_state.history[:100]
    add_history_db(kind, query)


def _load_favorites_once() -> None:
    if not st.session_state.get("cloud_favorites_loaded"):
        st.session_state.favorites = get_favorites_db()
        st.session_state.cloud_favorites_loaded = True


def toggle_favorite(item: dict) -> bool:
    _load_favorites_once()
    identity = str(item.get("id") or item.get("link") or item.get("title"))

    for index, saved in enumerate(st.session_state.favorites):
        saved_identity = str(saved.get("id") or saved.get("link") or saved.get("title"))
        if saved_identity == identity:
            st.session_state.favorites.pop(index)
            remove_favorite_db(identity)
            return False

    st.session_state.favorites.insert(0, item)
    st.session_state.favorites = st.session_state.favorites[:100]
    add_favorite_db(item)
    return True
