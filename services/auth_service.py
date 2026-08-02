from __future__ import annotations

from typing import Any

import streamlit as st

from services.supabase_service import get_admin_client, is_supabase_configured


def is_auth_configured() -> bool:
    try:
        auth = st.secrets["auth"]
        required = (
            "redirect_uri",
            "cookie_secret",
            "client_id",
            "client_secret",
            "server_metadata_url",
        )
        return all(auth.get(key) for key in required)
    except (KeyError, FileNotFoundError):
        return False


def current_identity() -> dict[str, Any]:
    if not getattr(st.user, "is_logged_in", False):
        return {}

    return {
        "sub": str(st.user.get("sub", "")),
        "email": str(st.user.get("email", "")).strip().lower(),
        "name": str(st.user.get("name", "") or st.user.get("given_name", "")),
        "picture": str(st.user.get("picture", "")),
    }


def render_login_screen() -> None:
    st.markdown(
        """
        <div class="hero glass rtl">
          <h1>✨ AI Information Hub</h1>
          <p>سجّل الدخول بحساب Google للوصول إلى الأخبار والتحليلات والمفضلة وسجل البحث.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not is_auth_configured():
        st.error("إعداد Google OIDC غير مكتمل داخل .streamlit/secrets.toml")
        st.code("راجع ملف .streamlit/secrets.example.toml")
        return

    st.button(
        "🔐 تسجيل الدخول باستخدام Google",
        type="primary",
        use_container_width=True,
        on_click=st.login,
    )


def _users_from_admin_response(response: Any) -> list[Any]:
    if isinstance(response, list):
        return response
    users = getattr(response, "users", None)
    if users is not None:
        return list(users)
    data = getattr(response, "data", None)
    if isinstance(data, dict):
        return list(data.get("users", []))
    return []


def _find_auth_user_by_email(email: str) -> Any | None:
    client = get_admin_client()
    page = 1
    while page <= 10:
        response = client.auth.admin.list_users(page=page, per_page=1000)
        users = _users_from_admin_response(response)
        for user in users:
            candidate = (
                user.get("email") if isinstance(user, dict) else getattr(user, "email", None)
            )
            if str(candidate or "").lower() == email:
                return user
        if len(users) < 1000:
            break
        page += 1
    return None


def _user_id(user: Any) -> str:
    if isinstance(user, dict):
        return str(user.get("id", ""))
    return str(getattr(user, "id", ""))


def sync_current_user() -> str:
    if st.session_state.get("cloud_user_id"):
        return str(st.session_state.cloud_user_id)

    identity = current_identity()
    email = identity.get("email", "")
    if not email:
        raise RuntimeError("لم يُرجع Google بريدًا إلكترونيًا صالحًا.")
    if not is_supabase_configured():
        raise RuntimeError("إعدادات Supabase غير مكتملة.")

    client = get_admin_client()
    profile_response = (
        client.table("profiles")
        .select("id,email,full_name,avatar_url,role")
        .eq("email", email)
        .limit(1)
        .execute()
    )
    rows = profile_response.data or []

    if rows:
        user_id = str(rows[0]["id"])
    else:
        existing = _find_auth_user_by_email(email)
        if existing is not None:
            user_id = _user_id(existing)
        else:
            created = client.auth.admin.create_user(
                {
                    "email": email,
                    "email_confirm": True,
                    "user_metadata": {
                        "name": identity.get("name", ""),
                        "full_name": identity.get("name", ""),
                        "avatar_url": identity.get("picture", ""),
                        "picture": identity.get("picture", ""),
                        "google_sub": identity.get("sub", ""),
                    },
                }
            )
            user_id = _user_id(created.user)

        if not user_id:
            raise RuntimeError("تعذر إنشاء هوية المستخدم داخل Supabase.")

    client.table("profiles").upsert(
        {
            "id": user_id,
            "email": email,
            "full_name": identity.get("name", ""),
            "avatar_url": identity.get("picture", ""),
        },
        on_conflict="id",
    ).execute()

    client.table("user_settings").upsert(
        {"user_id": user_id},
        on_conflict="user_id",
    ).execute()

    st.session_state.cloud_user_id = user_id
    st.session_state.cloud_identity = identity
    return user_id


def get_current_user_id() -> str:
    return sync_current_user()


def logout() -> None:
    for key in (
        "cloud_user_id",
        "cloud_identity",
        "favorites",
        "history",
    ):
        st.session_state.pop(key, None)
    st.logout()
