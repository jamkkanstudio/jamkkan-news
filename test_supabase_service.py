import unittest
from unittest.mock import MagicMock, patch

from services.supabase_service import delete_news, upsert_news


class UpsertNewsTest(unittest.TestCase):
    def test_upsert_news_writes_to_news_table(self) -> None:
        news = {"id": "news-id", "title": "테스트 뉴스"}
        client = MagicMock()

        with patch(
            "services.supabase_service.get_supabase_client",
            return_value=client,
        ):
            result = upsert_news(news)

        client.table.assert_called_once_with("news")
        client.table.return_value.upsert.assert_called_once_with(news)
        client.table.return_value.upsert.return_value.execute.assert_called_once_with()
        self.assertTrue(result)

    def test_upsert_news_returns_false_when_supabase_fails(self) -> None:
        client = MagicMock()
        client.table.return_value.upsert.return_value.execute.side_effect = (
            RuntimeError("Supabase unavailable")
        )

        with (
            patch(
                "services.supabase_service.get_supabase_client",
                return_value=client,
            ),
            patch("services.supabase_service.logger.exception") as log_error,
        ):
            result = upsert_news({"id": "news-id"})

        self.assertFalse(result)
        log_error.assert_called_once()


class DeleteNewsTest(unittest.TestCase):
    def test_delete_news_deletes_matching_id_from_news_table(self) -> None:
        client = MagicMock()

        with patch(
            "services.supabase_service.get_supabase_client",
            return_value=client,
        ):
            result = delete_news("news-id")

        client.table.assert_called_once_with("news")
        client.table.return_value.delete.assert_called_once_with()
        client.table.return_value.delete.return_value.eq.assert_called_once_with(
            "id",
            "news-id",
        )
        (
            client.table.return_value.delete.return_value.eq.return_value
            .execute.assert_called_once_with()
        )
        self.assertTrue(result)

    def test_delete_news_returns_false_when_supabase_fails(self) -> None:
        client = MagicMock()
        (
            client.table.return_value.delete.return_value.eq.return_value
            .execute.side_effect
        ) = RuntimeError("Supabase unavailable")

        with (
            patch(
                "services.supabase_service.get_supabase_client",
                return_value=client,
            ),
            patch("services.supabase_service.logger.exception") as log_error,
        ):
            result = delete_news("news-id")

        self.assertFalse(result)
        log_error.assert_called_once()


if __name__ == "__main__":
    unittest.main()
