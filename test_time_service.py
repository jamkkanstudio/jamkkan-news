import unittest
from datetime import date, datetime, timezone
from unittest.mock import patch

from services.time_service import (
    KST,
    current_week_dates,
    datetime_to_kst_date,
    today_kst,
)


class FrozenDateTime(datetime):
    @classmethod
    def now(cls, tz=None):
        instant = cls(2026, 7, 14, 15, 30, tzinfo=timezone.utc)
        return instant.astimezone(tz) if tz else instant.replace(tzinfo=None)


class KstTimeTest(unittest.TestCase):
    def test_today_kst_uses_korean_date_across_utc_boundary(self) -> None:
        with patch("services.time_service.datetime", FrozenDateTime):
            self.assertEqual(today_kst(), date(2026, 7, 15))

    def test_current_week_dates_uses_kst_today(self) -> None:
        with patch(
            "services.time_service.today_kst",
            return_value=date(2026, 7, 15),
        ):
            days = current_week_dates()

        self.assertEqual(days[0], date(2026, 7, 13))
        self.assertEqual(days[-1], date(2026, 7, 19))

    def test_utc_event_is_grouped_by_kst_date(self) -> None:
        instant = datetime(2026, 7, 14, 15, 30, tzinfo=timezone.utc)
        self.assertEqual(datetime_to_kst_date(instant), date(2026, 7, 15))

    def test_naive_legacy_event_is_interpreted_as_kst(self) -> None:
        instant = datetime(2026, 7, 15, 0, 30)
        self.assertEqual(datetime_to_kst_date(instant), date(2026, 7, 15))
        self.assertEqual(KST.key, "Asia/Seoul")


if __name__ == "__main__":
    unittest.main()
