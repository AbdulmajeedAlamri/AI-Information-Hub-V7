from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from services.auth_service import get_current_user_id
from services.supabase_service import get_admin_client


def initialise_database() -> None:
    # الجداول موجودة في Supabase عبر ملفات migrations.
    return None


def _json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, (UUID, Decimal)):
        return str(value)
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_json_safe(item) for item in value]
    return str(value)


def add_history_db(kind: str, query: str, metadata: dict | None = None) -> None:
    user_id = get_current_user_id()
    get_admin_client().table("search_history").insert(
        {
            "user_id": user_id,
            "search_type": kind,
            "query": query,
            "metadata": _json_safe(metadata or {}),
        }
    ).execute()


def get_history_db(limit: int = 100) -> list[dict[str, Any]]:
    user_id = get_current_user_id()
    response = (
        get_admin_client()
        .table("search_history")
        .select("id,search_type,query,metadata,created_at")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return response.data or []


def clear_history_db() -> None:
    user_id = get_current_user_id()
    (
        get_admin_client()
        .table("search_history")
        .delete()
        .eq("user_id", user_id)
        .execute()
    )


def add_favorite_db(item: dict) -> None:
    user_id = get_current_user_id()
    identity = str(item.get("id") or item.get("link") or item.get("title"))
    item_type = str(item.get("type") or "news")
    get_admin_client().table("favorites").upsert(
        {
            "user_id": user_id,
            "item_type": item_type,
            "item_key": identity,
            "title": str(item.get("title") or identity),
            "payload": _json_safe(item),
        },
        on_conflict="user_id,item_type,item_key",
    ).execute()


def remove_favorite_db(identity: str) -> None:
    user_id = get_current_user_id()
    (
        get_admin_client()
        .table("favorites")
        .delete()
        .eq("user_id", user_id)
        .eq("item_key", identity)
        .execute()
    )


def get_favorites_db() -> list[dict]:
    user_id = get_current_user_id()
    response = (
        get_admin_client()
        .table("favorites")
        .select("item_key,item_type,title,payload,created_at")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )
    return response.data or []


def save_profile_db(profile: dict) -> None:
    user_id = get_current_user_id()
    get_admin_client().table("profiles").update(
        {
            "full_name": profile.get("name", ""),
            "bio": profile.get("bio", ""),
            "updated_at": datetime.utcnow().isoformat(),
        }
    ).eq("id", user_id).execute()


def load_profile_db() -> dict:
    user_id = get_current_user_id()
    response = (
        get_admin_client()
        .table("profiles")
        .select("id,email,full_name,avatar_url,bio,role,created_at,updated_at")
        .eq("id", user_id)
        .limit(1)
        .execute()
    )
    rows = response.data or []
    if not rows:
        return {
            "name": "",
            "email": "",
            "bio": "",
            "avatar_url": "",
            "role": "user",
        }

    row = rows[0]
    return {
        "id": row.get("id", ""),
        "name": row.get("full_name", ""),
        "email": row.get("email", ""),
        "bio": row.get("bio", ""),
        "avatar_url": row.get("avatar_url", ""),
        "role": row.get("role", "user"),
        "created_at": row.get("created_at", ""),
        "updated_at": row.get("updated_at", ""),
    }


def load_user_settings() -> dict:
    user_id = get_current_user_id()
    response = (
        get_admin_client()
        .table("user_settings")
        .select("theme,language,preferences,updated_at")
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )
    rows = response.data or []
    return rows[0] if rows else {
        "theme": "dark",
        "language": "ar",
        "preferences": {},
    }


def save_user_settings(settings: dict) -> None:
    user_id = get_current_user_id()
    get_admin_client().table("user_settings").upsert(
        {
            "user_id": user_id,
            "theme": settings.get("theme", "dark"),
            "language": settings.get("language", "ar"),
            "preferences": _json_safe(settings.get("preferences", {})),
            "updated_at": datetime.utcnow().isoformat(),
        },
        on_conflict="user_id",
    ).execute()


def create_chat_session(title: str = "محادثة جديدة", context_type: str = "general") -> str:
    user_id = get_current_user_id()
    response = get_admin_client().table("chat_sessions").insert(
        {
            "user_id": user_id,
            "title": title,
            "context_type": context_type,
        }
    ).execute()
    rows = response.data or []
    return str(rows[0]["id"]) if rows else ""


def list_chat_sessions(limit: int = 50) -> list[dict]:
    user_id = get_current_user_id()
    response = (
        get_admin_client()
        .table("chat_sessions")
        .select("id,title,context_type,context_key,created_at,updated_at")
        .eq("user_id", user_id)
        .order("updated_at", desc=True)
        .limit(limit)
        .execute()
    )
    return response.data or []


def rename_chat_session(session_id: str, title: str) -> None:
    user_id = get_current_user_id()
    (
        get_admin_client()
        .table("chat_sessions")
        .update({"title": title, "updated_at": datetime.utcnow().isoformat()})
        .eq("id", session_id)
        .eq("user_id", user_id)
        .execute()
    )


def delete_chat_session(session_id: str) -> None:
    user_id = get_current_user_id()
    (
        get_admin_client()
        .table("chat_sessions")
        .delete()
        .eq("id", session_id)
        .eq("user_id", user_id)
        .execute()
    )


def add_chat_message(session_id: str, role: str, content: str) -> None:
    user_id = get_current_user_id()
    get_admin_client().table("chat_messages").insert(
        {
            "session_id": session_id,
            "user_id": user_id,
            "role": role,
            "content": content,
        }
    ).execute()

    (
        get_admin_client()
        .table("chat_sessions")
        .update({"updated_at": datetime.utcnow().isoformat()})
        .eq("id", session_id)
        .eq("user_id", user_id)
        .execute()
    )


def get_chat_messages(session_id: str) -> list[dict]:
    user_id = get_current_user_id()
    response = (
        get_admin_client()
        .table("chat_messages")
        .select("id,role,content,created_at")
        .eq("session_id", session_id)
        .eq("user_id", user_id)
        .order("created_at")
        .execute()
    )
    return response.data or []


def _count(table: str, user_id: str, extra_column: str | None = None, extra_value: str | None = None) -> int:
    query = (
        get_admin_client()
        .table(table)
        .select("*", count="exact", head=True)
        .eq("user_id", user_id)
    )
    if extra_column and extra_value:
        query = query.eq(extra_column, extra_value)
    response = query.execute()
    return int(response.count or 0)


def dashboard_counts() -> dict:
    user_id = get_current_user_id()
    return {
        "history": _count("search_history", user_id),
        "favorites": _count("favorites", user_id),
        "people": _count("search_history", user_id, "search_type", "person"),
        "news": _count("search_history", user_id, "search_type", "news"),
        "chats": _count("chat_sessions", user_id),
        "analyses": _count("news_analyses", user_id),
    }
