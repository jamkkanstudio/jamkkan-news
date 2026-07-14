"""Derive an opaque storage owner from the current OIDC identity."""

from dataclasses import dataclass
from hashlib import sha256
import hmac

import streamlit as st

from services.auth_service import is_logged_in


OWNER_ID_SECRET = "USER_ID_PEPPER"
MINIMUM_PEPPER_LENGTH = 32


class IdentityConfigurationError(RuntimeError):
    """Raised when an authenticated identity cannot be scoped safely."""


@dataclass(frozen=True)
class DataScope:
    """Select either the anonymous legacy store or an isolated user owner."""

    kind: str
    owner_id: str | None = None


def _secret_value(key: str, default=None):
    try:
        return st.secrets.get(key, default)
    except (FileNotFoundError, KeyError, AttributeError):
        return default


def _current_claim(name: str) -> str:
    try:
        return str(st.user.get(name, "")).strip()
    except (AttributeError, KeyError, TypeError):
        return ""


def current_owner_id() -> str | None:
    """
    Return a stable opaque owner id for a logged-in user.

    Anonymous visitors intentionally receive ``None`` and continue to use the
    legacy public data flow. Authenticated identities fail closed when the
    provider subject or server-only pepper is unavailable.
    """
    if not is_logged_in():
        return None

    issuer = _current_claim("iss")
    subject = _current_claim("sub")
    pepper = str(_secret_value(OWNER_ID_SECRET, ""))

    if not issuer or not subject:
        raise IdentityConfigurationError(
            "로그인 식별자(iss/sub)가 없어 사용자 데이터를 분리할 수 없습니다."
        )
    if len(pepper) < MINIMUM_PEPPER_LENGTH:
        raise IdentityConfigurationError(
            f"{OWNER_ID_SECRET}는 {MINIMUM_PEPPER_LENGTH}자 이상이어야 합니다."
        )

    identity = f"{issuer.rstrip('/')}\x00{subject}".encode("utf-8")
    digest = hmac.new(
        pepper.encode("utf-8"),
        identity,
        sha256,
    ).hexdigest()
    return f"usr_{digest}"


def current_data_scope() -> DataScope:
    """Resolve the safe storage scope without persisting an identity claim."""
    owner_id = current_owner_id()
    if owner_id is None:
        return DataScope(kind="legacy_anonymous")
    return DataScope(kind="user", owner_id=owner_id)
