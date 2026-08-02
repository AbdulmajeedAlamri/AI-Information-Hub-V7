from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
from typing import Any
from urllib.parse import quote_plus
from zoneinfo import ZoneInfo

import feedparser
import streamlit as st
from bs4 import BeautifulSoup

from services.http_client import SESSION
from config import HTTP_TIMEOUT

from config import COUNTRIES


TZ = ZoneInfo("Asia/Riyadh")


def _clean_html(text: str) -> str:
    if not text:
        return ""
    return BeautifulSoup(text, "html.parser").get_text(" ", strip=True)


def _parse_datetime(item: Any) -> datetime | None:
    parsed = item.get("published_parsed")

    if not parsed:
        return None

    try:
        return datetime(
            parsed.tm_year,
            parsed.tm_mon,
            parsed.tm_mday,
            parsed.tm_hour,
            parsed.tm_min,
            parsed.tm_sec,
            tzinfo=timezone.utc,
        ).astimezone(TZ)
    except (TypeError, ValueError):
        return None


def _range(
    period: str,
    start_date: date | None,
    end_date: date | None,
) -> tuple[datetime | None, datetime | None]:
    now = datetime.now(TZ)

    if period == "all":
        return None, None
    if period == "today":
        return datetime.combine(now.date(), time.min, tzinfo=TZ), now
    if period == "24_hours":
        return now - timedelta(hours=24), now
    if period == "3_days":
        return now - timedelta(days=3), now
    if period == "7_days":
        return now - timedelta(days=7), now
    if period == "30_days":
        return now - timedelta(days=30), now
    if period == "custom" and start_date and end_date:
        if start_date > end_date:
            start_date, end_date = end_date, start_date

        return (
            datetime.combine(start_date, time.min, tzinfo=TZ),
            datetime.combine(end_date, time.max, tzinfo=TZ),
        )

    return None, None


def _inside(
    published: datetime | None,
    start_dt: datetime | None,
    end_dt: datetime | None,
) -> bool:
    if start_dt is None and end_dt is None:
        return True
    if published is None:
        return False
    if start_dt and published < start_dt:
        return False
    if end_dt and published > end_dt:
        return False
    return True


def _image(item: Any) -> str:
    media = item.get("media_content") or []
    if media:
        return media[0].get("url", "")

    thumbnail = item.get("media_thumbnail") or []
    if thumbnail:
        return thumbnail[0].get("url", "")

    return ""


def _locale(language: str, country_code: str) -> tuple[str, str]:
    """Return Google News locale parameters in the format it expects."""
    if language == "ar":
        return "ar", f"{country_code}:ar"
    return "en-US", f"{country_code}:en"


def _feed_url(query: str, hl: str, gl: str, ceid: str) -> str:
    return (
        "https://news.google.com/rss/search"
        f"?q={quote_plus(query)}&hl={hl}&gl={gl}&ceid={ceid}"
    )


def _load_feed(url: str):
    """Fetch RSS with our browser-like session instead of feedparser's basic client.

    Render IPs are occasionally served an empty/blocked response by Google when the
    default feedparser user agent is used. Fetching explicitly also lets us detect
    HTTP failures rather than presenting them as a valid empty search.
    """
    response = SESSION.get(url, timeout=HTTP_TIMEOUT)
    response.raise_for_status()
    return feedparser.parse(response.content)


def _feed_entries(query: str, hl: str, gl: str, ceid: str) -> list[Any]:
    feed = _load_feed(_feed_url(query, hl, gl, ceid))
    entries = list(getattr(feed, "entries", []) or [])
    if getattr(feed, "bozo", False) and not entries:
        raise RuntimeError("تعذر قراءة استجابة خدمة الأخبار.")
    return entries


@st.cache_data(ttl=300, show_spinner=False, max_entries=128)
def search_news(
    query: str,
    language: str,
    country_name: str,
    limit: int,
    period: str,
    start_date: date | None,
    end_date: date | None,
    sort_order: str,
) -> list[dict]:
    query = query.strip()
    if not query:
        return []

    gl, default_ceid = COUNTRIES[country_name]
    hl, ceid = _locale(language, gl)
    # Preserve a valid configured edition when it matches the requested language.
    if default_ceid.endswith(f":{language}"):
        ceid = default_ceid

    start_dt, end_dt = _range(period, start_date, end_date)

    dated_query = query
    if start_dt is not None:
        dated_query += f" after:{start_dt.date().isoformat()}"
    if end_dt is not None:
        dated_query += f" before:{(end_dt.date() + timedelta(days=1)).isoformat()}"

    # Google News RSS is inconsistent with date operators, especially for Arabic
    # queries. First try the server-side date query, then retry the plain query and
    # apply the exact date range locally. This prevents false "no results" screens.
    try:
        entries = _feed_entries(dated_query, hl, gl, ceid)
        if not entries and dated_query != query:
            entries = _feed_entries(query, hl, gl, ceid)
    except Exception as first_error:
        try:
            entries = _feed_entries(query, hl, gl, ceid)
        except Exception as second_error:
            raise RuntimeError("تعذر الاتصال بخدمة الأخبار حاليًا. حاول بعد قليل.") from second_error

    results: list[dict] = []
    candidates = entries[: max(200, limit * 15)]
    for item in candidates:
        published = _parse_datetime(item)
        if not _inside(published, start_dt, end_dt):
            continue

        source = item.source.get("title", "") if item.get("source") else ""
        results.append(
            {
                "id": item.get("id") or item.get("link") or item.get("title"),
                "title": item.get("title", ""),
                "link": item.get("link", ""),
                "source": source,
                "description": _clean_html(item.get("summary", "")),
                "image_url": _image(item),
                "country": country_name,
                "published_datetime": published,
                "published_date": published.strftime("%d/%m/%Y") if published else "غير متوفر",
                "published_time": published.strftime("%I:%M %p") if published else "غير متوفر",
            }
        )

    results.sort(
        key=lambda article: article.get("published_datetime")
        or datetime.min.replace(tzinfo=TZ),
        reverse=sort_order == "newest",
    )
    return results[:limit]


def trending_topics(language: str) -> list[str]:
    return (
        [
            "الذكاء الاصطناعي",
            "الأسواق العالمية",
            "الطاقة",
            "كرة القدم",
            "التقنية",
            "الصحة",
        ]
        if language == "ar"
        else [
            "Artificial Intelligence",
            "Global Markets",
            "Energy",
            "Football",
            "Technology",
            "Health",
        ]
    )
