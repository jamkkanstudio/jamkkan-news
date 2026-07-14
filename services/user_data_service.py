"""Owner-scoped Supabase primitives for future personal-data activation."""

import re

import streamlit as st
from supabase import Client, create_client


OWNER_ID_PATTERN = re.compile(r"^usr_[0-9a-f]{64}$")


class UserDataConfigurationError(RuntimeError):
    """Raised when the server-only user-data backend is not configured."""


class InvalidOwnerIdError(ValueError):
    """Raised before a query can run with an invalid owner identifier."""


def _secret_value(key: str, default=None):
    try:
        return st.secrets.get(key, default)
    except (FileNotFoundError, KeyError, AttributeError):
        return default


@st.cache_resource
def get_user_data_client() -> Client:
    """Create a server-only client that is never exposed to browser code."""
    url = str(_secret_value("SUPABASE_URL", "")).strip()
    secret_key = str(
        _secret_value("SUPABASE_SECRET_KEY", "")
        or _secret_value("SUPABASE_SERVICE_ROLE_KEY", "")
    ).strip()

    if not url or not secret_key:
        raise UserDataConfigurationError(
            "사용자 데이터용 Supabase 서버 비밀키가 설정되지 않았습니다."
        )
    return create_client(url, secret_key)


def _validated_owner_id(owner_id: str) -> str:
    if not OWNER_ID_PATTERN.fullmatch(str(owner_id)):
        raise InvalidOwnerIdError("유효하지 않은 사용자 소유자 식별자입니다.")
    return owner_id


def load_user_interests(owner_id: str) -> list[str]:
    """Load only the selected owner's ordered interests."""
    owner_id = _validated_owner_id(owner_id)
    response = (
        get_user_data_client()
        .table("user_interests")
        .select("interest, position")
        .eq("owner_id", owner_id)
        .order("position")
        .execute()
    )
    return [row["interest"] for row in (response.data or [])]


def replace_user_interests(owner_id: str, interests: list[str]) -> None:
    """Atomically replace interests through the owner-scoped database function."""
    owner_id = _validated_owner_id(owner_id)
    get_user_data_client().rpc(
        "replace_user_interests",
        {
            "p_owner_id": owner_id,
            "p_interests": interests,
        },
    ).execute()


def load_user_settings(owner_id: str) -> dict:
    """Load only the selected owner's settings."""
    owner_id = _validated_owner_id(owner_id)
    response = (
        get_user_data_client()
        .table("user_settings")
        .select("setting_key, setting_value")
        .eq("owner_id", owner_id)
        .execute()
    )
    return {
        row["setting_key"]: row["setting_value"]
        for row in (response.data or [])
    }


def upsert_user_setting(
    owner_id: str,
    setting_key: str,
    setting_value: object,
) -> None:
    """Upsert one setting under the explicit owner composite key."""
    owner_id = _validated_owner_id(owner_id)
    (
        get_user_data_client()
        .table("user_settings")
        .upsert(
            {
                "owner_id": owner_id,
                "setting_key": setting_key,
                "setting_value": setting_value,
            },
            on_conflict="owner_id,setting_key",
        )
        .execute()
    )


def load_user_growth_daily(owner_id: str) -> list[dict]:
    """Load growth rows for exactly one owner."""
    owner_id = _validated_owner_id(owner_id)
    response = (
        get_user_data_client()
        .table("user_growth_daily")
        .select("activity_date, articles, seconds, read_news_ids")
        .eq("owner_id", owner_id)
        .order("activity_date")
        .execute()
    )
    return list(response.data or [])


def upsert_user_growth_daily(owner_id: str, growth_day: dict) -> None:
    """Upsert one owner's daily growth row without accepting owner in payload."""
    owner_id = _validated_owner_id(owner_id)
    payload = {
        "owner_id": owner_id,
        "activity_date": growth_day["activity_date"],
        "articles": growth_day["articles"],
        "seconds": growth_day["seconds"],
        "read_news_ids": list(growth_day.get("read_news_ids", [])),
    }
    (
        get_user_data_client()
        .table("user_growth_daily")
        .upsert(
            payload,
            on_conflict="owner_id,activity_date",
        )
        .execute()
    )


def load_user_events(owner_id: str) -> list[dict]:
    """Load analytics events for exactly one owner."""
    owner_id = _validated_owner_id(owner_id)
    response = (
        get_user_data_client()
        .table("user_events")
        .select(
            "id, event_type, news_id, category, title, seconds, occurred_at"
        )
        .eq("owner_id", owner_id)
        .order("occurred_at")
        .execute()
    )
    return list(response.data or [])


def insert_user_event(owner_id: str, event: dict) -> None:
    """Insert an analytics event with the trusted owner overriding payload data."""
    owner_id = _validated_owner_id(owner_id)
    payload = {
        "id": event["id"],
        "owner_id": owner_id,
        "event_type": event["event_type"],
        "news_id": event.get("news_id"),
        "category": event.get("category", "기타"),
        "title": event.get("title", ""),
        "seconds": max(int(event.get("seconds", 0)), 0),
        "occurred_at": event["occurred_at"],
    }
    get_user_data_client().table("user_events").insert(payload).execute()
