from __future__ import annotations

from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from config import MAX_ARTICLE_CHARS, HTTP_TIMEOUT
from services.http_client import SESSION


def _best_article_url(response, soup: BeautifulSoup) -> str:
    final_url = str(getattr(response, "url", "") or "")
    candidates: list[str] = []

    for selector, attribute in (
        ('link[rel="canonical"]', "href"),
        ('meta[property="og:url"]', "content"),
        ('meta[name="twitter:url"]', "content"),
    ):
        node = soup.select_one(selector)
        if node and node.get(attribute):
            candidates.append(urljoin(final_url, node.get(attribute)))

    # Google News intermediary pages often expose the publisher URL in anchors.
    if "news.google." in urlparse(final_url).netloc:
        for anchor in soup.find_all("a", href=True):
            href = urljoin(final_url, anchor["href"])
            host = urlparse(href).netloc.lower()
            if host and "google." not in host and href.startswith(("http://", "https://")):
                candidates.append(href)

    for candidate in candidates:
        host = urlparse(candidate).netloc.lower()
        if candidate.startswith(("http://", "https://")) and "news.google." not in host:
            return candidate

    return final_url


def _extract_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "noscript", "svg", "header", "footer", "nav", "aside"]):
        tag.decompose()

    selectors = [
        "article p",
        "main p",
        '[itemprop="articleBody"] p',
        ".article-body p",
        ".story-body p",
        ".entry-content p",
        ".post-content p",
        "p",
    ]

    paragraphs: list[str] = []
    seen: set[str] = set()

    for selector in selectors:
        for node in soup.select(selector):
            text = " ".join(node.get_text(" ", strip=True).split())
            if len(text) < 35 or text in seen:
                continue
            seen.add(text)
            paragraphs.append(text)
        if len(" ".join(paragraphs)) >= 1200:
            break

    if not paragraphs:
        for selector in ('meta[name="description"]', 'meta[property="og:description"]'):
            node = soup.select_one(selector)
            if node and node.get("content"):
                value = " ".join(node.get("content").split())
                if value:
                    paragraphs.append(value)

    return " ".join(paragraphs)[:MAX_ARTICLE_CHARS]


def get_article_text(url: str) -> str:
    if not url:
        return ""

    try:
        response = SESSION.get(url, timeout=HTTP_TIMEOUT, allow_redirects=True)
        response.raise_for_status()
        first_soup = BeautifulSoup(response.text, "html.parser")
        article_url = _best_article_url(response, first_soup)

        if article_url and article_url != str(response.url):
            response = SESSION.get(article_url, timeout=HTTP_TIMEOUT, allow_redirects=True)
            response.raise_for_status()

        return _extract_text(response.text)
    except Exception:
        return ""
