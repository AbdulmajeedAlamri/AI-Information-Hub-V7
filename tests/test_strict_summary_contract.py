from services.ai_service import _fallback, _normalise


def test_fallback_always_returns_five_to_eight_summary_lines():
    result = _fallback(
        title="إطلاق مبادرة تقنية جديدة",
        description="أُعلن عن مبادرة تقنية جديدة لدعم التحول الرقمي.",
        article_text="",
        language="ar",
    )
    assert 5 <= len(result["summary_lines"]) <= 8
    assert "\n" not in result["summary"]
    assert result["summary"] == " ".join(result["summary_lines"])


def test_fallback_always_returns_at_least_three_takeaways():
    result = _fallback(
        title="خبر قصير",
        description="وصف قصير.",
        article_text="",
        language="ar",
    )
    assert 3 <= len(result["key_takeaways"]) <= 6


def test_normalise_rejectable_shape_is_visible_to_caller():
    result = _normalise(
        {
            "headline": "عنوان",
            "summary": "جملة واحدة فقط.",
            "key_takeaways": ["نقطة واحدة"],
        },
        "ar",
    )
    assert len(result["summary_lines"]) == 1
    assert len(result["key_takeaways"]) == 1
