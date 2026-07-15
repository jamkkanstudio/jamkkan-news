import json
import tempfile
import unittest
from datetime import date, datetime
from pathlib import Path
from unittest.mock import patch

from services.analytics_service import (
    get_current_week_events,
    get_today_helpful_news_ids,
    record_article_helpful_event,
)
from services.time_service import KST


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

    def test_helpful_event_uses_minimum_legacy_payload(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            events_file = Path(temp_dir) / "events.json"
            with (
                patch("services.analytics_service.EVENTS_FILE", events_file),
                patch(
                    "services.analytics_service.now_kst",
                    return_value=datetime(2026, 7, 15, 12, 0, tzinfo=KST),
                ),
            ):
                record_article_helpful_event("news-id", "사회", "도움 기사")

            events = json.loads(events_file.read_text(encoding="utf-8"))

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["event_type"], "article_helpful")
        self.assertEqual(events[0]["news_id"], "news-id")
        self.assertEqual(events[0]["seconds"], 0)
        self.assertEqual(
            set(events[0]),
            {
                "id",
                "event_type",
                "news_id",
                "category",
                "title",
                "seconds",
                "created_at",
            },
        )

    def test_today_helpful_ids_ignore_old_and_completion_events(self) -> None:
        events = [
            {
                "event_type": "article_helpful",
                "news_id": "today-helpful",
                "created_at": "2026-07-15T08:00:00+09:00",
            },
            {
                "event_type": "article_helpful",
                "news_id": "old-helpful",
                "created_at": "2026-07-14T23:59:59+09:00",
            },
            {
                "event_type": "article_read",
                "news_id": "today-read",
                "created_at": "2026-07-15T09:00:00+09:00",
            },
        ]
        with (
            patch(
                "services.analytics_service.today_kst",
                return_value=date(2026, 7, 15),
            ),
            patch("services.analytics_service.load_events", return_value=events),
        ):
            helpful_ids = get_today_helpful_news_ids()

        self.assertEqual(helpful_ids, {"today-helpful"})


if __name__ == "__main__":
    unittest.main()
