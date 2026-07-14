import json
from pathlib import Path

from services.auth_service import require_admin


SETTINGS_FILE = Path("data/settings.json")
DEFAULT_DAILY_GOAL_SECONDS = 180


def save_setting_to_supabase(
    setting_key: str,
    setting_value: object,
) -> bool:
    """설정 한 건을 Supabase에 저장합니다."""
    from services.supabase_service import upsert_setting

    return upsert_setting(setting_key, setting_value)


def load_settings() -> dict:
    """사용자 설정을 불러옵니다."""
    default_settings = {
        "daily_goal_seconds": DEFAULT_DAILY_GOAL_SECONDS,
    }

    if not SETTINGS_FILE.exists():
        return default_settings

    try:
        with SETTINGS_FILE.open("r", encoding="utf-8") as file:
            saved_settings = json.load(file)

        if not isinstance(saved_settings, dict):
            return default_settings

        default_settings.update(saved_settings)
        return default_settings

    except (json.JSONDecodeError, OSError):
        return default_settings


def save_settings(settings: dict) -> None:
    """사용자 설정을 저장합니다."""
    SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)

    with SETTINGS_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            settings,
            file,
            ensure_ascii=False,
            indent=2,
        )


def get_daily_goal_seconds() -> int:
    """오늘의 목표 시간을 초 단위로 반환합니다."""
    settings = load_settings()

    try:
        goal_seconds = int(
            settings.get(
                "daily_goal_seconds",
                DEFAULT_DAILY_GOAL_SECONDS,
            )
        )
    except (TypeError, ValueError):
        return DEFAULT_DAILY_GOAL_SECONDS

    return max(goal_seconds, 30)


def save_daily_goal_seconds(seconds: int) -> bool:
    """목표 시간을 JSON에 저장하고 Supabase 미러링 결과를 반환합니다."""
    require_admin()
    settings = load_settings()
    settings["daily_goal_seconds"] = max(int(seconds), 30)
    save_settings(settings)
    return save_setting_to_supabase(
        "daily_goal_seconds",
        settings["daily_goal_seconds"],
    )
