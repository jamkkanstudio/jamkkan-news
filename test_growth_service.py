import json
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

from services.growth_service import get_today_read_news_ids, record_article_read


class RecordArticleReadTest(unittest.TestCase):
    def test_today_read_ids_use_current_legacy_day_only(self) -> None:
        growth = {
            "daily": {
                "2026-07-14": {"read_news_ids": ["old-news"]},
                "2026-07-15": {
                    "read_news_ids": ["today-news", "today-news"]
                },
            }
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            growth_file = Path(temp_dir) / "growth.json"
            growth_file.write_text(json.dumps(growth), encoding="utf-8")
            with (
                patch("services.growth_service.GROWTH_FILE", growth_file),
                patch(
                    "services.growth_service.today_kst",
                    return_value=date(2026, 7, 15),
                ),
            ):
                read_ids = get_today_read_news_ids()

        self.assertEqual(read_ids, {"today-news"})

    def test_record_article_read_writes_json_then_supabase(self) -> None:
        today = "2026-07-15"

        with tempfile.TemporaryDirectory() as temp_dir:
            growth_file = Path(temp_dir) / "growth.json"

            with (
                patch("services.growth_service.GROWTH_FILE", growth_file),
                patch(
                    "services.growth_service.today_kst",
                    return_value=date(2026, 7, 15),
                ),
                patch(
                    "services.growth_service.save_growth_to_supabase",
                    return_value=True,
                ) as save_supabase,
            ):
                mirrored = record_article_read("news-id", seconds=30)

            with growth_file.open("r", encoding="utf-8") as file:
                saved_growth = json.load(file)

            self.assertEqual(saved_growth["total_articles"], 1)
            self.assertEqual(saved_growth["total_seconds"], 30)
            save_supabase.assert_called_once_with(
                {
                    "activity_date": today,
                    "articles": 1,
                    "seconds": 30,
                    "read_news_ids": ["news-id"],
                }
            )
            self.assertTrue(mirrored)

    def test_record_article_read_returns_none_when_supabase_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            growth_file = Path(temp_dir) / "growth.json"

            with (
                patch("services.growth_service.GROWTH_FILE", growth_file),
                patch(
                    "services.growth_service.save_growth_to_supabase",
                    return_value=False,
                ),
            ):
                result = record_article_read("news-id")

            self.assertIsNone(result)
            self.assertTrue(growth_file.exists())

    def test_record_article_read_continues_streak_on_kst_next_day(self) -> None:
        existing = {
            "total_articles": 1,
            "total_seconds": 30,
            "current_streak": 1,
            "last_active_date": "2026-07-14",
            "daily": {
                "2026-07-14": {
                    "articles": 1,
                    "seconds": 30,
                    "read_news_ids": ["yesterday-news"],
                }
            },
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            growth_file = Path(temp_dir) / "growth.json"
            growth_file.write_text(
                json.dumps(existing),
                encoding="utf-8",
            )

            with (
                patch("services.growth_service.GROWTH_FILE", growth_file),
                patch(
                    "services.growth_service.today_kst",
                    return_value=date(2026, 7, 15),
                ),
                patch(
                    "services.growth_service.save_growth_to_supabase",
                    return_value=True,
                ),
            ):
                record_article_read("today-news")

            saved_growth = json.loads(
                growth_file.read_text(encoding="utf-8")
            )

        self.assertEqual(saved_growth["current_streak"], 2)
        self.assertEqual(saved_growth["last_active_date"], "2026-07-15")


if __name__ == "__main__":
    unittest.main()
