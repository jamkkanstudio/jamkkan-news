import json
from pathlib import Path

from services.auth_service import require_admin


INTEREST_FILE = Path("data/interest.json")


def save_interests_to_supabase(interests: list[str]) -> bool:
    """관심 분야 목록을 Supabase에 저장합니다."""
    from services.supabase_service import replace_interests

    return replace_interests(interests)


def load_interests() -> list[str]:
    """저장된 관심 분야 목록을 불러옵니다."""
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


def save_interests(interests: list[str]) -> bool:
    """관심 분야를 JSON에 저장하고 Supabase 미러링 결과를 반환합니다."""
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
