import json
from datetime import datetime
from pathlib import Path
from uuid import uuid4


DATA_FILE = Path("data/news.json")


def save_news_to_supabase(news: dict) -> bool:
    """뉴스 한 건을 Supabase에 저장합니다."""
    from services.supabase_service import upsert_news

    return upsert_news(news)


def load_news() -> list[dict]:
    """news.json에서 뉴스 목록을 불러옵니다."""
    if not DATA_FILE.exists():
        return []

    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return []


def save_news(news_list: list[dict]) -> None:
    """뉴스 목록을 news.json에 저장합니다."""
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            news_list,
            file,
            ensure_ascii=False,
            indent=2,
        )


def add_news(news: dict) -> bool:
    """새 뉴스를 JSON에 추가하고 Supabase 미러링 결과를 반환합니다."""
    news_list = load_news()

    new_news = {
        "id": str(uuid4()),
        "title": news["title"],
        "summary": news["summary"],
        "reason": news["reason"],
        "source": news["source"],
        "url": news["url"],
        "category": news.get("category", "기타"),
        "importance": news.get("importance", 50),
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }

    news_list.append(new_news)
    save_news(news_list)
    return save_news_to_supabase(new_news)


def delete_news(news_id: str) -> bool:
    """id가 일치하는 뉴스를 삭제합니다."""
    news_list = load_news()

    updated_news = [
        news for news in news_list
        if news.get("id") != news_id
    ]

    if len(updated_news) == len(news_list):
        return False

    save_news(updated_news)
    return True


def update_news(news_id: str, updated_data: dict) -> bool | None:
    """뉴스를 JSON에서 수정하고 Supabase 미러링 결과를 반환합니다."""
    news_list = load_news()

    for news in news_list:
        if news.get("id") == news_id:
            news.update(
                {
                    "title": updated_data["title"],
                    "summary": updated_data["summary"],
                    "reason": updated_data["reason"],
                    "source": updated_data["source"],
                    "url": updated_data["url"],
                    "category": updated_data["category"],
                    "importance": updated_data["importance"],
                }
            )

            save_news(news_list)
            return save_news_to_supabase(news)

    return None
