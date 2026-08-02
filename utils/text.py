from __future__ import annotations

import html
import re


CJK_PATTERN = re.compile(
    r"[\u3400-\u4DBF\u4E00-\u9FFF"
    r"\U00020000-\U0002FA1F"
    r"\u3040-\u30FF\uAC00-\uD7AF]+"
)

ARABIC_REPLACEMENTS = {
    "policymakers": "صنّاع السياسات",
    "economy": "الاقتصاد",
    "economic": "اقتصادي",
    "investors": "المستثمرون",
    "markets": "الأسواق",
    "growth": "النمو",
    "inflation": "التضخم",
    "government": "الحكومة",
    "companies": "الشركات",
    "technology": "التقنية",
    "global": "عالمي",
    "international": "دولي",
    "trade": "التجارة",
    "finance": "التمويل",
    "risk": "المخاطر",
    "risks": "المخاطر",
    "analysis": "التحليل",
}

WHITELIST = {
    "AI","OpenAI","Reuters","Bloomberg","Tesla","Google",
    "Microsoft","Apple","Meta","NVIDIA","NASA","NATO",
    "EU","UN","USA","UK","GDP","CEO","USD","EUR",
}


def clean_generated_text(value: object, language: str = "ar") -> str:
    text = CJK_PATTERN.sub("", str(value or ""))
    text = re.sub(r"\b(?=\w*\d)(?=\w*[A-Za-z])\w+\b", "", text)

    if language == "ar":
        for english, arabic in ARABIC_REPLACEMENTS.items():
            text = re.sub(
                rf"\b{re.escape(english)}\b",
                arabic,
                text,
                flags=re.IGNORECASE,
            )

        def remove_stray(match: re.Match[str]) -> str:
            token = match.group(0)
            if token in WHITELIST or token.isupper() or token[:1].isupper():
                return token
            return ""

        text = re.sub(
            r"\b[A-Za-z][A-Za-z\-]{1,}\b",
            remove_stray,
            text,
        )

    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\s+([،,.!?؟:;])", r"\1", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip(" -–—،,.;:")


def has_mixed_language(value: object, language: str) -> bool:
    text = str(value or "")
    if CJK_PATTERN.search(text):
        return True

    if language == "ar":
        for match in re.finditer(r"\b[a-z][a-z\-]{2,}\b", text):
            if match.group(0) not in WHITELIST:
                return True

    return False


def safe_text(value: object, language: str = "ar") -> str:
    return html.escape(clean_generated_text(value, language))


def safe_plain(value: object) -> str:
    return html.escape(str(value or ""))
