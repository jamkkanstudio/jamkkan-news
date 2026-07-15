import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from services.settings_service import (
    load_global_daily_briefing,
    save_daily_goal_seconds,
    save_global_daily_briefing,
)


class SaveDailyGoalSecondsTest(unittest.TestCase):
    def test_save_daily_goal_writes_json_then_supabase(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            settings_file = Path(temp_dir) / "settings.json"

            with (
                patch(
                    "services.settings_service.SETTINGS_FILE",
                    settings_file,
                ),
                patch("services.settings_service.require_admin"),
                patch(
                    "services.settings_service.save_setting_to_supabase",
                    return_value=True,
                ) as save_supabase,
            ):
                mirrored = save_daily_goal_seconds(300)

            with settings_file.open("r", encoding="utf-8") as file:
                saved_settings = json.load(file)

            self.assertEqual(saved_settings["daily_goal_seconds"], 300)
            save_supabase.assert_called_once_with(
                "daily_goal_seconds",
                300,
            )
            self.assertTrue(mirrored)

    def test_daily_briefing_snapshot_requires_automation_admin_and_mirrors(self):
        snapshot = {
            "date": "2026-07-15",
            "candidate_ids": ["one", "two", "one"],
            "selected_at": "2026-07-15T08:00:00+09:00",
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            settings_file = Path(temp_dir) / "settings.json"
            settings_file.write_text(
                json.dumps({"daily_goal_seconds": 300}),
                encoding="utf-8",
            )
            operations = []
            with (
                patch(
                    "services.settings_service.SETTINGS_FILE",
                    settings_file,
                ),
                patch(
                    "services.settings_service.require_automation_admin",
                    side_effect=lambda: operations.append("authorize"),
                ),
                patch(
                    "services.settings_service.save_setting_to_supabase",
                    side_effect=lambda key, value: operations.append("supabase")
                    or True,
                ),
            ):
                saved = save_global_daily_briefing(snapshot)
                loaded = load_global_daily_briefing("2026-07-15")

        self.assertTrue(saved)
        self.assertEqual(operations, ["authorize", "supabase"])
        self.assertEqual(loaded["candidate_ids"], ["one", "two"])

    def test_daily_briefing_mirror_failure_preserves_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            settings_file = Path(temp_dir) / "settings.json"
            original = {"daily_goal_seconds": 300}
            settings_file.write_text(json.dumps(original), encoding="utf-8")
            with (
                patch(
                    "services.settings_service.SETTINGS_FILE",
                    settings_file,
                ),
                patch("services.settings_service.require_automation_admin"),
                patch(
                    "services.settings_service.save_setting_to_supabase",
                    return_value=False,
                ),
            ):
                saved = save_global_daily_briefing(
                    {
                        "date": "2026-07-15",
                        "candidate_ids": ["one"],
                        "selected_at": "now",
                    }
                )

            self.assertFalse(saved)
            self.assertEqual(
                json.loads(settings_file.read_text(encoding="utf-8")),
                original,
            )


if __name__ == "__main__":
    unittest.main()
