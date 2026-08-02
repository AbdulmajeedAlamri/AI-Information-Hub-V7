from __future__ import annotations

import requests
import streamlit as st


@st.cache_data(ttl=300, show_spinner=False)
def check_ollama() -> tuple[bool, str]:
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=3)
        response.raise_for_status()
        return True, "Ollama متصل"
    except requests.RequestException:
        return False, "Ollama غير متصل أو غير متاح على الخادم"


@st.cache_data(ttl=300, show_spinner=False)
def check_wikipedia() -> tuple[bool, str]:
    try:
        response = requests.get(
            "https://www.wikipedia.org/",
            timeout=5,
            headers={"User-Agent": "AI-Information-Hub/6.0"},
        )
        response.raise_for_status()
        return True, "Wikipedia متاحة"
    except requests.RequestException:
        return False, "Wikipedia غير متاحة مؤقتًا"
