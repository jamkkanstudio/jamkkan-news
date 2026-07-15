import tempfile
import unittest
from contextlib import ExitStack
from datetime import date, datetime, timezone
from pathlib import Path
from unittest.mock import patch

from services import analytics_service, growth_service, settings_service, user_service
from services.identity_service import DataScope
from services.user_data_service import UserDataConfigurationError


OWNER_A = "usr_" + "a" * 64
OWNER_B = "usr_" + "b" * 64


class PersonalDataRoutingTest(unittest.TestCase):
    def test_authenticated_backend_failure_does_not_read_legacy_interests(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            interest_file = Path(temp_dir) / "interest.json"
            interest_file.write_text(
                '{"interests": ["legacy-global"]}',
                encoding="utf-8",
            )
            with (
                patch(
                    "services.user_service.current_storage_scope",
                    return_value=DataScope(kind="user", owner_id=OWNER_A),
                ),
                patch("services.user_service.INTEREST_FILE", interest_file),
                patch(
                    "services.user_data_service.load_user_interests",
                    side_effect=UserDataConfigurationError("missing secret"),
                ),
            ):
                with self.assertRaises(UserDataConfigurationError):
                    user_service.load_interests()

    def test_two_owners_share_one_route_without_cross_read_or_write(self) -> None:
        active_scope = {"value": DataScope(kind="user", owner_id=OWNER_A)}
        interests: dict[str, list[str]] = {}
        settings: dict[str, dict] = {}
        growth: dict[str, dict[str, dict]] = {}
        events: dict[str, list[dict]] = {}

        def replace_interests(owner_id, selected):
            interests[owner_id] = list(selected)

        def upsert_setting(owner_id, key, value):
            settings.setdefault(owner_id, {})[key] = value

        def upsert_growth(owner_id, row):
            growth.setdefault(owner_id, {})[row["activity_date"]] = dict(row)

        def insert_event(owner_id, event):
            events.setdefault(owner_id, []).append(dict(event))

        with tempfile.TemporaryDirectory() as temp_dir, ExitStack() as stack:
            temp_path = Path(temp_dir)
            for module_name in (
                "user_service",
                "settings_service",
                "growth_service",
                "analytics_service",
            ):
                stack.enter_context(
                    patch(
                        f"services.{module_name}.current_storage_scope",
                        side_effect=lambda: active_scope["value"],
                    )
                )

            stack.enter_context(
                patch("services.user_service.INTEREST_FILE", temp_path / "interest.json")
            )
            stack.enter_context(
                patch("services.settings_service.SETTINGS_FILE", temp_path / "settings.json")
            )
            stack.enter_context(
                patch("services.growth_service.GROWTH_FILE", temp_path / "growth.json")
            )
            stack.enter_context(
                patch("services.analytics_service.EVENTS_FILE", temp_path / "events.json")
            )
            stack.enter_context(
                patch(
                    "services.user_data_service.replace_user_interests",
                    side_effect=replace_interests,
                )
            )
            stack.enter_context(
                patch(
                    "services.user_data_service.load_user_interests",
                    side_effect=lambda owner_id: interests.get(owner_id, []),
                )
            )
            stack.enter_context(
                patch(
                    "services.user_data_service.upsert_user_setting",
                    side_effect=upsert_setting,
                )
            )
            stack.enter_context(
                patch(
                    "services.user_data_service.load_user_settings",
                    side_effect=lambda owner_id: settings.get(owner_id, {}),
                )
            )
            stack.enter_context(
                patch(
                    "services.user_data_service.upsert_user_growth_daily",
                    side_effect=upsert_growth,
                )
            )
            stack.enter_context(
                patch(
                    "services.user_data_service.load_user_growth_daily",
                    side_effect=lambda owner_id: list(growth.get(owner_id, {}).values()),
                )
            )
            stack.enter_context(
                patch(
                    "services.user_data_service.insert_user_event",
                    side_effect=insert_event,
                )
            )
            stack.enter_context(
                patch(
                    "services.user_data_service.load_user_events",
                    side_effect=lambda owner_id: events.get(owner_id, []),
                )
            )
            stack.enter_context(
                patch(
                    "services.growth_service.today_kst",
                    return_value=date(2026, 7, 15),
                )
            )
            stack.enter_context(
                patch(
                    "services.analytics_service.now_kst",
                    return_value=datetime(
                        2026, 7, 15, 12, 0, tzinfo=timezone.utc
                    ),
                )
            )

            user_service.save_interests(["AI"])
            settings_service.save_daily_goal_seconds(300)
            growth_service.record_article_read("owner-a-news")
            analytics_service.record_article_read_event(
                "owner-a-news", "AI", "A"
            )
            analytics_service.record_article_helpful_event(
                "owner-a-news", "AI", "A"
            )

            active_scope["value"] = DataScope(kind="user", owner_id=OWNER_B)
            user_service.save_interests(["경제"])
            settings_service.save_daily_goal_seconds(60)
            growth_service.record_article_read("owner-b-news")
            analytics_service.record_article_read_event(
                "owner-b-news", "경제", "B"
            )
            analytics_service.record_article_helpful_event(
                "owner-b-news", "경제", "B"
            )

            self.assertEqual(user_service.load_interests(), ["경제"])
            self.assertEqual(settings_service.get_daily_goal_seconds(), 60)
            self.assertTrue(growth_service.is_read_today("owner-b-news"))
            self.assertFalse(growth_service.is_read_today("owner-a-news"))
            self.assertEqual(
                [event["news_id"] for event in analytics_service.load_events()],
                ["owner-b-news", "owner-b-news"],
            )
            self.assertEqual(
                analytics_service.get_today_helpful_news_ids(),
                {"owner-b-news"},
            )

            active_scope["value"] = DataScope(kind="user", owner_id=OWNER_A)
            self.assertEqual(user_service.load_interests(), ["AI"])
            self.assertEqual(settings_service.get_daily_goal_seconds(), 300)
            self.assertTrue(growth_service.is_read_today("owner-a-news"))
            self.assertFalse(growth_service.is_read_today("owner-b-news"))
            self.assertEqual(
                [event["news_id"] for event in analytics_service.load_events()],
                ["owner-a-news", "owner-a-news"],
            )
            self.assertEqual(
                analytics_service.get_today_helpful_news_ids(),
                {"owner-a-news"},
            )

            self.assertEqual(list(temp_path.iterdir()), [])

    def test_logout_with_enabled_flag_keeps_legacy_growth_flow(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            growth_file = Path(temp_dir) / "growth.json"
            with (
                patch(
                    "services.data_routing_service.is_user_data_enabled",
                    return_value=True,
                ),
                patch(
                    "services.data_routing_service.current_data_scope",
                    return_value=DataScope(kind="legacy_anonymous"),
                ),
                patch("services.growth_service.GROWTH_FILE", growth_file),
                patch(
                    "services.growth_service.today_kst",
                    return_value=date(2026, 7, 15),
                ),
                patch(
                    "services.growth_service.save_growth_to_supabase",
                    return_value=True,
                ),
                patch(
                    "services.user_data_service.upsert_user_growth_daily"
                ) as user_write,
            ):
                result = growth_service.record_article_read("anonymous-news")

            self.assertTrue(result)
            self.assertTrue(growth_file.exists())
            user_write.assert_not_called()


if __name__ == "__main__":
    unittest.main()
