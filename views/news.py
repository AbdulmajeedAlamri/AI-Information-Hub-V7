from __future__ import annotations

from datetime import date, timedelta
import hashlib

import streamlit as st

from components.common import page_header, render_analysis
from config import CATEGORIES, COUNTRIES
from services.ai_service import answer_question, summarise
from services.article_service import get_article_text
from services.news_service import search_news, trending_topics
from utils.exporters import make_docx, make_image, make_json, make_pdf, make_text
from utils.storage import add_history, toggle_favorite
from utils.text import safe_plain, safe_text


def _chat(
    article: dict,
    article_text: str,
    language: str,
    identity: str,
    enabled: bool,
) -> None:
    history_key = f"article_chat_{identity}_{language}"

    if history_key not in st.session_state:
        st.session_state[history_key] = []

    direction = "rtl" if language == "ar" else "ltr"

    st.markdown(
        f"""
        <div class="chat-shell glass {direction}">
          <h3>{"🤖 المحادثة مع الخبر" if language == "ar" else "🤖 Article AI Chat"}</h3>
          <p>{"اسأل عن الأسباب والتأثير والمخاطر والجهات المستفيدة." if language == "ar" else "Ask about causes, impact, risks, and beneficiaries."}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not enabled:
        st.info(
            "حلّل الخبر أولًا لتفعيل المحادثة."
            if language == "ar"
            else "Analyse the article first to enable chat."
        )

    for message in st.session_state[history_key]:
        css = (
            "chat-user"
            if message["role"] == "user"
            else "chat-assistant"
        )

        st.markdown(
            f'<div class="chat-message {css} {direction}">'
            f'<strong>{safe_plain(message["role"])}</strong><br>'
            f'{safe_text(message["content"], language)}'
            f'</div>',
            unsafe_allow_html=True,
        )

    question = st.text_input(
        "اكتب سؤالك"
        if language == "ar"
        else "Write your question",
        key=f"chat_input_{identity}_{language}",
        disabled=not enabled,
    )

    send_column, clear_column = st.columns([3, 1])

    with send_column:
        send = st.button(
            "إرسال"
            if language == "ar"
            else "Send",
            key=f"chat_send_{identity}_{language}",
            type="primary",
            use_container_width=True,
            disabled=not enabled,
        )

    with clear_column:
        clear = st.button(
            "مسح"
            if language == "ar"
            else "Clear",
            key=f"chat_clear_{identity}_{language}",
            use_container_width=True,
            disabled=not enabled,
        )

    if clear:
        st.session_state[history_key] = []
        st.rerun()

    if send and question.strip():
        answer = answer_question(
            question=question,
            title=article.get("title", ""),
            description=article.get("description", ""),
            article_text=article_text,
            history=st.session_state[history_key],
            language=language,
        )

        st.session_state[history_key].append(
            {"role": "user", "content": question.strip()}
        )
        st.session_state[history_key].append(
            {"role": "assistant", "content": answer}
        )
        st.rerun()


def render_news() -> None:
    from utils.i18n import category_label, country_label, current_language, direction, tr

    ui_language = current_language()
    ui_direction = direction(ui_language)

    page_header(
        tr("📰 مركز الأخبار الذكي", "📰 Smart News Center", ui_language),
        tr(
            "صور، دول، مجالات، رائج، عاجل، تحليل، محادثة، مفضلة، وتصدير.",
            "Images, countries, topics, trends, breaking news, analysis, chat, favorites, and export.",
            ui_language,
        ),
    )

    with st.sidebar:
        st.markdown(f"### {tr('إعدادات الأخبار','News settings',ui_language)}")
        news_language = st.selectbox(
            tr("لغة الأخبار", "News language", ui_language), ["ar", "en"],
            format_func=lambda value: tr("العربية", "Arabic", ui_language) if value == "ar" else tr("الإنجليزية", "English", ui_language),
            key="news_language_choice",
        )
        analysis_language = st.selectbox(
            tr("لغة التحليل", "Analysis language", ui_language), ["ar", "en"],
            format_func=lambda value: tr("العربية", "Arabic", ui_language) if value == "ar" else tr("الإنجليزية", "English", ui_language),
            key="analysis_language_choice",
        )
        country_name = st.selectbox(
            tr("الدولة", "Country", ui_language), list(COUNTRIES),
            format_func=lambda value: country_label(value, ui_language), key="news_country_choice",
        )
        category_name = st.selectbox(
            tr("المجال", "Topic", ui_language), list(CATEGORIES),
            format_func=lambda value: category_label(value, ui_language), key="news_category_choice",
        )
        period = st.selectbox(
            tr("الفترة", "Period", ui_language),
            ["today", "24_hours", "3_days", "7_days", "30_days", "all", "custom"],
            format_func=lambda value: {
                "today": tr("اليوم فقط", "Today only", ui_language),
                "24_hours": tr("آخر 24 ساعة", "Last 24 hours", ui_language),
                "3_days": tr("آخر 3 أيام", "Last 3 days", ui_language),
                "7_days": tr("آخر 7 أيام", "Last 7 days", ui_language),
                "30_days": tr("آخر 30 يومًا", "Last 30 days", ui_language),
                "all": tr("جميع الأخبار", "All news", ui_language),
                "custom": tr("فترة مخصصة", "Custom range", ui_language),
            }[value],
            key="news_period_choice",
        )
        sort_order = st.selectbox(
            tr("الترتيب", "Sort order", ui_language), ["newest", "oldest"],
            format_func=lambda value: tr("الأحدث أولًا", "Newest first", ui_language) if value == "newest" else tr("الأقدم أولًا", "Oldest first", ui_language),
            key="news_sort_choice",
        )
        limit = st.slider(tr("عدد الأخبار", "Number of articles", ui_language), 5, 30, 10, 5, key="news_limit_choice")
        start_date = None
        end_date = None
        if period == "custom":
            end_date = st.date_input(tr("إلى تاريخ", "End date", ui_language), value=date.today(), key="news_end_date")
            start_date = st.date_input(tr("من تاريخ", "Start date", ui_language), value=end_date - timedelta(days=7), key="news_start_date")

    suggested = CATEGORIES[category_name][news_language]
    category_state = f"{category_name}_{news_language}"
    if "news_query_value" not in st.session_state:
        st.session_state["news_query_value"] = suggested
    if st.session_state.get("last_news_category") != category_state:
        if category_name != "بحث مخصص":
            st.session_state["news_query_value"] = suggested
        st.session_state["last_news_category"] = category_state

    st.markdown(f"### 🔥 {tr('الأخبار الرائجة','Trending News',ui_language)}")
    topic_columns = st.columns(3)
    for index, topic in enumerate(trending_topics(news_language)):
        with topic_columns[index % 3]:
            if st.button(topic, key=f"topic_{index}_{news_language}", use_container_width=True):
                st.session_state["news_query_value"] = topic
                st.rerun()

    query = st.text_input(tr("موضوع البحث", "Search topic", ui_language), key="news_query_value")
    if st.button(tr("🔍 البحث", "🔍 Search", ui_language), type="primary", use_container_width=True):
        if not query.strip():
            st.warning(tr("اكتب موضوعًا أو اختر مجالًا.", "Enter a topic or choose a category.", ui_language))
        else:
            try:
                with st.spinner(tr("جارٍ جلب الأخبار...", "Fetching news...", ui_language)):
                    st.session_state.news_results = search_news(
                        query=query, language=news_language, country_name=country_name, limit=limit,
                        period=period, start_date=start_date, end_date=end_date, sort_order=sort_order,
                    )
            except Exception as error:
                st.session_state.news_results = []
                st.error(tr("تعذر الاتصال بمصدر الأخبار حاليًا. حاول بعد قليل.", "The news source is temporarily unavailable. Please try again shortly.", ui_language))
                st.caption(str(error))
            else:
                add_history("news", query)
                if st.session_state.news_results:
                    st.toast(tr(f"تم العثور على {len(st.session_state.news_results)} خبر", f"Found {len(st.session_state.news_results)} articles", ui_language))
                else:
                    st.warning(tr("لم تُعثر نتائج مطابقة. جرّب عبارة أقصر أو فترة أوسع.", "No matching results were found. Try a shorter query or a wider date range.", ui_language))

    results = st.session_state.get("news_results", [])
    if not results:
        st.info(tr("ابدأ عملية البحث لعرض الأخبار.", "Start a search to view news.", ui_language))
        return

    for index, article in enumerate(results):
        identity_source = str(article.get("id") or article.get("link") or article.get("title") or index)
        identity = hashlib.sha256(identity_source.encode("utf-8", errors="ignore")).hexdigest()[:16]
        analysis_key = f"analysis_{identity}_{analysis_language}"
        text_key = f"article_text_{identity}"

        with st.container(border=True):
            image_column, content_column = st.columns([0.85, 2.15])
            with image_column:
                if article.get("image_url"):
                    st.image(article["image_url"], use_container_width=True)
                else:
                    st.markdown(
                        f'<div class="entity-card glass {ui_direction}"><h2>📰</h2><p>{tr("لا توجد صورة متاحة","No image available",ui_language)}</p></div>',
                        unsafe_allow_html=True,
                    )
            with content_column:
                st.markdown(f'<div class="{ui_direction}"><h3>{index + 1}. {safe_plain(article.get("title"))}</h3></div>', unsafe_allow_html=True)
                meta_html = (
                    f'<div class="meta {ui_direction}">'
                    f'<span>🌐 {safe_plain(article.get("source"))}</span>'
                    f'<span>🌍 {safe_plain(country_label(article.get("country", ""), ui_language))}</span>'
                    f'<span>📅 {safe_plain(article.get("published_date"))}</span>'
                    f'<span>🕒 {safe_plain(article.get("published_time"))}</span>'
                    '</div>'
                )
                st.markdown(meta_html, unsafe_allow_html=True)
                with st.expander(tr("عرض الوصف", "Show description", ui_language)):
                    st.write(article.get("description", ""))
                buttons = st.columns(4)
                with buttons[0]:
                    if article.get("link"):
                        st.link_button(tr("🌐 الخبر", "🌐 Open article", ui_language), article["link"], use_container_width=True)
                with buttons[1]:
                    analyse = st.button(tr("🤖 تحليل", "🤖 Analyze", ui_language), key=f"analyse_{identity}_{analysis_language}", use_container_width=True)
                with buttons[2]:
                    favourite = st.button(tr("⭐ مفضلة", "⭐ Favorite", ui_language), key=f"favorite_{identity}", use_container_width=True)
                with buttons[3]:
                    st.button(tr("📤 مشاركة", "📤 Share", ui_language), key=f"share_{identity}", use_container_width=True,
                              help=tr("استخدم رابط الخبر الأصلي للمشاركة.", "Use the original article link to share.", ui_language))
                if favourite:
                    added = toggle_favorite(article)
                    st.toast(tr("تمت الإضافة للمفضلة" if added else "تمت الإزالة من المفضلة", "Added to favorites" if added else "Removed from favorites", ui_language))

            if analyse:
                with st.spinner(tr("جارٍ قراءة الخبر وتحليله...", "Reading and analyzing the article...", ui_language)):
                    article_text = get_article_text(article.get("link", ""))
                    st.session_state[text_key] = article_text
                    st.session_state[analysis_key] = summarise(
                        title=article.get("title", ""), description=article.get("description", ""),
                        article_text=article_text, language=analysis_language,
                    )

            enabled = analysis_key in st.session_state
            _chat(article=article, article_text=st.session_state.get(text_key, ""), language=analysis_language, identity=identity, enabled=enabled)
            if enabled:
                analysis = st.session_state[analysis_key]
                render_analysis(analysis, analysis_language)
                st.markdown(f"### 📄 {tr('أدوات التقرير','Report tools',ui_language)}")
                st.caption(tr("تم تحسين التصدير لدعم العربية والإنجليزية واتجاه النص تلقائيًا.", "Exports support Arabic, English, and automatic text direction.", ui_language))
                export_columns = st.columns(5)
                with export_columns[0]:
                    st.download_button("PDF", make_pdf(analysis), "news_report.pdf", "application/pdf", use_container_width=True)
                with export_columns[1]:
                    st.download_button("Word", make_docx(analysis), "news_report.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)
                with export_columns[2]:
                    st.download_button("PNG", make_image(analysis), "news_report.png", "image/png", use_container_width=True)
                with export_columns[3]:
                    st.download_button("TXT", make_text(analysis), "news_report.txt", "text/plain; charset=utf-8", use_container_width=True)
                with export_columns[4]:
                    st.download_button("JSON", make_json(analysis), "news_report.json", "application/json", use_container_width=True)
                with st.expander(tr("معاينة النص الخام", "Raw text preview", ui_language)):
                    st.code(analysis.get("summary", ""), language=None)
