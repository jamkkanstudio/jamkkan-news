import json
from pathlib import Path

from services.auth_service import require_admin
from services.data_routing_service import current_storage_scope


INTEREST_FILE = Path("data/interest.json")


def save_interests_to_supabase(interests: list[str]) -> bool:
    """관심 분야 목록을 Supabase에 저장합니다."""
    from services.supabase_service import replace_interests

    return replace_interests(interests)


def _load_legacy_interests() -> list[str]:
    if not INTEREST_FILE.exists():
        return []

    try:
        with INTEREST_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        interests = data.get("interests", [])

        if not isinstance(interests, list):
            return []

        return interests

    except (json.JSONDecodeError, OSError):
        return []


def load_interests() -> list[str]:
    """현재 저장 범위의 관심 분야 목록을 불러옵니다."""
    scope = current_storage_scope()
    if scope.kind == "user":
        from services.user_data_service import load_user_interests

        return load_user_interests(scope.owner_id)
    return _load_legacy_interests()


def save_interests(interests: list[str]) -> bool:
    """현재 저장 범위에 관심 분야를 저장합니다."""
    scope = current_storage_scope()
    if scope.kind == "user":
        from services.user_data_service import replace_user_interests

        replace_user_interests(scope.owner_id, interests)
        return True

    require_admin()
    INTEREST_FILE.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "interests": interests,
    }

    with INTEREST_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2,
        )

    return save_interests_to_supabase(interests)
