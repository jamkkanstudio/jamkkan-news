from collections.abc import Mapping
import os

import streamlit as st


class AuthorizationError(PermissionError):
    """Raised when a protected global write lacks administrator access."""


def _secret_value(key: str, default=None):
    try:
        return st.secrets.get(key, default)
    except (FileNotFoundError, KeyError, AttributeError):
        return default


def is_auth_configured() -> bool:
    auth = _secret_value("auth")
    if not isinstance(auth, Mapping):
        return False
    return bool(
        auth.get("redirect_uri")
        and auth.get("cookie_secret")
        and isinstance(auth.get("google"), Mapping)
        and auth["google"].get("client_id")
        and auth["google"].get("client_secret")
        and auth["google"].get("server_metadata_url")
    )


def is_logged_in() -> bool:
    try:
        return bool(st.user.is_logged_in)
    except (AttributeError, KeyError, TypeError):
        return False


def current_user_email() -> str:
    if not is_logged_in():
        return ""
    try:
        return str(st.user.get("email", "")).strip().lower()
    except (AttributeError, KeyError, TypeError):
        return ""


def admin_emails() -> set[str]:
    raw_emails = _secret_value("ADMIN_EMAILS", [])
    if isinstance(raw_emails, str):
        raw_emails = raw_emails.split(",")
    if not isinstance(raw_emails, (list, tuple, set)):
        return set()
    return {str(email).strip().lower() for email in raw_emails if str(email).strip()}


def _parse_email_allowlist(raw_emails) -> set[str]:
    """쉼표 문자열이나 목록 형태의 관리자 이메일을 정규화합니다."""
    if isinstance(raw_emails, str):
        raw_emails = raw_emails.split(",")
    if not isinstance(raw_emails, (list, tuple, set)):
        return set()
    return {
        str(email).strip().lower()
        for email in raw_emails
        if str(email).strip()
    }


def is_admin() -> bool:
    email = current_user_email()
    return bool(email and email in admin_emails())


def require_admin() -> None:
    if not is_admin():
        raise AuthorizationError("관리자 권한이 필요한 작업입니다.")


def require_automation_admin() -> None:
    """예약 작업의 실행 주체가 배포 관리자 목록에 있는지 확인합니다."""
    automation_email = os.environ.get(
        "NEWS_AUTOMATION_ADMIN_EMAIL",
        "",
    ).strip().lower()
    allowed_emails = _parse_email_allowlist(
        os.environ.get("ADMIN_EMAILS", "")
    )

    if not automation_email or automation_email not in allowed_emails:
        raise AuthorizationError("자동 수집 관리자 권한이 필요합니다.")


def render_auth_sidebar() -> None:
    with st.sidebar:
        st.subheader("계정")
        if is_logged_in():
            st.caption(current_user_email() or "로그인됨")
            st.write("관리자" if is_admin() else "로그인 사용자")
            if st.button("로그아웃", key="auth_logout", use_container_width=True):
                st.logout()
        elif is_auth_configured():
            if st.button("Google로 로그인", key="auth_login", use_container_width=True):
                st.login("google")
        else:
            st.caption("로그인 설정이 없어 읽기 전용으로 실행 중입니다.")


def require_admin_page() -> None:
    render_auth_sidebar()
    if is_admin():
        return
    if not is_auth_configured():
        st.info("관리자 로그인이 설정되지 않아 이 화면을 사용할 수 없습니다.")
    elif is_logged_in():
        st.warning("이 계정에는 관리자 권한이 없습니다.")
    else:
        st.info("관리자만 사용할 수 있습니다. 사이드바에서 로그인해 주세요.")
    st.stop()
