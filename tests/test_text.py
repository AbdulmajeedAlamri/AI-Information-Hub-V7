import unittest

from utils.text import clean_generated_text


class TextTests(unittest.TestCase):
    def test_cjk_removed(self):
        self.assertNotIn("中文", clean_generated_text("خبر 中文 مهم", "ar"))

    def test_common_term_translated(self):
        self.assertIn("الاقتصاد", clean_generated_text("economy", "ar"))


if __name__ == "__main__":
    unittest.main()
