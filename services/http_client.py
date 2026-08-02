from __future__ import annotations

import time
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import HTTP_RETRIES, HTTP_TIMEOUT


SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "AI-Information-Hub/6.0 (+public-information-research)"
})

retry = Retry(
    total=HTTP_RETRIES,
    connect=HTTP_RETRIES,
    read=HTTP_RETRIES,
    status=HTTP_RETRIES,
    backoff_factor=0.7,
    status_forcelist=(429, 500, 502, 503, 504),
    allowed_methods=frozenset(["GET"]),
    respect_retry_after_header=True,
)

SESSION.mount("https://", HTTPAdapter(max_retries=retry))
SESSION.mount("http://", HTTPAdapter(max_retries=retry))


class ExternalServiceError(RuntimeError):
    pass


def get_json(url: str, params: dict | None = None) -> dict:
    try:
        response = SESSION.get(url, params=params, timeout=HTTP_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as error:
        raise ExternalServiceError(
            "تعذر الاتصال بمصدر البيانات حاليًا. حاول بعد قليل."
        ) from error


def get_text(url: str) -> str:
    try:
        response = SESSION.get(url, timeout=HTTP_TIMEOUT)
        response.raise_for_status()
        return response.text
    except requests.RequestException as error:
        raise ExternalServiceError(
            "تعذر تحميل المحتوى من المصدر حاليًا."
        ) from error
