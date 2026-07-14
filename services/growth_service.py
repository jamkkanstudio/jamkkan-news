import json
from datetime import date, timedelta
from pathlib import Path


GROWTH_FILE = Path("data/growth.json")


def _default_growth_data() -> dict:
    """성장 기록의 기본값을 반환합니다."""
    return {
        "total_articles": 0,
        "total_seconds": 0,
        "current_streak": 0,
        "last_active_date": "",
        "daily": {},
    }


def load_growth() -> dict:
    """저장된 성장 기록을 불러옵니다."""
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


def save_growth(data: dict) -> None:
    """성장 기록을 JSON 파일에 저장합니다."""
    GROWTH_FILE.parent.mkdir(parents=True, exist_ok=True)

    with GROWTH_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2,
        )


def is_read_today(news_id: str) -> bool:
    """해당 기사를 오늘 이미 읽었는지 확인합니다."""
    growth = load_growth()
    today = date.today().isoformat()

    today_data = growth["daily"].get(today, {})
    read_news_ids = today_data.get("read_news_ids", [])

    return news_id in read_news_ids


def record_article_read(
    news_id: str,
    seconds: int = 30,
) -> bool:
    """
    기사 읽기 기록을 저장합니다.

    오늘 이미 기록된 기사라면 False,
    새롭게 기록했다면 True를 반환합니다.
    """
    growth = load_growth()

    today = date.today()
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

    save_growth(growth)

    return True


def get_growth_summary() -> dict:
    """화면에 표시할 성장 통계를 반환합니다."""
    growth = load_growth()
    today = date.today().isoformat()

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

    today = date.today().isoformat()

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