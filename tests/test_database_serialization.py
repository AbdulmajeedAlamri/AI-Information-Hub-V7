from datetime import date, datetime
import unittest

import json


def _json_safe(value):
    return json.loads(json.dumps(value, default=lambda item: item.isoformat()))


class DatabaseSerializationTests(unittest.TestCase):
    def test_nested_dates_are_serializable(self):
        value = {
            "published": datetime(2026, 7, 30, 21, 30),
            "days": [date(2026, 7, 30)],
        }
        result = _json_safe(value)
        self.assertEqual(
            result["published"],
            "2026-07-30T21:30:00",
        )
        self.assertEqual(
            result["days"][0],
            "2026-07-30",
        )


if __name__ == "__main__":
    unittest.main()
