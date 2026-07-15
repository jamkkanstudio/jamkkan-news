import json
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path
from uuid import uuid4

from services.data_routing_service import current_storage_scope
from services.time_service import datetime_to_kst_date, now_kst, today_kst


EVENTS_FILE = Path("data/events.json")
ARTICLE_READ_EVENT = "article_read"
ARTICLE_HELPFUL_EVENT = "article_helpful"


def _load_legacy_events() -> list[dict]:
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


def load_events() -> list[dict]:
    """현재 저장 범위의 사용자 행동 기록을 불러옵니다."""
    scope = current_storage_scope()
    if scope.kind == "user":
        from services.user_data_service import load_user_events

        return [
            {
                **event,
                "created_at": event.get("occurred_at", ""),
            }
            for event in load_user_events(scope.owner_id)
        ]
    return _load_legacy_events()


def _save_legacy_events(events: list[dict]) -> None:
    EVENTS_FILE.parent.mkdir(parents=True, exist_ok=True)

    with EVENTS_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            events,
            file,
            ensure_ascii=False,
            indent=2,
        )


def _record_article_event(
    event_type: str,
    news_id: str,
    category: str,
    title: str,
    seconds: int,
) -> None:
    event = {
        "id": str(uuid4()),
        "event_type": event_type,
        "news_id": news_id,
        "category": category or "기타",
        "title": title,
        "seconds": max(int(seconds), 0),
        "created_at": now_kst().isoformat(timespec="seconds"),
    }

    scope = current_storage_scope()
    if scope.kind == "user":
        from services.user_data_service import insert_user_event

        insert_user_event(
            scope.owner_id,
            {
                **event,
                "occurred_at": event["created_at"],
            },
        )
        return

    events = _load_legacy_events()
    events.append(event)
    _save_legacy_events(events)


def record_article_read_event(
    news_id: str,
    category: str,
    title: str,
    seconds: int = 30,
) -> None:
    """기사 투자 완료 이벤트를 저장합니다."""
    _record_article_event(
        ARTICLE_READ_EVENT,
        news_id,
        category,
        title,
        seconds,
    )


def record_article_helpful_event(
    news_id: str,
    category: str,
    title: str,
) -> None:
    """사용자가 명시한 기사 도움 신호를 저장합니다."""
    _record_article_event(
        ARTICLE_HELPFUL_EVENT,
        news_id,
        category,
        title,
        0,
    )


def save_events(events: list[dict]) -> None:
    """현재 저장 범위에 사용자 행동 기록을 저장합니다."""
    scope = current_storage_scope()
    if scope.kind == "user":
        from services.user_data_service import insert_user_event

        for event in events:
            insert_user_event(
                scope.owner_id,
                {
                    **event,
                    "occurred_at": event.get(
                        "occurred_at", event.get("created_at", "")
                    ),
                },
            )
        return
    _save_legacy_events(events)


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
        if event.get("event_type") == ARTICLE_READ_EVENT
    ]


def get_today_helpful_news_ids() -> set[str]:
    """오늘 현재 범위에서 도움 신호를 남긴 기사 ID를 반환합니다."""
    today = today_kst()
    return {
        str(event.get("news_id"))
        for event in load_events()
        if event.get("event_type") == ARTICLE_HELPFUL_EVENT
        and event.get("news_id")
        and _get_event_date(event) == today
    }


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
