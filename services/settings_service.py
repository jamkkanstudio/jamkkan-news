import json
from pathlib import Path


SETTINGS_FILE = Path("data/settings.json")
DEFAULT_DAILY_GOAL_SECONDS = 180


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


def save_daily_goal_seconds(seconds: int) -> None:
    """오늘의 목표 시간을 저장합니다."""
    settings = load_settings()
    settings["daily_goal_seconds"] = max(int(seconds), 30)
    save_settings(settings)