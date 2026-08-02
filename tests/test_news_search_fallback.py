from datetime import datetime
from types import ModuleType, SimpleNamespace
from zoneinfo import ZoneInfo
import sys

# The lightweight test environment does not install the production RSS parser.
# Provide only the interface used by news_service before importing it.
if "feedparser" not in sys.modules:
    fake_feedparser = ModuleType("feedparser")
    fake_feedparser.parse = lambda content: SimpleNamespace(entries=[], bozo=False)
    sys.modules["feedparser"] = fake_feedparser

if "streamlit" not in sys.modules:
    fake_streamlit = ModuleType("streamlit")

    def cache_data(*args, **kwargs):
        def decorator(func):
            func.clear = lambda: None
            return func
        return decorator

    fake_streamlit.cache_data = cache_data
    sys.modules["streamlit"] = fake_streamlit

import services.news_service as news_service


class Item(dict):
    __getattr__ = dict.get


def _entry(title="خبر تقني"):
    dt = datetime.now(ZoneInfo("Asia/Riyadh")).astimezone(ZoneInfo("UTC"))
    parsed = SimpleNamespace(
        tm_year=dt.year,
        tm_mon=dt.month,
        tm_mday=dt.day,
        tm_hour=dt.hour,
        tm_min=dt.minute,
        tm_sec=dt.second,
    )
    return Item(
        id="1",
        title=title,
        link="https://example.com/story",
        summary="<p>وصف الخبر</p>",
        published_parsed=parsed,
        source={"title": "Example"},
    )


def test_retries_plain_query_when_dated_query_is_empty(monkeypatch):
    calls = []

    def fake_entries(query, hl, gl, ceid):
        calls.append(query)
        return [] if "after:" in query else [_entry()]

    monkeypatch.setattr(news_service, "_feed_entries", fake_entries)
    news_service.search_news.clear()

    results = news_service.search_news(
        query="التقنية",
        language="ar",
        country_name="السعودية",
        limit=10,
        period="today",
        start_date=None,
        end_date=None,
        sort_order="newest",
    )

    assert len(calls) == 2
    assert "after:" in calls[0]
    assert calls[1] == "التقنية"
    assert results
    assert results[0]["title"] == "خبر تقني"


def test_google_rss_is_fetched_with_shared_http_session(monkeypatch):
    class Response:
        content = b"<rss><channel></channel></rss>"

        @staticmethod
        def raise_for_status():
            return None

    observed = {}

    def fake_get(url, timeout):
        observed["url"] = url
        observed["timeout"] = timeout
        return Response()

    monkeypatch.setattr(news_service.SESSION, "get", fake_get)
    news_service._load_feed("https://example.com/rss")

    assert observed["url"] == "https://example.com/rss"
    assert observed["timeout"] == news_service.HTTP_TIMEOUT
