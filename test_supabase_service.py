import unittest
from unittest.mock import MagicMock, patch

from services.supabase_service import (
    delete_news,
    get_setting,
    replace_interests,
    upsert_growth_daily,
    upsert_setting,
    upsert_news,
)


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


class ReplaceInterestsTest(unittest.TestCase):
    def test_replace_interests_replaces_all_rows(self) -> None:
        client = MagicMock()
        table = client.table.return_value

        with patch(
            "services.supabase_service.get_supabase_client",
            return_value=client,
        ):
            result = replace_interests(["경제", "AI"])

        client.table.assert_called_once_with("interests")
        table.delete.assert_called_once_with()
        table.delete.return_value.neq.assert_called_once_with("id", 0)
        table.insert.assert_called_once_with(
            [{"interest": "경제"}, {"interest": "AI"}]
        )
        self.assertTrue(result)

    def test_replace_interests_supports_empty_list(self) -> None:
        client = MagicMock()
        table = client.table.return_value

        with patch(
            "services.supabase_service.get_supabase_client",
            return_value=client,
        ):
            result = replace_interests([])

        (
            table.delete.return_value.neq.return_value.execute
            .assert_called_once_with()
        )
        table.insert.assert_not_called()
        self.assertTrue(result)


class UpsertSettingTest(unittest.TestCase):
    def test_upsert_setting_writes_key_and_json_value(self) -> None:
        client = MagicMock()

        with patch(
            "services.supabase_service.get_supabase_client",
            return_value=client,
        ):
            result = upsert_setting("daily_goal_seconds", 300)

        client.table.assert_called_once_with("settings")
        client.table.return_value.upsert.assert_called_once_with(
            {
                "setting_key": "daily_goal_seconds",
                "setting_value": 300,
            }
        )
        self.assertTrue(result)

    def test_get_setting_reads_json_value(self) -> None:
        client = MagicMock()
        query = (
            client.table.return_value.select.return_value.eq.return_value
            .limit.return_value
        )
        query.execute.return_value.data = [
            {"setting_value": {"status": "success"}}
        ]

        with patch(
            "services.supabase_service.get_supabase_client",
            return_value=client,
        ):
            value = get_setting("news_collection_status")

        self.assertEqual(value, {"status": "success"})


class UpsertGrowthDailyTest(unittest.TestCase):
    def test_upsert_growth_daily_writes_daily_record(self) -> None:
        growth_day = {
            "activity_date": "2026-07-15",
            "articles": 2,
            "seconds": 60,
            "read_news_ids": ["00000000-0000-0000-0000-000000000001"],
        }
        client = MagicMock()

        with patch(
            "services.supabase_service.get_supabase_client",
            return_value=client,
        ):
            result = upsert_growth_daily(growth_day)

        client.table.assert_called_once_with("growth_daily")
        client.table.return_value.upsert.assert_called_once_with(growth_day)
        self.assertTrue(result)

if __name__ == "__main__":
    unittest.main()
