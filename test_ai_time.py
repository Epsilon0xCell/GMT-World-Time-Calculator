import datetime
import subprocess
import sys
import unittest

from ai_time import CITY_OFFSETS, time_for_city

UTC = datetime.timezone.utc


class TimeForCityTests(unittest.TestCase):
    def test_tokyo_offset(self):
        now = datetime.datetime(2026, 1, 1, 1, 10, 5, tzinfo=UTC)
        self.assertEqual(time_for_city("Tokyo", now), ("Tokyo", 10, 10, 5))

    def test_negative_wrap_is_previous_evening(self):
        now = datetime.datetime(2026, 1, 1, 1, 10, 5, tzinfo=UTC)
        self.assertEqual(time_for_city("Boston", now), ("Boston", 21, 10, 5))

    def test_kolkata_half_hour_carries(self):
        now = datetime.datetime(2026, 1, 1, 16, 45, 0, tzinfo=UTC)
        self.assertEqual(time_for_city("Kolkata", now), ("Kolkata", 22, 15, 0))

    def test_unknown_city_falls_back_to_gmt(self):
        now = datetime.datetime(2026, 1, 1, 3, 4, 5, tzinfo=UTC)
        self.assertEqual(time_for_city("Nowhere", now), ("GMT", 3, 4, 5))

    def test_every_table_entry_is_whole_or_half_hour(self):
        for name, (hours, minutes) in CITY_OFFSETS.items():
            self.assertIn(minutes, (0, 30), name)


class ScriptTests(unittest.TestCase):
    def test_lowercase_city_and_exit(self):
        out = subprocess.run(
            [sys.executable, "ai_time.py"],
            input="tokyo\nexit\n",
            capture_output=True,
            text=True,
        )
        self.assertEqual(out.returncode, 0)
        self.assertIn("Tokyo", out.stdout)

    def test_eof_ends_cleanly(self):
        out = subprocess.run(
            [sys.executable, "ai_time.py"], input="", capture_output=True, text=True
        )
        self.assertEqual(out.returncode, 0)
        self.assertNotIn("Traceback", out.stderr)


if __name__ == "__main__":
    unittest.main()
