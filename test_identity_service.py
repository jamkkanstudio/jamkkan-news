import unittest
from unittest.mock import patch

from services.identity_service import (
    IdentityConfigurationError,
    current_data_scope,
    current_owner_id,
)


PEPPER = "p" * 32


class IdentityServiceTest(unittest.TestCase):
    def test_anonymous_scope_keeps_legacy_flow_without_secrets(self) -> None:
        with patch("services.identity_service.is_logged_in", return_value=False):
            scope = current_data_scope()

        self.assertEqual(scope.kind, "legacy_anonymous")
        self.assertIsNone(scope.owner_id)

    def test_logged_in_identity_becomes_opaque_owner_id(self) -> None:
        claims = {"iss": "https://accounts.google.com", "sub": "subject-123"}
        with (
            patch("services.identity_service.is_logged_in", return_value=True),
            patch(
                "services.identity_service._current_claim",
                side_effect=lambda name: claims[name],
            ),
            patch("services.identity_service._secret_value", return_value=PEPPER),
        ):
            first = current_owner_id()
            second = current_owner_id()

        self.assertEqual(first, second)
        self.assertRegex(first or "", r"^usr_[0-9a-f]{64}$")
        self.assertNotIn("subject-123", first or "")
        self.assertNotIn("accounts.google.com", first or "")

    def test_issuer_is_part_of_owner_boundary(self) -> None:
        with (
            patch("services.identity_service.is_logged_in", return_value=True),
            patch("services.identity_service._secret_value", return_value=PEPPER),
            patch(
                "services.identity_service._current_claim",
                side_effect=lambda name: {
                    "iss": "https://issuer-one.example",
                    "sub": "same-subject",
                }[name],
            ),
        ):
            first = current_owner_id()

        with (
            patch("services.identity_service.is_logged_in", return_value=True),
            patch("services.identity_service._secret_value", return_value=PEPPER),
            patch(
                "services.identity_service._current_claim",
                side_effect=lambda name: {
                    "iss": "https://issuer-two.example",
                    "sub": "same-subject",
                }[name],
            ),
        ):
            second = current_owner_id()

        self.assertNotEqual(first, second)

    def test_authenticated_identity_fails_closed_without_claims(self) -> None:
        with (
            patch("services.identity_service.is_logged_in", return_value=True),
            patch("services.identity_service._current_claim", return_value=""),
            patch("services.identity_service._secret_value", return_value=PEPPER),
        ):
            with self.assertRaises(IdentityConfigurationError):
                current_data_scope()

    def test_authenticated_identity_fails_closed_with_short_pepper(self) -> None:
        with (
            patch("services.identity_service.is_logged_in", return_value=True),
            patch("services.identity_service._current_claim", return_value="claim"),
            patch("services.identity_service._secret_value", return_value="short"),
        ):
            with self.assertRaises(IdentityConfigurationError):
                current_data_scope()


if __name__ == "__main__":
    unittest.main()
