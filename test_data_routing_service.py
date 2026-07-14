import unittest
from unittest.mock import patch

from services.identity_service import DataScope, IdentityConfigurationError
from services.data_routing_service import (
    current_storage_scope,
    is_user_data_enabled,
)


class DataRoutingServiceTest(unittest.TestCase):
    def test_feature_flag_defaults_off_and_accepts_explicit_true_values(self) -> None:
        with patch(
            "services.data_routing_service._secret_value",
            return_value=False,
        ):
            self.assertFalse(is_user_data_enabled())

        for enabled_value in (True, "true", "1", "YES", "on"):
            with self.subTest(enabled_value=enabled_value), patch(
                "services.data_routing_service._secret_value",
                return_value=enabled_value,
            ):
                self.assertTrue(is_user_data_enabled())

    def test_disabled_flag_preserves_legacy_without_resolving_identity(self) -> None:
        with (
            patch(
                "services.data_routing_service.is_user_data_enabled",
                return_value=False,
            ),
            patch("services.data_routing_service.current_data_scope") as scope,
        ):
            resolved = current_storage_scope()

        self.assertEqual(resolved, DataScope(kind="legacy_anonymous"))
        scope.assert_not_called()

    def test_enabled_flag_never_falls_back_after_identity_failure(self) -> None:
        with (
            patch(
                "services.data_routing_service.is_user_data_enabled",
                return_value=True,
            ),
            patch(
                "services.data_routing_service.current_data_scope",
                side_effect=IdentityConfigurationError("incomplete"),
            ),
        ):
            with self.assertRaises(IdentityConfigurationError):
                current_storage_scope()


if __name__ == "__main__":
    unittest.main()
