from pathlib import Path
import ast
import unittest


class SyntaxTests(unittest.TestCase):
    def test_all_python_files_parse(self):
        root = Path(__file__).resolve().parents[1]

        for path in root.rglob("*.py"):
            if "venv" in path.parts:
                continue

            with self.subTest(path=path):
                ast.parse(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
