"""Resolve the single feature-gated storage route for personal data."""

import streamlit as st

from services.identity_service import DataScope, current_data_scope


USER_DATA_FEATURE_FLAG = "USER_DATA_ENABLED"
_TRUE_VALUES = {"1", "true", "yes", "on"}


def _secret_value(key: str, default=None):
    try:
        return st.secrets.get(key, default)
    except (FileNotFoundError, KeyError, AttributeError):
        return default


def is_user_data_enabled() -> bool:
    """Return whether all authenticated personal-data routes are enabled."""
    value = _secret_value(USER_DATA_FEATURE_FLAG, False)
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in _TRUE_VALUES


def current_storage_scope() -> DataScope:
    """
    Resolve one route shared by interests, goals, growth, and analytics.

    The disabled flag preserves the legacy behavior. Once enabled, an
    authenticated request must resolve a valid owner and may never fall back
    to the legacy global store when identity configuration is incomplete.
    """
    if not is_user_data_enabled():
        return DataScope(kind="legacy_anonymous")
    return current_data_scope()
