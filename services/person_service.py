from __future__ import annotations

from datetime import date, datetime
from typing import Any

import streamlit as st

from services.http_client import ExternalServiceError, get_json


def _search_title(name: str, language: str) -> str:
    data = get_json(
        f"https://{language}.wikipedia.org/w/api.php",
        {
            "action": "query",
            "list": "search",
            "srsearch": name,
            "srlimit": 5,
            "format": "json",
            "utf8": 1,
        },
    )
    results = data.get("query", {}).get("search", [])
    return results[0].get("title", "") if results else ""


def _page(title: str, language: str) -> dict:
    data = get_json(
        f"https://{language}.wikipedia.org/w/api.php",
        {
            "action": "query",
            "prop": "extracts|pageimages|pageprops|info",
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
        return {}
    page = next(iter(pages.values()))
    if "missing" in page:
        return {}

    props = page.get("pageprops", {})
    return {
        "title": page.get("title", title),
        "summary": page.get("extract", ""),
        "image_url": (
            page.get("original", {}).get("source")
            or page.get("thumbnail", {}).get("source")
            or ""
        ),
        "page_url": page.get("fullurl", ""),
        "wikidata_id": props.get("wikibase_item", ""),
        "disambiguation": "disambiguation" in props,
    }


def _entity(entity_id: str) -> dict:
    if not entity_id:
        return {}
    data = get_json(
        "https://www.wikidata.org/w/api.php",
        {
            "action": "wbgetentities",
            "ids": entity_id,
            "props": "labels|descriptions|claims",
            "languages": "ar|en",
            "languagefallback": 1,
            "format": "json",
        },
    )
    return data.get("entities", {}).get(entity_id, {})


def _label(entity: dict, language: str) -> str:
    labels = entity.get("labels", {})
    item = labels.get(language) or labels.get("en") or labels.get("ar")
    return item.get("value", "") if item else ""


def _description(entity: dict, language: str) -> str:
    descriptions = entity.get("descriptions", {})
    item = descriptions.get(language) or descriptions.get("en") or descriptions.get("ar")
    return item.get("value", "") if item else ""


def _ids(entity: dict, property_id: str) -> list[str]:
    values = []
    for claim in entity.get("claims", {}).get(property_id, []):
        try:
            values.append(claim["mainsnak"]["datavalue"]["value"]["id"])
        except (KeyError, TypeError):
            continue
    return list(dict.fromkeys(values))


def _strings(entity: dict, property_id: str) -> list[str]:
    values = []
    for claim in entity.get("claims", {}).get(property_id, []):
        try:
            value = claim["mainsnak"]["datavalue"]["value"]
            if isinstance(value, str):
                values.append(value)
        except (KeyError, TypeError):
            continue
    return list(dict.fromkeys(values))


def _time(entity: dict, property_id: str) -> str:
    for claim in entity.get("claims", {}).get(property_id, []):
        try:
            return claim["mainsnak"]["datavalue"]["value"]["time"]
        except (KeyError, TypeError):
            continue
    return ""


def _resolve(ids: list[str], language: str) -> list[str]:
    if not ids:
        return []
    data = get_json(
        "https://www.wikidata.org/w/api.php",
        {
            "action": "wbgetentities",
            "ids": "|".join(ids),
            "props": "labels",
            "languages": f"{language}|en|ar",
            "languagefallback": 1,
            "format": "json",
        },
    )
    output = []
    for entity_id in ids:
        labels = data.get("entities", {}).get(entity_id, {}).get("labels", {})
        item = labels.get(language) or labels.get("en") or labels.get("ar")
        if item and item.get("value"):
            output.append(item["value"])
    return output


def _format_date(value: str) -> str:
    if not value:
        return ""
    try:
        parsed = datetime.strptime(value.lstrip("+")[:10], "%Y-%m-%d").date()
        return parsed.strftime("%d/%m/%Y")
    except ValueError:
        return ""


def _age(value: str) -> int | None:
    if not value:
        return None
    try:
        born = datetime.strptime(value.lstrip("+")[:10], "%Y-%m-%d").date()
    except ValueError:
        return None
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


@st.cache_data(ttl=3600, show_spinner=False)
def search_person(name: str, language: str) -> dict[str, Any]:
    name = name.strip()
    if not name:
        return {"found": False, "message": "اكتب الاسم أولًا."}

    try:
        page = {}
        for search_language in (language, "en", "ar"):
            title = _search_title(name, search_language)
            if not title:
                continue
            candidate = _page(title, search_language)
            if candidate and candidate.get("wikidata_id") and not candidate.get("disambiguation"):
                page = candidate
                break

        if not page:
            return {"found": False, "message": "لم يتم العثور على معلومات واضحة."}

        entity = _entity(page["wikidata_id"])
        birth = _time(entity, "P569")

        return {
            "found": True,
            "id": page["wikidata_id"],
            "full_name": _label(entity, language) or page["title"],
            "description": _description(entity, language),
            "summary": page["summary"],
            "image_url": page["image_url"],
            "page_url": page["page_url"],
            "birth_date": _format_date(birth),
            "age": _age(birth),
            "occupations": _resolve(_ids(entity, "P106"), language),
            "positions": _resolve(_ids(entity, "P39"), language),
            "citizenships": _resolve(_ids(entity, "P27"), language),
            "birthplaces": _resolve(_ids(entity, "P19"), language),
            "employers": _resolve(_ids(entity, "P108"), language),
            "education": _resolve(_ids(entity, "P69"), language),
            "awards": _resolve(_ids(entity, "P166"), language),
            "companies": _resolve(_ids(entity, "P112"), language),
            "websites": _strings(entity, "P856"),
            "twitter": _strings(entity, "P2002"),
            "instagram": _strings(entity, "P2003"),
            "facebook": _strings(entity, "P2013"),
            "timeline": [{"date": _format_date(birth), "event": "الميلاد"}] if birth else [],
        }

    except ExternalServiceError as error:
        return {"found": False, "message": str(error)}
    except Exception:
        return {
            "found": False,
            "message": "تعذر جلب بيانات الشخصية مؤقتًا. حاول بعد قليل.",
        }
