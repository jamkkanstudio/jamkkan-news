import json
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path
from uuid import uuid4

from services.time_service import datetime_to_kst_date, now_kst, today_kst


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
        "created_at": now_kst().isoformat(timespec="seconds"),
    }

    events.append(event)
    save_events(events)


def _get_event_date(event: dict) -> date | None:
    """이벤트 날짜를 한국 시간 기준으로 반환합니다."""
    created_at = event.get("created_at", "")

    if not created_at:
        return None

    try:
        event_datetime = datetime.fromisoformat(created_at)

        return datetime_to_kst_date(event_datetime)

    except (TypeError, ValueError):
        return None


def get_article_read_events() -> list[dict]:
    """기사 읽기 이벤트만 반환합니다."""
    return [
        event
        for event in load_events()
        if event.get("event_type") == "article_read"
    ]


def get_category_statistics(
    events: list[dict] | None = None,
) -> list[dict]:
    """카테고리별 기사 수와 투자 시간을 계산합니다."""
    if events is None:
        events = get_article_read_events()

    category_data = defaultdict(
        lambda: {
            "articles": 0,
            "seconds": 0,
        }
    )

    for event in events:
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


def get_current_week_events() -> list[dict]:
    """이번 주 월요일부터 오늘까지의 이벤트를 반환합니다."""
    today = today_kst()
    monday = today - timedelta(days=today.weekday())

    weekly_events = []

    for event in get_article_read_events():
        event_date = _get_event_date(event)

        if event_date and monday <= event_date <= today:
            weekly_events.append(event)

    return weekly_events


def get_current_week_daily_statistics() -> list[dict]:
    """이번 주 월요일부터 일요일까지 일별 기록을 반환합니다."""
    today = today_kst()
    monday = today - timedelta(days=today.weekday())

    daily_data = {
        monday + timedelta(days=offset): {
            "articles": 0,
            "seconds": 0,
        }
        for offset in range(7)
    }

    for event in get_current_week_events():
        event_date = _get_event_date(event)

        if event_date in daily_data:
            daily_data[event_date]["articles"] += 1
            daily_data[event_date]["seconds"] += int(
                event.get("seconds", 0)
            )

    day_names = ["월", "화", "수", "목", "금", "토", "일"]

    return [
        {
            "date": day.isoformat(),
            "day": day_names[index],
            "articles": daily_data[day]["articles"],
            "seconds": daily_data[day]["seconds"],
        }
        for index, day in enumerate(daily_data.keys())
    ]
