from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests
import streamlit as st

from config import HTTP_TIMEOUT, OLLAMA_MODEL


class AIUnavailable(RuntimeError):
    pass


@dataclass(frozen=True)
class AIConfig:
    provider: str
    api_key: str
    base_url: str
    model: str


def _secret_value(section: Any, key: str, default: str = "") -> str:
    try:
        value = section.get(key, default)
    except Exception:
        value = default
    return str(value or default).strip()


def get_ai_config() -> AIConfig:
    try:
        section = st.secrets.get("ai", {})
    except Exception:
        section = {}

    provider = _secret_value(section, "provider", "ollama").lower()
    api_key = _secret_value(section, "api_key")
    base_url = _secret_value(section, "base_url", "https://api.openai.com/v1").rstrip("/")
    model = _secret_value(section, "model", OLLAMA_MODEL)

    return AIConfig(
        provider=provider,
        api_key=api_key,
        base_url=base_url,
        model=model,
    )


def cloud_ai_configured() -> bool:
    config = get_ai_config()
    return config.provider in {"openai", "groq", "openai_compatible"} and bool(config.api_key and config.model)


def generate_chat(
    messages: list[dict],
    *,
    temperature: float = 0.2,
    max_tokens: int = 800,
    json_mode: bool = False,
) -> str:
    config = get_ai_config()

    if config.provider in {"openai", "groq", "openai_compatible"}:
        if not config.api_key:
            raise AIUnavailable("مفتاح مزود الذكاء الاصطناعي السحابي غير مُعدّ في Render.")

        payload: dict[str, Any] = {
            "model": config.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        try:
            response = requests.post(
                f"{config.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {config.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=max(HTTP_TIMEOUT, 30),
            )
            response.raise_for_status()
            data = response.json()
            return str(data["choices"][0]["message"]["content"] or "").strip()
        except (requests.RequestException, KeyError, IndexError, TypeError, ValueError) as error:
            raise AIUnavailable("تعذر الاتصال بمزود الذكاء الاصطناعي السحابي حاليًا.") from error

    try:
        from ollama import chat

        response = chat(
            model=config.model or OLLAMA_MODEL,
            messages=messages,
            format="json" if json_mode else None,
            options={
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        )
        return str(response.message.content or "").strip()
    except Exception as error:
        raise AIUnavailable(
            "المساعد المحلي Ollama غير متاح على خادم Render. "
            "أضف قسم [ai] في Secret File لاستخدام مزود سحابي."
        ) from error
