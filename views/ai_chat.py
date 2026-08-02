from __future__ import annotations

import streamlit as st

from components.common import page_header
from database.db import (
    add_chat_message,
    create_chat_session,
    delete_chat_session,
    get_chat_messages,
    list_chat_sessions,
    rename_chat_session,
)
from services.llm_service import AIUnavailable, generate_chat
from utils.i18n import current_language, direction, tr
from utils.text import clean_generated_text, safe_text


def _new_session() -> str:
    session_id = create_chat_session()
    st.session_state.active_chat_session = session_id
    return session_id


def render_ai_chat() -> None:
    language = current_language()
    text_direction = direction(language)
    new_title = tr("محادثة جديدة", "New conversation", language)

    page_header(
        tr("🤖 المساعد الذكي", "🤖 AI Assistant", language),
        tr(
            "محادثات محفوظة في حسابك السحابي عبر Supabase.",
            "Conversations are saved to your cloud account through Supabase.",
            language,
        ),
    )

    sessions = list_chat_sessions(100)
    sidebar_column, chat_column = st.columns([1, 3], gap="large")

    with sidebar_column:
        if st.button(tr("➕ محادثة جديدة", "➕ New conversation", language), type="primary", use_container_width=True):
            _new_session()
            st.rerun()

        if sessions:
            labels = {
                str(item["id"]): item.get("title") or new_title
                for item in sessions
            }
            session_ids = list(labels)
            current = str(st.session_state.get("active_chat_session") or session_ids[0])
            if current not in session_ids:
                current = session_ids[0]
            selected = st.radio(
                tr("المحادثات", "Conversations", language),
                session_ids,
                index=session_ids.index(current),
                format_func=lambda value: labels[value],
                label_visibility="collapsed",
            )
            st.session_state.active_chat_session = selected
        else:
            selected = ""

    with chat_column:
        session_id = str(st.session_state.get("active_chat_session") or selected or "")
        if not session_id:
            st.info(tr("أنشئ محادثة جديدة للبدء.", "Create a new conversation to begin.", language))
            return

        current_session = next((item for item in sessions if str(item["id"]) == session_id), {})
        title = st.text_input(
            tr("عنوان المحادثة", "Conversation title", language),
            value=current_session.get("title", new_title),
            key=f"chat_title_{session_id}_{language}",
        )

        title_columns = st.columns([3, 1])
        with title_columns[0]:
            if st.button(tr("حفظ العنوان", "Save title", language), key=f"save_title_{session_id}", use_container_width=True):
                rename_chat_session(session_id, title.strip() or new_title)
                st.rerun()
        with title_columns[1]:
            if st.button(tr("حذف المحادثة", "Delete conversation", language), key=f"delete_session_{session_id}", use_container_width=True):
                delete_chat_session(session_id)
                st.session_state.pop("active_chat_session", None)
                st.rerun()

        messages = get_chat_messages(session_id)
        for message in messages:
            css = "chat-user" if message["role"] == "user" else "chat-assistant"
            role_name = tr("أنت", "You", language) if message["role"] == "user" else tr("المساعد", "Assistant", language)
            st.markdown(
                f'<div class="chat-message {css} {text_direction}">'
                f'<strong>{role_name}</strong><br>'
                f'{safe_text(message["content"], language)}'
                f'</div>',
                unsafe_allow_html=True,
            )

        question = st.text_input(tr("اكتب سؤالك", "Write your question", language), key=f"chat_input_{session_id}_{language}")
        if st.button(tr("إرسال", "Send", language), type="primary", use_container_width=True, key=f"chat_send_{session_id}") and question.strip():
            add_chat_message(session_id, "user", question.strip())
            try:
                answer = generate_chat(
                    [{"role": item["role"], "content": item["content"]} for item in messages[-10:]]
                    + [{"role": "user", "content": question.strip()}],
                    temperature=0.2,
                    max_tokens=800,
                )
                answer = clean_generated_text(answer, language)
            except AIUnavailable as error:
                answer = str(error)
            except Exception:
                answer = tr("تعذر تشغيل المساعد مؤقتًا. حاول بعد قليل.", "The assistant is temporarily unavailable. Please try again shortly.", language)

            add_chat_message(session_id, "assistant", answer)
            if current_session.get("title") in (None, "", "محادثة جديدة", "New conversation"):
                rename_chat_session(session_id, question.strip()[:60])
            st.rerun()
