import json
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

from services.growth_service import record_article_read


class RecordArticleReadTest(unittest.TestCase):
    def test_record_article_read_writes_json_then_supabase(self) -> None:
        today = date.today().isoformat()

        with tempfile.TemporaryDirectory() as temp_dir:
            growth_file = Path(temp_dir) / "growth.json"

            with (
                patch("services.growth_service.GROWTH_FILE", growth_file),
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


if __name__ == "__main__":
    unittest.main()
