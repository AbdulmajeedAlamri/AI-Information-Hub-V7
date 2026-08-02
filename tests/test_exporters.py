from io import BytesIO
import unittest

from PIL import Image

from utils.exporters import make_docx, make_image, make_pdf


ARABIC_ANALYSIS = {
    "headline": "إطلاق منصة تقنية جديدة في المملكة العربية السعودية",
    "summary": "أعلنت الشركة إطلاق منصة رقمية جديدة. تهدف المنصة إلى تحسين تجربة المستخدم ودعم التحول الرقمي.",
    "sentiment": "إيجابي",
    "category": "تقنية",
    "importance": "مرتفعة",
    "confidence": "مرتفعة",
    "impact": "قد تسهم المنصة في رفع الكفاءة وتحسين الوصول إلى الخدمات الرقمية.",
    "key_takeaways": ["إطلاق منصة جديدة", "دعم التحول الرقمي", "تحسين تجربة المستخدم"],
    "key_entities": ["الشركة", "المملكة العربية السعودية"],
    "risks_watchlist": "تحتاج مؤشرات الأداء إلى متابعة بعد الإطلاق.",
}

ENGLISH_ANALYSIS = {
    "headline": "Championship won, standard unchanged for Indiana football",
    "summary": "The team won the championship. The program will keep the same performance standards.",
    "sentiment": "Neutral",
    "category": "General News",
    "importance": "Medium",
    "confidence": "Medium",
    "impact": "The story may affect the mentioned organizations or sectors.",
    "key_takeaways": ["The championship was won.", "The standard remains unchanged."],
    "key_entities": ["Indiana football", "The Hoosier Network"],
    "risks_watchlist": "Some details may be incomplete.",
}


class ExporterTests(unittest.TestCase):
    def test_pdf_headers_are_valid_for_both_languages(self):
        for analysis in (ARABIC_ANALYSIS, ENGLISH_ANALYSIS):
            with self.subTest(headline=analysis["headline"]):
                payload = make_pdf(analysis)
                self.assertTrue(payload.startswith(b"%PDF"))
                self.assertGreater(len(payload), 20_000)

    def test_png_is_valid_and_contains_complete_canvas(self):
        payload = make_image(ARABIC_ANALYSIS)
        image = Image.open(BytesIO(payload))
        self.assertEqual(image.format, "PNG")
        self.assertEqual(image.width, 1654)
        self.assertGreaterEqual(image.height, 2339)

    def test_docx_is_valid_zip_container(self):
        payload = make_docx(ENGLISH_ANALYSIS)
        self.assertTrue(payload.startswith(b"PK"))

    def test_report_uses_only_the_three_requested_analysis_sections(self):
        from utils.exporters import analysis_text
        text = analysis_text(ARABIC_ANALYSIS)
        self.assertIn("عنوان الخبر", text)
        self.assertIn("ملخص الخبر", text)
        self.assertIn("أهم النقاط", text)
        self.assertNotIn("المشاعر", text)
        self.assertNotIn("تحليل التأثير", text)
        self.assertNotIn("المخاطر والمتابعة", text)


if __name__ == "__main__":
    unittest.main()



def test_text_and_json_exports() -> None:
    from utils.exporters import make_json, make_text
    import json

    sample = {
        "headline": "خبر تجريبي",
        "summary": "ملخص عربي English",
        "sentiment": "محايد",
        "category": "تقنية",
        "importance": "متوسط",
        "confidence": "مرتفع",
        "impact": "تأثير تجريبي",
        "key_takeaways": ["نقطة أولى"],
        "key_entities": ["جهة"],
        "risks_watchlist": "لا يوجد",
    }
    assert make_text(sample).startswith(b"\xef\xbb\xbf")
    payload = make_json(sample).decode("utf-8-sig")
    assert json.loads(payload)["headline"] == "خبر تجريبي"
