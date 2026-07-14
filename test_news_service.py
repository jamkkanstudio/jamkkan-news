import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from services.news_service import add_news


class AddNewsTest(unittest.TestCase):
    def test_add_news_saves_same_news_to_json_and_supabase(self) -> None:
        news = {
            "title": "테스트 뉴스",
            "summary": "테스트 요약",
            "reason": "테스트 이유",
            "source": "테스트 출처",
            "url": "https://example.com/news",
            "category": "경제",
            "importance": 80,
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            data_file = Path(temp_dir) / "news.json"

            with (
                patch("services.news_service.DATA_FILE", data_file),
                patch(
                    "services.news_service.save_news_to_supabase",
                    return_value=True,
                ) as save_supabase,
            ):
                mirrored = add_news(news)

            with data_file.open("r", encoding="utf-8") as file:
                saved_news_list = json.load(file)

            self.assertEqual(len(saved_news_list), 1)
            save_supabase.assert_called_once_with(saved_news_list[0])
            self.assertIs(mirrored, True)


if __name__ == "__main__":
    unittest.main()
