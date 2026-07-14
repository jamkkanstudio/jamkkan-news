import unittest
from unittest.mock import MagicMock, patch

from services.user_data_service import (
    InvalidOwnerIdError,
    insert_user_event,
    load_user_growth_daily,
    load_user_interests,
    replace_user_interests,
    upsert_user_growth_daily,
    upsert_user_setting,
)


OWNER_ID = "usr_" + "a" * 64


class UserDataServiceTest(unittest.TestCase):
    def test_invalid_owner_is_rejected_before_query(self) -> None:
        with patch("services.user_data_service.get_user_data_client") as client:
            with self.assertRaises(InvalidOwnerIdError):
                load_user_interests("raw-google-subject")
        client.assert_not_called()

    def test_interests_read_is_owner_scoped_and_ordered(self) -> None:
        client = MagicMock()
        query = client.table.return_value.select.return_value
        query.eq.return_value.order.return_value.execute.return_value.data = [
            {"interest": "AI", "position": 0},
            {"interest": "경제", "position": 1},
        ]

        with patch(
            "services.user_data_service.get_user_data_client",
            return_value=client,
        ):
            interests = load_user_interests(OWNER_ID)

        client.table.assert_called_once_with("user_interests")
        query.eq.assert_called_once_with("owner_id", OWNER_ID)
        query.eq.return_value.order.assert_called_once_with("position")
        self.assertEqual(interests, ["AI", "경제"])

    def test_interest_replace_uses_owner_scoped_atomic_function(self) -> None:
        client = MagicMock()

        with patch(
            "services.user_data_service.get_user_data_client",
            return_value=client,
        ):
            replace_user_interests(OWNER_ID, ["AI", "경제"])

        client.rpc.assert_called_once_with(
            "replace_user_interests",
            {
                "p_owner_id": OWNER_ID,
                "p_interests": ["AI", "경제"],
            },
        )
        client.rpc.return_value.execute.assert_called_once_with()

    def test_setting_upsert_uses_owner_composite_conflict_key(self) -> None:
        client = MagicMock()
        table = client.table.return_value

        with patch(
            "services.user_data_service.get_user_data_client",
            return_value=client,
        ):
            upsert_user_setting(OWNER_ID, "daily_goal_seconds", 300)

        table.upsert.assert_called_once_with(
            {
                "owner_id": OWNER_ID,
                "setting_key": "daily_goal_seconds",
                "setting_value": 300,
            },
            on_conflict="owner_id,setting_key",
        )

    def test_growth_read_and_write_are_owner_scoped(self) -> None:
        client = MagicMock()
        table = client.table.return_value
        query = table.select.return_value
        query.eq.return_value.order.return_value.execute.return_value.data = []
        growth_day = {
            "owner_id": "usr_" + "b" * 64,
            "activity_date": "2026-07-15",
            "articles": 2,
            "seconds": 60,
            "read_news_ids": ["news-id"],
        }

        with patch(
            "services.user_data_service.get_user_data_client",
            return_value=client,
        ):
            self.assertEqual(load_user_growth_daily(OWNER_ID), [])
            upsert_user_growth_daily(OWNER_ID, growth_day)

        query.eq.assert_called_once_with("owner_id", OWNER_ID)
        table.upsert.assert_called_once_with(
            {
                "owner_id": OWNER_ID,
                "activity_date": "2026-07-15",
                "articles": 2,
                "seconds": 60,
                "read_news_ids": ["news-id"],
            },
            on_conflict="owner_id,activity_date",
        )

    def test_event_payload_cannot_override_trusted_owner(self) -> None:
        client = MagicMock()
        table = client.table.return_value
        event = {
            "id": "00000000-0000-0000-0000-000000000001",
            "owner_id": "usr_" + "b" * 64,
            "event_type": "article_read",
            "news_id": "news-id",
            "category": "AI",
            "title": "테스트",
            "seconds": 30,
            "occurred_at": "2026-07-15T12:00:00+09:00",
        }

        with patch(
            "services.user_data_service.get_user_data_client",
            return_value=client,
        ):
            insert_user_event(OWNER_ID, event)

        payload = table.insert.call_args.args[0]
        self.assertEqual(payload["owner_id"], OWNER_ID)


if __name__ == "__main__":
    unittest.main()
