from __future__ import annotations

import json
import re

from config import MAX_ARTICLE_CHARS, OLLAMA_MODEL
from utils.text import clean_generated_text, has_mixed_language
from services.translation_service import translate_items, translate_text
from services.llm_service import AIUnavailable, generate_chat


REQUIRED_KEYS = {"headline", "summary", "key_takeaways"}


def _extract_json(value: str) -> dict | None:
    text = str(value or "").strip()
    text = re.sub(r"^```(?:json)?", "", text, flags=re.IGNORECASE)
    text = re.sub(r"```$", "", text).strip()

    try:
        parsed = json.loads(text)
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", text, flags=re.DOTALL)

    if not match:
        return None

    try:
        parsed = json.loads(match.group(0))
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        return None



def _normalise_list(value: object, language: str) -> list[str]:
    if isinstance(value, list):
        items = value
    elif isinstance(value, str):
        items = re.split(r"[\n•]+", value)
    else:
        items = []

    output: list[str] = []
    seen: set[str] = set()

    for item in items:
        cleaned = clean_generated_text(item, language)
        key = cleaned.casefold()
        if cleaned and key not in seen:
            seen.add(key)
            output.append(cleaned)

    return output


def _split_sentences(value: object, language: str) -> list[str]:
    cleaned = clean_generated_text(value, language)
    if not cleaned:
        return []

    parts = re.split(r"(?:\r?\n)+|(?<=[.!؟])\s+", cleaned)
    output: list[str] = []
    seen: set[str] = set()

    for part in parts:
        sentence = clean_generated_text(part, language)
        key = sentence.casefold()
        if len(sentence) >= 12 and key not in seen:
            seen.add(key)
            output.append(sentence)

    return output


def _normalise(data: dict, language: str) -> dict:
    summary_lines = _split_sentences(data.get("summary", ""), language)[:8]
    takeaways = _normalise_list(data.get("key_takeaways", []), language)[:6]

    return {
        "headline": clean_generated_text(data.get("headline", ""), language),
        "summary": " ".join(summary_lines),
        "summary_lines": summary_lines,
        "key_takeaways": takeaways,
    }


def _grounded_candidates(
    title: str,
    description: str,
    article_text: str,
    language: str,
) -> list[str]:
    translated_article = translate_text(str(article_text or "")[:7000], language)
    translated_description = translate_text(str(description or "")[:1800], language)
    translated_title = translate_text(str(title or "")[:500], language)

    candidates: list[str] = []
    seen: set[str] = set()

    for source in (translated_article, translated_description, translated_title):
        for sentence in _split_sentences(source, language):
            key = sentence.casefold()
            if key not in seen:
                seen.add(key)
                candidates.append(sentence)

    return candidates


def _pad_grounded_lines(
    lines: list[str],
    title: str,
    description: str,
    article_text: str,
    language: str,
) -> list[str]:
    output = list(lines[:8])

    if len(output) >= 5:
        return output

    has_article = bool(str(article_text or "").strip())
    has_description = bool(str(description or "").strip())

    if language == "ar":
        notices = [
            "يعرض المصدر المتاح معلومات محدودة، لذلك اقتصر الملخص على التفاصيل المنشورة دون إضافة افتراضات.",
            "لم يتضمن النص المتاح تفاصيل إضافية كافية حول خلفية الحدث أو تسلسله الزمني.",
            "لم يذكر المصدر المتاح أرقامًا أو تصريحات إضافية يمكن تضمينها بثقة.",
            "تحتاج التفاصيل الكاملة إلى الرجوع إلى الصفحة الأصلية للخبر عند توفرها.",
            "تم الحفاظ على صياغة محايدة وعدم اختلاق معلومات غير موجودة في المصدر.",
        ]
        if has_article:
            notices[0] = "اعتمد الملخص على النص المستخرج من صفحة الخبر مع حذف التكرار والمحتوى غير المرتبط."
        elif has_description:
            notices[0] = "تعذر استخراج نص المقال الكامل، لذلك اعتمد الملخص على عنوان الخبر ووصفه المنشور."
    else:
        notices = [
            "The available source contains limited detail, so the summary stays within the published information.",
            "The available text does not provide enough additional background or a complete event timeline.",
            "No additional figures or attributable statements were available to include with confidence.",
            "Complete details require reviewing the original article page when it is accessible.",
            "The wording remains neutral and does not introduce facts that are absent from the source.",
        ]
        if has_article:
            notices[0] = "The summary is based on text extracted from the article page after removing repetition and unrelated content."
        elif has_description:
            notices[0] = "The full article text could not be extracted, so the summary relies on the published title and description."

    for notice in notices:
        if len(output) >= 5:
            break
        if notice.casefold() not in {item.casefold() for item in output}:
            output.append(notice)

    return output[:8]


def _fallback(
    title: str,
    description: str,
    article_text: str,
    language: str,
) -> dict:
    headline = clean_generated_text(translate_text(str(title or ""), language), language)
    candidates = _grounded_candidates(title, description, article_text, language)
    summary_lines = _pad_grounded_lines(
        candidates[:8],
        title=title,
        description=description,
        article_text=article_text,
        language=language,
    )

    # Fallback mode has no LLM. Keep takeaways grounded and avoid pretending that
    # copied article sentences are "analysis". We extract distinct factual sentences
    # and label their role so the UI remains useful without inventing conclusions.
    factual = candidates[:5]
    takeaways: list[str] = []
    if factual:
        if language == "ar":
            labels = ["التطور الرئيسي", "السياق المهم", "الجهة أو الطرف المرتبط", "تفصيل يستحق المتابعة", "معلومة إضافية"]
        else:
            labels = ["Main development", "Important context", "Relevant party", "Detail to watch", "Additional fact"]
        for label, sentence in zip(labels, factual):
            takeaways.append(f"{label}: {sentence}")

    if len(takeaways) < 3:
        if language == "ar":
            supplements = [
                "المصدر المنشور لا يحتوي تفاصيل كافية لاستخراج نقطة تحليلية إضافية بثقة.",
                "لا توجد في النص المتاح معلومات كافية لتقدير أثر أوسع دون افتراضات.",
                "يلزم الرجوع إلى المصدر الأصلي عند توفر نص كامل قبل استخلاص استنتاجات إضافية.",
            ]
        else:
            supplements = [
                "The published source does not contain enough detail for another confident analytical takeaway.",
                "The available text is insufficient to estimate broader impact without assumptions.",
                "The full original source is needed before drawing additional conclusions.",
            ]
        for item in supplements:
            if len(takeaways) >= 3:
                break
            takeaways.append(item)

    if language == "ar":
        headline = headline or "عنوان الخبر غير متاح"
    else:
        headline = headline or "News title unavailable"

    return {
        "_language": language,
        "headline": headline,
        "summary": " ".join(summary_lines),
        "summary_lines": summary_lines,
        "key_takeaways": takeaways[:6],
    }


def _build_prompt(
    title: str,
    description: str,
    source: str,
    language: str,
    retry: bool,
) -> str:
    if language == "ar":
        language_rule = """
اكتب جميع القيم باللغة العربية الفصحى فقط.
لا تستخدم أي كلمة إنجليزية عامة داخل الجمل.
ترجم المصطلحات العامة إلى العربية.
يُسمح فقط بأسماء الشركات والأشخاص والاختصارات العالمية الضرورية.
يُمنع استخدام الصينية أو اليابانية أو الكورية.
"""
    else:
        language_rule = """
Write every value in professional English only.
Do not use Arabic, Chinese, Japanese, or Korean sentences.
Keep only proper names in their standard spelling.
"""

    retry_rule = (
        "The previous response mixed languages. Rewrite every field from scratch."
        if retry
        else ""
    )

    return f"""
You are a professional news intelligence analyst.

{language_rule}
{retry_rule}

Return valid JSON only with these exact keys:
headline, summary, key_takeaways.

Rules:
- headline: one clear, factual news headline.
- summary: 5 to 8 complete, informative sentences. Cover what happened, the main parties, relevant place/time when supported, and the most important context. Avoid repetition and filler.
- key_takeaways: 3 to 5 concise ANALYTICAL takeaways, not copied sentences. Each item should explain one of: the significance of the development, the affected parties, likely implications supported by the article, or what deserves follow-up. Do not repeat the summary or merely restate the headline.
- Do not invent facts. If the source lacks a detail, omit that detail rather than guessing.
- No Markdown.
- Do not output text outside JSON.

Title:
{title}

Description:
{description}

Article:
{source}
""".strip()


def summarise(
    title: str,
    description: str,
    article_text: str,
    language: str,
) -> dict:
    source = clean_generated_text(
        article_text or description or title,
        language,
    )[:MAX_ARTICLE_CHARS]

    try:
        for attempt in range(2):
            content = generate_chat(
                [
                    {
                        "role": "system",
                        "content": (
                            "Use exactly one requested language. "
                            "Return valid JSON only."
                        ),
                    },
                    {
                        "role": "user",
                        "content": _build_prompt(
                            title=title,
                            description=description,
                            source=source,
                            language=language,
                            retry=attempt == 1,
                        ),
                    },
                ],
                temperature=0.0,
                max_tokens=1500,
                json_mode=True,
            )

            parsed = _extract_json(content)

            if not parsed:
                continue

            if not REQUIRED_KEYS.issubset(parsed):
                continue

            cleaned = _normalise(
                parsed,
                language,
            )

            combined = json.dumps(
                cleaned,
                ensure_ascii=False,
            )

            if has_mixed_language(
                combined,
                language,
            ):
                continue

            if len(cleaned.get("summary_lines", [])) < 5:
                continue
            if len(cleaned.get("key_takeaways", [])) < 3:
                continue

            cleaned["_language"] = language
            return cleaned

    except Exception as error:
        print("=" * 60)
        print("OLLAMA ERROR")
        print(repr(error))
        print("=" * 60)

    return _fallback(
        title=title,
        description=description,
        article_text=article_text,
        language=language,
    )


def answer_question(
    question: str,
    title: str,
    description: str,
    article_text: str,
    history: list[dict],
    language: str,
) -> str:
    source = clean_generated_text(
        article_text or description or title,
        language,
    )[:MAX_ARTICLE_CHARS]

    history_text = "\n".join(
        f'{message.get("role")}: {message.get("content")}'
        for message in history[-8:]
    )

    language_rule = (
        "أجب بالعربية الفصحى فقط، ولا تستخدم كلمات إنجليزية عامة."
        if language == "ar"
        else "Answer in professional English only."
    )

    prompt = f"""
Answer only from the article below.

{language_rule}
If the answer is unavailable, say so clearly.
Do not invent facts.

Title:
{title}

Description:
{description}

Article:
{source}

History:
{history_text}

Question:
{question}
""".strip()

    try:
        for _ in range(2):
            content = generate_chat(
                [
                    {
                        "role": "system",
                        "content": (
                            "Answer only from the supplied article "
                            "and use exactly one requested language."
                        ),
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                temperature=0.0,
                max_tokens=600,
            )

            answer = clean_generated_text(content, language)

            if (
                answer
                and not has_mixed_language(
                    answer,
                    language,
                )
            ):
                return answer

    except Exception:
        pass

    return (
        source[:900]
        if source
        else (
            "لا تتوفر معلومات كافية للإجابة."
            if language == "ar"
            else "Not enough information is available."
        )
    )
