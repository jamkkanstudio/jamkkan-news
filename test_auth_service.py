import unittest
from unittest.mock import MagicMock, patch

from services.auth_service import (
    AuthorizationError,
    admin_emails,
    current_user_email,
    is_admin,
    is_auth_configured,
    require_admin,
    require_automation_admin,
    render_auth_sidebar,
)


class AuthServiceTest(unittest.TestCase):
    def test_missing_auth_configuration_is_safe(self) -> None:
        with patch("services.auth_service._secret_value", return_value=None):
            self.assertFalse(is_auth_configured())

    def test_google_auth_configuration_is_detected(self) -> None:
        auth = {
            "redirect_uri": "https://example.com/oauth2callback",
            "cookie_secret": "not-a-real-secret",
            "google": {
                "client_id": "test",
                "client_secret": "test",
                "server_metadata_url": "https://accounts.example/.well-known",
            },
        }
        with patch("services.auth_service._secret_value", return_value=auth):
            self.assertTrue(is_auth_configured())

    def test_anonymous_user_has_no_email(self) -> None:
        with patch("services.auth_service.is_logged_in", return_value=False):
            self.assertEqual(current_user_email(), "")

    def test_logged_in_email_is_normalized(self) -> None:
        user = MagicMock()
        user.get.return_value = " Admin@Example.com "
        with (
            patch("services.auth_service.is_logged_in", return_value=True),
            patch("services.auth_service.st.user", user, create=True),
        ):
            self.assertEqual(current_user_email(), "admin@example.com")

    def test_admin_allowlist_accepts_list_or_comma_separated_string(self) -> None:
        for value in (["Admin@Example.com"], "Admin@Example.com, other@example.com"):
            with self.subTest(value=value), patch(
                "services.auth_service._secret_value", return_value=value
            ):
                self.assertIn("admin@example.com", admin_emails())

    def test_logged_in_non_admin_is_rejected(self) -> None:
        with (
            patch("services.auth_service.current_user_email", return_value="user@example.com"),
            patch("services.auth_service.admin_emails", return_value={"admin@example.com"}),
        ):
            self.assertFalse(is_admin())
            with self.assertRaises(AuthorizationError):
                require_admin()

    def test_admin_is_allowed(self) -> None:
        with patch("services.auth_service.is_admin", return_value=True):
            require_admin()

    def test_automation_admin_must_be_in_environment_allowlist(self) -> None:
        with patch.dict(
            "os.environ",
            {
                "ADMIN_EMAILS": "admin@example.com,other@example.com",
                "NEWS_AUTOMATION_ADMIN_EMAIL": "Admin@Example.com",
            },
            clear=True,
        ):
            require_automation_admin()

    def test_automation_non_admin_is_rejected(self) -> None:
        with patch.dict(
            "os.environ",
            {
                "ADMIN_EMAILS": "admin@example.com",
                "NEWS_AUTOMATION_ADMIN_EMAIL": "other@example.com",
            },
            clear=True,
        ):
            with self.assertRaises(AuthorizationError):
                require_automation_admin()

    def test_login_button_starts_google_login(self) -> None:
        sidebar = MagicMock()
        sidebar.__enter__.return_value = sidebar
        with (
            patch("services.auth_service.st.sidebar", sidebar),
            patch("services.auth_service.is_logged_in", return_value=False),
            patch("services.auth_service.is_auth_configured", return_value=True),
            patch("services.auth_service.st.button", return_value=True),
            patch("services.auth_service.st.login", create=True) as login,
        ):
            render_auth_sidebar()
        login.assert_called_once_with("google")

    def test_logout_button_logs_out(self) -> None:
        sidebar = MagicMock()
        sidebar.__enter__.return_value = sidebar
        with (
            patch("services.auth_service.st.sidebar", sidebar),
            patch("services.auth_service.is_logged_in", return_value=True),
            patch("services.auth_service.is_admin", return_value=False),
            patch("services.auth_service.current_user_email", return_value="user@example.com"),
            patch("services.auth_service.st.button", return_value=True),
            patch("services.auth_service.st.logout", create=True) as logout,
        ):
            render_auth_sidebar()
        logout.assert_called_once_with()

    def test_anonymous_navigation_hides_admin_pages(self) -> None:
        sidebar = MagicMock()
        sidebar.__enter__.return_value = sidebar
        with (
            patch("services.auth_service.st.sidebar", sidebar),
            patch("services.auth_service.is_admin", return_value=False),
            patch("services.auth_service.is_logged_in", return_value=False),
            patch("services.auth_service.is_auth_configured", return_value=False),
            patch("services.auth_service.st.markdown"),
            patch("services.auth_service.st.divider"),
            patch("services.auth_service.st.subheader"),
            patch("services.auth_service.st.caption"),
            patch("services.auth_service.st.page_link") as page_link,
        ):
            render_auth_sidebar()

        labels = [call.kwargs["label"] for call in page_link.call_args_list]
        self.assertEqual(
            labels,
            ["오늘의 브리핑", "관심 분야와 목표", "나의 성장", "나의 분석"],
        )

    def test_admin_navigation_shows_management_pages(self) -> None:
        sidebar = MagicMock()
        sidebar.__enter__.return_value = sidebar
        with (
            patch("services.auth_service.st.sidebar", sidebar),
            patch("services.auth_service.is_admin", return_value=True),
            patch("services.auth_service.is_logged_in", return_value=True),
            patch("services.auth_service.st.markdown"),
            patch("services.auth_service.st.divider"),
            patch("services.auth_service.st.subheader"),
            patch("services.auth_service.st.caption"),
            patch("services.auth_service.st.button", return_value=False),
            patch("services.auth_service.st.page_link") as page_link,
        ):
            render_auth_sidebar()

        labels = [call.kwargs["label"] for call in page_link.call_args_list]
        self.assertIn("뉴스 관리", labels)
        self.assertIn("수집 상태", labels)


if __name__ == "__main__":
    unittest.main()
