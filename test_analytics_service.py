import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from services.analytics_service import record_article_read_event


class RecordArticleReadEventTest(unittest.TestCase):
    def test_record_event_writes_same_event_to_json_and_supabase(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            events_file = Path(temp_dir) / "events.json"

            with (
                patch("services.analytics_service.EVENTS_FILE", events_file),
                patch(
                    "services.analytics_service.save_event_to_supabase",
                    return_value=True,
                ) as save_supabase,
            ):
                mirrored = record_article_read_event(
                    news_id="00000000-0000-0000-0000-000000000001",
                    category="경제",
                    title="테스트 뉴스",
                    seconds=30,
                )

            with events_file.open("r", encoding="utf-8") as file:
                saved_event = json.load(file)[0]

            self.assertEqual(saved_event["event_type"], "article_read")
            self.assertEqual(saved_event["seconds"], 30)
            save_supabase.assert_called_once_with(saved_event)
            self.assertTrue(mirrored)


if __name__ == "__main__":
    unittest.main()
