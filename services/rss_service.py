from datetime import datetime
from email.utils import parsedate_to_datetime
from urllib.request import Request, urlopen

import feedparser


RSS_FEEDS = {
    "최신": "https://www.yonhapnewstv.co.kr/browse/feed/",
    "정치": "https://www.yonhapnewstv.co.kr/category/news/politics/feed/",
    "경제": "https://www.yonhapnewstv.co.kr/category/news/economy/feed/",
    "사회": "https://www.yonhapnewstv.co.kr/category/news/society/feed/",
    "국제": "https://www.yonhapnewstv.co.kr/category/news/international/feed/",
}

RSS_TIMEOUT_SECONDS = 20
RSS_USER_AGENT = "JamkkanNewsCollector/1.0 (+https://jamkkan-news.streamlit.app/)"


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
    request = Request(
        feed_url,
        headers={"User-Agent": RSS_USER_AGENT},
    )

    try:
        with urlopen(request, timeout=RSS_TIMEOUT_SECONDS) as response:
            feed = feedparser.parse(response.read())
    except OSError as error:
        raise RuntimeError("RSS를 불러오지 못했습니다.") from error

    if feed.bozo and not feed.entries:
        raise RuntimeError("RSS를 불러오지 못했습니다.")

    news_list = []

    for entry in feed.entries[:limit]:
        news_list.append(
            {
                "title": entry.get("title", "").strip(),
                "url": entry.get("link", "").strip(),
                "source_id": str(
                    entry.get("id", entry.get("guid", ""))
                ).strip(),
                "summary": entry.get("summary", "").strip(),
                "source": "연합뉴스TV",
                "category": category,
                "published_at": _parse_published_date(entry),
                "collected_at": datetime.now().isoformat(timespec="seconds"),
            }
        )

    return news_list
