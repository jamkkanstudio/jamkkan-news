import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from uuid import uuid4


EVENTS_FILE = Path("data/events.json")


def load_events() -> list[dict]:
    """저장된 사용자 행동 기록을 불러옵니다."""
    if not EVENTS_FILE.exists():
        return []

    try:
        with EVENTS_FILE.open("r", encoding="utf-8") as file:
            events = json.load(file)

        if not isinstance(events, list):
            return []

        return events

    except (json.JSONDecodeError, OSError):
        return []


def save_events(events: list[dict]) -> None:
    """사용자 행동 기록을 JSON 파일에 저장합니다."""
    EVENTS_FILE.parent.mkdir(parents=True, exist_ok=True)

    with EVENTS_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            events,
            file,
            ensure_ascii=False,
            indent=2,
        )


def record_article_read_event(
    news_id: str,
    category: str,
    title: str,
    seconds: int = 30,
) -> None:
    """기사 투자 완료 이벤트를 저장합니다."""
    events = load_events()

    event = {
        "id": str(uuid4()),
        "event_type": "article_read",
        "news_id": news_id,
        "category": category or "기타",
        "title": title,
        "seconds": max(int(seconds), 0),
        "created_at": datetime.now().isoformat(
            timespec="seconds"
        ),
    }

    events.append(event)
    save_events(events)


def get_category_statistics() -> list[dict]:
    """카테고리별 읽은 기사 수와 투자 시간을 계산합니다."""
    events = load_events()
    category_data = defaultdict(
        lambda: {
            "articles": 0,
            "seconds": 0,
        }
    )

    for event in events:
        if event.get("event_type") != "article_read":
            continue

        category = event.get("category", "기타")
        category_data[category]["articles"] += 1
        category_data[category]["seconds"] += int(
            event.get("seconds", 0)
        )

    statistics = [
        {
            "category": category,
            "articles": values["articles"],
            "seconds": values["seconds"],
        }
        for category, values in category_data.items()
    ]

    return sorted(
        statistics,
        key=lambda item: item["seconds"],
        reverse=True,
    )