from __future__ import annotations

from functools import lru_cache
import re

ARABIC_PATTERN = re.compile(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]")
LATIN_PATTERN = re.compile(r"[A-Za-z]")


def _needs_translation(text: str, target: str) -> bool:
    if not text.strip():
        return False
    arabic = len(ARABIC_PATTERN.findall(text))
    latin = len(LATIN_PATTERN.findall(text))
    return (target == "ar" and latin > arabic) or (target == "en" and arabic > 0)


@lru_cache(maxsize=512)
def translate_text(text: str, target: str) -> str:
    value = str(text or "").strip()
    if not _needs_translation(value, target):
        return value
    try:
        from deep_translator import GoogleTranslator

        translated = GoogleTranslator(source="auto", target=target).translate(value)
        return str(translated or value).strip()
    except Exception:
        return value


def translate_items(items: list[str], target: str) -> list[str]:
    return [translate_text(str(item), target) for item in items if str(item).strip()]
