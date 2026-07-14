from datetime import datetime
from email.utils import parsedate_to_datetime

import feedparser


RSS_FEEDS = {
    "최신": "http://www.yonhapnewstv.co.kr/browse/feed/",
    "정치": "http://www.yonhapnewstv.co.kr/category/news/politics/feed/",
    "경제": "http://www.yonhapnewstv.co.kr/category/news/economy/feed/",
    "사회": "http://www.yonhapnewstv.co.kr/category/news/society/feed/",
    "국제": "http://www.yonhapnewstv.co.kr/category/news/international/feed/",
}


def _parse_published_date(entry) -> str:
    """RSS 발행일을 ISO 형식 문자열로 변환합니다."""
    published = entry.get("published", "")

    if not published:
        return ""

    try:
        parsed_date = parsedate_to_datetime(published)
        return parsed_date.isoformat(timespec="seconds")
    except (TypeError, ValueError, OverflowError):
        return published


def fetch_rss_news(category: str = "최신", limit: int = 20) -> list[dict]:
    """선택한 RSS에서 최신 기사 목록을 가져옵니다."""
    if category not in RSS_FEEDS:
        raise ValueError(f"지원하지 않는 카테고리입니다: {category}")

    feed_url = RSS_FEEDS[category]
    feed = feedparser.parse(feed_url)

    if feed.bozo and not feed.entries:
        raise RuntimeError("RSS를 불러오지 못했습니다.")

    news_list = []

    for entry in feed.entries[:limit]:
        news_list.append(
            {
                "title": entry.get("title", "").strip(),
                "url": entry.get("link", "").strip(),
                "summary": entry.get("summary", "").strip(),
                "source": "연합뉴스TV",
                "category": category,
                "published_at": _parse_published_date(entry),
                "collected_at": datetime.now().isoformat(timespec="seconds"),
            }
        )

    return news_list