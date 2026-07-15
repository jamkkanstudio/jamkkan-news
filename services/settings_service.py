import json
from pathlib import Path

from services.auth_service import require_admin, require_automation_admin
from services.data_routing_service import current_storage_scope


SETTINGS_FILE = Path("data/settings.json")
DEFAULT_DAILY_GOAL_SECONDS = 180
DAILY_BRIEFING_KEY = "daily_briefing"


def save_setting_to_supabase(
    setting_key: str,
    setting_value: object,
) -> bool:
    """설정 한 건을 Supabase에 저장합니다."""
    from services.supabase_service import upsert_setting

    return upsert_setting(setting_key, setting_value)


def _default_settings() -> dict:
    return {
        "daily_goal_seconds": DEFAULT_DAILY_GOAL_SECONDS,
    }


def _load_legacy_settings() -> dict:
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


def load_settings() -> dict:
    """현재 저장 범위의 설정을 불러옵니다."""
    scope = current_storage_scope()
    if scope.kind == "user":
        from services.user_data_service import load_user_settings

        settings = _default_settings()
        settings.update(load_user_settings(scope.owner_id))
        return settings
    return _load_legacy_settings()


def load_global_daily_briefing(target_date: str) -> dict | None:
    """익명·로그인 사용자에게 공통인 당일 후보 스냅샷만 읽습니다."""
    snapshot = _load_legacy_settings().get(DAILY_BRIEFING_KEY)
    if not isinstance(snapshot, dict) or snapshot.get("date") != target_date:
        return None
    candidate_ids = snapshot.get("candidate_ids")
    if not isinstance(candidate_ids, list) or not candidate_ids:
        return None
    if not all(isinstance(news_id, str) and news_id for news_id in candidate_ids):
        return None
    return {
        "date": target_date,
        "candidate_ids": list(dict.fromkeys(candidate_ids)),
        "selected_at": str(snapshot.get("selected_at", "")),
    }


def save_global_daily_briefing(snapshot: dict) -> bool:
    """자동화 관리자만 당일 후보군을 Supabase 우선으로 고정합니다."""
    require_automation_admin()
    target_date = str(snapshot.get("date", "")).strip()
    candidate_ids = [
        str(news_id).strip()
        for news_id in snapshot.get("candidate_ids", [])
        if str(news_id).strip()
    ]
    normalized = {
        "date": target_date,
        "candidate_ids": list(dict.fromkeys(candidate_ids)),
        "selected_at": str(snapshot.get("selected_at", "")).strip(),
    }
    if not target_date or not normalized["candidate_ids"]:
        raise ValueError("invalid_daily_briefing")

    settings = _load_legacy_settings()
    existing = settings.get(DAILY_BRIEFING_KEY)
    if isinstance(existing, dict) and existing.get("date") == target_date:
        return True

    if not save_setting_to_supabase(DAILY_BRIEFING_KEY, normalized):
        return False

    settings[DAILY_BRIEFING_KEY] = normalized
    SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    temporary_file = SETTINGS_FILE.with_suffix(f"{SETTINGS_FILE.suffix}.tmp")
    try:
        with temporary_file.open("w", encoding="utf-8") as file:
            json.dump(settings, file, ensure_ascii=False, indent=2)
            file.flush()
        temporary_file.replace(SETTINGS_FILE)
    finally:
        temporary_file.unlink(missing_ok=True)
    return True


def save_settings(settings: dict) -> None:
    """현재 저장 범위에 설정을 저장합니다."""
    scope = current_storage_scope()
    if scope.kind == "user":
        from services.user_data_service import upsert_user_setting

        for setting_key, setting_value in settings.items():
            upsert_user_setting(
                scope.owner_id,
                setting_key,
                setting_value,
            )
        return

    require_admin()
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
    """현재 저장 범위에 일일 목표를 저장합니다."""
    scope = current_storage_scope()
    goal_seconds = max(int(seconds), 30)
    if scope.kind == "user":
        from services.user_data_service import upsert_user_setting

        upsert_user_setting(
            scope.owner_id,
            "daily_goal_seconds",
            goal_seconds,
        )
        return True

    require_admin()
    settings = _load_legacy_settings()
    settings["daily_goal_seconds"] = goal_seconds
    SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with SETTINGS_FILE.open("w", encoding="utf-8") as file:
        json.dump(settings, file, ensure_ascii=False, indent=2)
    return save_setting_to_supabase(
        "daily_goal_seconds",
        settings["daily_goal_seconds"],
    )
