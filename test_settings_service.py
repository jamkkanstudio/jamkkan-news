import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from services.settings_service import save_daily_goal_seconds


class SaveDailyGoalSecondsTest(unittest.TestCase):
    def test_save_daily_goal_writes_json_then_supabase(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            settings_file = Path(temp_dir) / "settings.json"

            with (
                patch(
                    "services.settings_service.SETTINGS_FILE",
                    settings_file,
                ),
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


if __name__ == "__main__":
    unittest.main()
