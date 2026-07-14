import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from services.user_service import save_interests


class SaveInterestsTest(unittest.TestCase):
    def test_save_interests_writes_json_then_supabase(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            interest_file = Path(temp_dir) / "interest.json"

            with (
                patch("services.user_service.INTEREST_FILE", interest_file),
                patch(
                    "services.user_service.save_interests_to_supabase",
                    return_value=True,
                ) as save_supabase,
            ):
                mirrored = save_interests(["경제", "AI"])

            with interest_file.open("r", encoding="utf-8") as file:
                saved_data = json.load(file)

            self.assertEqual(saved_data, {"interests": ["경제", "AI"]})
            save_supabase.assert_called_once_with(["경제", "AI"])
            self.assertTrue(mirrored)


if __name__ == "__main__":
    unittest.main()
