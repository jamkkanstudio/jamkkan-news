import json
from datetime import date, timedelta
from pathlib import Path

from services.data_routing_service import current_storage_scope
from services.time_service import today_kst


GROWTH_FILE = Path("data/growth.json")


def save_growth_to_supabase(growth_day: dict) -> bool:
    """일별 성장 기록을 Supabase에 저장합니다."""
    from services.supabase_service import upsert_growth_daily

    return upsert_growth_daily(growth_day)


def _default_growth_data() -> dict:
    """성장 기록의 기본값을 반환합니다."""
    return {
        "total_articles": 0,
        "total_seconds": 0,
        "current_streak": 0,
        "last_active_date": "",
        "daily": {},
    }


def _load_legacy_growth() -> dict:
    if not GROWTH_FILE.exists():
        return _default_growth_data()

    try:
        with GROWTH_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        default_data = _default_growth_data()
        default_data.update(data)

        if not isinstance(default_data.get("daily"), dict):
            default_data["daily"] = {}

        return default_data

    except (json.JSONDecodeError, OSError):
        return _default_growth_data()


def _growth_from_daily_rows(rows: list[dict]) -> dict:
    growth = _default_growth_data()
    active_dates = []

    for row in rows:
        activity_date = str(row.get("activity_date", ""))
        try:
            parsed_date = date.fromisoformat(activity_date)
        except (TypeError, ValueError):
            continue

        articles = max(int(row.get("articles", 0)), 0)
        seconds = max(int(row.get("seconds", 0)), 0)
        growth["daily"][activity_date] = {
            "articles": articles,
            "seconds": seconds,
            "read_news_ids": list(row.get("read_news_ids", [])),
        }
        growth["total_articles"] += articles
        growth["total_seconds"] += seconds
        if articles > 0 or seconds > 0:
            active_dates.append(parsed_date)

    if active_dates:
        unique_dates = sorted(set(active_dates))
        growth["last_active_date"] = unique_dates[-1].isoformat()
        streak = 1
        for index in range(len(unique_dates) - 1, 0, -1):
            if unique_dates[index - 1] == unique_dates[index] - timedelta(days=1):
                streak += 1
            else:
                break
        growth["current_streak"] = streak

    return growth


def _load_growth_for_scope(scope) -> dict:
    if scope.kind == "user":
        from services.user_data_service import load_user_growth_daily

        return _growth_from_daily_rows(load_user_growth_daily(scope.owner_id))
    return _load_legacy_growth()


def load_growth() -> dict:
    """현재 저장 범위의 성장 기록을 불러옵니다."""
    return _load_growth_for_scope(current_storage_scope())


def _save_legacy_growth(data: dict) -> None:
    GROWTH_FILE.parent.mkdir(parents=True, exist_ok=True)

    with GROWTH_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2,
        )


def save_growth(data: dict) -> None:
    """현재 저장 범위에 성장 기록을 저장합니다."""
    scope = current_storage_scope()
    if scope.kind == "user":
        from services.user_data_service import upsert_user_growth_daily

        for activity_date, day in data.get("daily", {}).items():
            upsert_user_growth_daily(
                scope.owner_id,
                {
                    "activity_date": activity_date,
                    "articles": day.get("articles", 0),
                    "seconds": day.get("seconds", 0),
                    "read_news_ids": day.get("read_news_ids", []),
                },
            )
        return
    _save_legacy_growth(data)


def get_today_read_news_ids() -> set[str]:
    """현재 저장 범위에서 오늘 완료한 기사 ID를 반환합니다."""
    growth = load_growth()
    today = today_kst().isoformat()

    today_data = growth["daily"].get(today, {})
    read_news_ids = today_data.get("read_news_ids", [])

    return {str(news_id) for news_id in read_news_ids}


def is_read_today(news_id: str) -> bool:
    """해당 기사를 오늘 이미 읽었는지 확인합니다."""

    return news_id in get_today_read_news_ids()


def record_article_read(
    news_id: str,
    seconds: int = 30,
) -> bool | None:
    """
    기사 읽기 기록을 저장합니다.

    오늘 이미 기록된 기사라면 False, 선택된 저장 경로에 저장하면 True,
    legacy JSON만 저장되고 Supabase 미러링이 실패하면 None을 반환합니다.
    """
    scope = current_storage_scope()
    growth = _load_growth_for_scope(scope)

    today = today_kst()
    today_string = today.isoformat()

    today_data = growth["daily"].setdefault(
        today_string,
        {
            "articles": 0,
            "seconds": 0,
            "read_news_ids": [],
        },
    )

    if news_id in today_data["read_news_ids"]:
        return False

    today_data["read_news_ids"].append(news_id)
    today_data["articles"] += 1
    today_data["seconds"] += seconds

    growth["total_articles"] += 1
    growth["total_seconds"] += seconds

    last_active_date = growth.get("last_active_date", "")

    if not last_active_date:
        growth["current_streak"] = 1

    else:
        try:
            previous_date = date.fromisoformat(last_active_date)

            if previous_date == today:
                pass
            elif previous_date == today - timedelta(days=1):
                growth["current_streak"] += 1
            else:
                growth["current_streak"] = 1

        except ValueError:
            growth["current_streak"] = 1

    growth["last_active_date"] = today_string

    growth_day = {
        "activity_date": today_string,
        "articles": today_data["articles"],
        "seconds": today_data["seconds"],
        "read_news_ids": today_data["read_news_ids"],
    }
    if scope.kind == "user":
        from services.user_data_service import upsert_user_growth_daily

        upsert_user_growth_daily(scope.owner_id, growth_day)
        return True

    _save_legacy_growth(growth)
    mirrored = save_growth_to_supabase(
        growth_day
    )

    return True if mirrored else None


def get_growth_summary() -> dict:
    """화면에 표시할 성장 통계를 반환합니다."""
    growth = load_growth()
    today = today_kst().isoformat()

    today_data = growth["daily"].get(
        today,
        {
            "articles": 0,
            "seconds": 0,
        },
    )

    return {
        "today_articles": today_data.get("articles", 0),
        "today_seconds": today_data.get("seconds", 0),
        "total_articles": growth.get("total_articles", 0),
        "total_seconds": growth.get("total_seconds", 0),
        "current_streak": growth.get("current_streak", 0),
    }


def is_today_brief_completed(news_list: list[dict]) -> bool:
    """
    오늘의 브리핑을 모두 완료했는지 확인합니다.
    """

    growth = load_growth()

    today = today_kst().isoformat()

    today_data = growth["daily"].get(today, {})

    read_news_ids = set(
        today_data.get("read_news_ids", [])
    )

    if not news_list:
        return False

    today_news_ids = {
        news.get("id")
        for news in news_list
        if news.get("id")
    }

    return (
        len(today_news_ids) > 0
        and today_news_ids.issubset(read_news_ids)
    )
