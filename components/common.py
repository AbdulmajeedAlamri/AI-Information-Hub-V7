from __future__ import annotations

import streamlit as st

from utils.i18n import current_language, direction, t
from utils.text import safe_plain, safe_text


def page_header(title: str, subtitle: str) -> None:
    language = current_language()
    label = "AURORA INTELLIGENCE OS · V11"
    st.markdown(
        f"""
        <header class="page-head glass {direction(language)}">
          <div class="page-kicker">{label}</div>
          <h1>{safe_plain(t(title, language))}</h1>
          <p>{safe_plain(t(subtitle, language))}</p>
        </header>
        """,
        unsafe_allow_html=True,
    )


def home_hero() -> None:
    language = current_language()
    if language == "ar":
        title = "مركز قيادة للمعلومة"
        subtitle = "ابحث، حلّل، قارن، ووثّق المعرفة في مساحة عمل واحدة مصممة لاتخاذ قرارات أسرع وأوضح."
        chips = ["بحث متعدد المصادر", "تحليل ثنائي اللغة", "تقارير جاهزة", "مزامنة سحابية"]
    else:
        title = "A command center for information"
        subtitle = "Research, analyze, compare, and document knowledge in one workspace built for clearer, faster decisions."
        chips = ["Multi-source research", "Bilingual intelligence", "Ready-to-share reports", "Cloud workspace"]
    pills = "".join(f'<span class="status-pill"><span class="online-dot"></span>{safe_plain(x)}</span>' for x in chips)
    st.markdown(
        f"""
        <section class="hero-v10 glass {direction(language)}">
          <div class="hero-grid">
            <div>
              <div class="hero-kicker">AI INFORMATION HUB · AURORA V11</div>
              <h1>{safe_plain(title)}</h1>
              <p>{safe_plain(subtitle)}</p>
              <div class="status-row">{pills}</div>
            </div>
            <div class="hero-visual">
              <div class="visual-label">LIVE INTELLIGENCE MAP</div>
              <div class="orbit"></div><div class="orb a"></div><div class="orb b"></div>
            </div>
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_analysis(analysis: dict, language: str) -> None:
    text_direction = "rtl" if language == "ar" else "ltr"

    headline_label = "عنوان الخبر" if language == "ar" else "News Title"
    summary_label = "ملخص الخبر" if language == "ar" else "News Summary"
    points_label = "أهم النقاط" if language == "ar" else "Key Points"

    headline = analysis.get("headline", "")
    if str(headline or "").strip():
        st.markdown(
            f'<div class="analysis-card glass {text_direction}"><h3>◉ {safe_plain(headline_label)}</h3><p>{safe_text(headline, language)}</p></div>',
            unsafe_allow_html=True,
        )

    summary = str(analysis.get("summary", "") or "").strip()
    if not summary:
        summary = " ".join(str(item).strip() for item in analysis.get("summary_lines", []) if str(item).strip())
    if summary:
        # The summary is deliberately rendered as one continuous paragraph.
        # Sentence count is a content constraint, not a numbered UI list.
        summary_html = safe_text(summary.replace("\n", " "), language)
        st.markdown(
            f'<div class="analysis-card glass {text_direction}"><h3>▤ {safe_plain(summary_label)}</h3><div class="analysis-summary"><p>{summary_html}</p></div></div>',
            unsafe_allow_html=True,
        )

    items = [item for item in analysis.get("key_takeaways", []) if str(item).strip()][:6]
    if items:
        html_items = "".join(f"<li>{safe_text(item, language)}</li>" for item in items)
        st.markdown(
            f'<div class="analysis-card glass {text_direction}"><h3>✦ {safe_plain(points_label)}</h3><ul>{html_items}</ul></div>',
            unsafe_allow_html=True,
        )

