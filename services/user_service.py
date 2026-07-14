import json
from pathlib import Path


INTEREST_FILE = Path("data/interest.json")


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


def save_interests(interests: list[str]) -> None:
    """관심 분야 목록을 저장합니다."""
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