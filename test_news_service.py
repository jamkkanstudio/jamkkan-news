import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from services.auth_service import AuthorizationError
from services.news_service import add_news, delete_news, update_news


class AddNewsTest(unittest.TestCase):
    def test_add_news_denies_write_before_loading_data(self) -> None:
        with (
            patch(
                "services.news_service.require_admin",
                side_effect=AuthorizationError,
            ),
            patch("services.news_service.load_news") as load_news,
        ):
            with self.assertRaises(AuthorizationError):
                add_news({})
        load_news.assert_not_called()

    def test_add_news_saves_same_news_to_json_and_supabase(self) -> None:
        news = {
            "title": "테스트 뉴스",
            "summary": "테스트 요약",
            "reason": "테스트 이유",
            "source": "테스트 출처",
            "url": "https://example.com/news",
            "category": "경제",
            "importance": 80,
            "published_at": "2026-07-15T09:00:00+09:00",
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            data_file = Path(temp_dir) / "news.json"

            with (
                patch("services.news_service.DATA_FILE", data_file),
                patch("services.news_service.require_admin"),
                patch(
                    "services.news_service.save_news_to_supabase",
                    return_value=True,
                ) as save_supabase,
            ):
                mirrored = add_news(news)

            with data_file.open("r", encoding="utf-8") as file:
                saved_news_list = json.load(file)

            self.assertEqual(len(saved_news_list), 1)
            self.assertEqual(
                saved_news_list[0]["created_at"],
                news["published_at"],
            )
            save_supabase.assert_called_once_with(saved_news_list[0])
            self.assertIs(mirrored, True)


class UpdateNewsTest(unittest.TestCase):
    def test_update_news_saves_same_news_to_json_and_supabase(self) -> None:
        original_news = {
            "id": "news-id",
            "title": "수정 전 제목",
            "summary": "수정 전 요약",
            "reason": "수정 전 이유",
            "source": "수정 전 출처",
            "url": "https://example.com/before",
            "category": "사회",
            "importance": 50,
            "created_at": "2026-07-15T00:00:00",
        }
        updated_data = {
            "title": "수정 후 제목",
            "summary": "수정 후 요약",
            "reason": "수정 후 이유",
            "source": "수정 후 출처",
            "url": "https://example.com/after",
            "category": "경제",
            "importance": 80,
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            data_file = Path(temp_dir) / "news.json"
            data_file.write_text(
                json.dumps([original_news], ensure_ascii=False),
                encoding="utf-8",
            )

            with (
                patch("services.news_service.DATA_FILE", data_file),
                patch("services.news_service.require_admin"),
                patch(
                    "services.news_service.save_news_to_supabase",
                    return_value=True,
                ) as save_supabase,
            ):
                mirrored = update_news("news-id", updated_data)

            with data_file.open("r", encoding="utf-8") as file:
                saved_news = json.load(file)[0]

            self.assertEqual(saved_news["id"], original_news["id"])
            self.assertEqual(saved_news["created_at"], original_news["created_at"])
            self.assertEqual(saved_news["title"], updated_data["title"])
            save_supabase.assert_called_once_with(saved_news)
            self.assertIs(mirrored, True)


class DeleteNewsTest(unittest.TestCase):
    def test_delete_news_removes_same_news_from_json_and_supabase(self) -> None:
        news_list = [
            {"id": "delete-id", "title": "삭제할 뉴스"},
            {"id": "keep-id", "title": "보존할 뉴스"},
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            data_file = Path(temp_dir) / "news.json"
            data_file.write_text(
                json.dumps(news_list, ensure_ascii=False),
                encoding="utf-8",
            )

            with (
                patch("services.news_service.DATA_FILE", data_file),
                patch("services.news_service.require_admin"),
                patch(
                    "services.news_service.delete_news_from_supabase",
                    return_value=True,
                ) as delete_supabase,
            ):
                mirrored = delete_news("delete-id")

            with data_file.open("r", encoding="utf-8") as file:
                saved_news_list = json.load(file)

            self.assertEqual(saved_news_list, [news_list[1]])
            delete_supabase.assert_called_once_with("delete-id")
            self.assertIs(mirrored, True)

    def test_delete_news_does_not_call_supabase_when_news_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            data_file = Path(temp_dir) / "news.json"
            data_file.write_text("[]", encoding="utf-8")

            with (
                patch("services.news_service.DATA_FILE", data_file),
                patch("services.news_service.require_admin"),
                patch(
                    "services.news_service.delete_news_from_supabase"
                ) as delete_supabase,
            ):
                result = delete_news("missing-id")

            self.assertIsNone(result)
            delete_supabase.assert_not_called()


if __name__ == "__main__":
    unittest.main()
