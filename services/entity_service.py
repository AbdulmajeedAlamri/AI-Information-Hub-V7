from __future__ import annotations

import streamlit as st

from services.http_client import ExternalServiceError, get_json


def _search_language(name: str, language: str) -> dict:
    search = get_json(
        f"https://{language}.wikipedia.org/w/api.php",
        {
            "action": "query",
            "list": "search",
            "srsearch": name,
            "srlimit": 3,
            "format": "json",
            "utf8": 1,
        },
    )
    results = search.get("query", {}).get("search", [])
    if not results:
        return {"found": False}

    title = results[0]["title"]
    data = get_json(
        f"https://{language}.wikipedia.org/w/api.php",
        {
            "action": "query",
            "prop": "extracts|pageimages|info",
            "titles": title,
            "exintro": 1,
            "explaintext": 1,
            "piprop": "original|thumbnail",
            "pithumbsize": 900,
            "inprop": "url",
            "format": "json",
            "redirects": 1,
        },
    )
    pages = data.get("query", {}).get("pages", {})
    if not pages:
        return {"found": False}

    page = next(iter(pages.values()))
    summary = str(page.get("extract", "") or "").strip()
    if not summary:
        return {"found": False}

    return {
        "found": True,
        "title": page.get("title", title),
        "summary": summary,
        "image_url": (
            page.get("original", {}).get("source")
            or page.get("thumbnail", {}).get("source")
            or ""
        ),
        "page_url": page.get("fullurl", ""),
        "source_language": language,
    }


@st.cache_data(ttl=3600, show_spinner=False)
def search_entity(name: str, language: str) -> dict:
    name = str(name or "").strip()
    if len(name) < 2:
        return {"found": False, "message": "اكتب اسمًا واضحًا من حرفين على الأقل."}

    preferred = "ar" if language == "ar" else "en"
    languages = [preferred, "en" if preferred == "ar" else "ar"]

    try:
        for candidate in languages:
            result = _search_language(name, candidate)
            if result.get("found"):
                return result
        return {
            "found": False,
            "message": "لم يتم العثور على صفحة موسوعية واضحة. جرّب الاسم الرسمي أو باللغة الإنجليزية.",
        }
    except ExternalServiceError as error:
        return {"found": False, "message": str(error)}
    except Exception:
        return {"found": False, "message": "تعذر جلب البيانات مؤقتًا."}

def get_entity_profile(name: str, language: str) -> dict:
    """Compatibility entry point used by the entity analysis view.

    The original V11 view imported ``get_entity_profile`` while the service
    exposed only ``search_entity``. Keeping this wrapper makes the public
    service API explicit and prevents startup ImportError failures.
    """
    return search_entity(name, language)

