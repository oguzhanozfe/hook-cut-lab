import json
from pathlib import Path
import unittest

from project import analyze


def example():
    return json.loads(Path(__file__).with_name("example.json").read_text(encoding="utf-8"))


class ProjectTests(unittest.TestCase):
    def test_window_clips_and_merges_overlaps(self):
        result = analyze(example())
        self.assertEqual(result["rows"][0]["Product visible (s)"], 2.9)
        self.assertEqual(result["rows"][1]["First proof (s)"], "Absent")
        self.assertEqual(result["metrics"]["With early proof"], 2)

    def test_window_end_is_exclusive(self):
        result = analyze({"window_seconds": 2, "variants": [{"name": "Late",
                          "beats": [{"start": 2, "end": 3, "features": ["proof"]}]}]})
        self.assertEqual(result["metrics"]["With early proof"], 0)

    def test_unknown_tag(self):
        data = example()
        data["variants"][0]["beats"][0]["features"] = ["brandish"]
        with self.assertRaises(ValueError):
            analyze(data)

    def test_bad_window(self):
        data = example()
        data["window_seconds"] = True
        with self.assertRaises(ValueError):
            analyze(data)


if __name__ == "__main__":
    unittest.main()
