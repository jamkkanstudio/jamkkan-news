import unittest
from datetime import date
from unittest.mock import patch

from services.analytics_service import get_current_week_events


class CurrentWeekEventsTest(unittest.TestCase):
    def test_week_period_uses_kst_date_for_utc_event(self) -> None:
        events = [
            {
                "event_type": "article_read",
                "created_at": "2026-07-14T15:30:00+00:00",
            },
            {
                "event_type": "article_read",
                "created_at": "2026-07-12T14:59:59+00:00",
            },
        ]

        with (
            patch(
                "services.analytics_service.today_kst",
                return_value=date(2026, 7, 15),
            ),
            patch(
                "services.analytics_service.get_article_read_events",
                return_value=events,
            ),
        ):
            weekly_events = get_current_week_events()

        self.assertEqual(weekly_events, [events[0]])


if __name__ == "__main__":
    unittest.main()
