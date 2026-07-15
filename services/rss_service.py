from datetime import datetime
from email.utils import parsedate_to_datetime
from urllib.request import Request, urlopen

import feedparser

from services.time_service import KST, now_kst


RSS_FEEDS = {
    "최신": "https://www.yonhapnewstv.co.kr/browse/feed/",
    "정치": "https://www.yonhapnewstv.co.kr/category/news/politics/feed/",
    "경제": "https://www.yonhapnewstv.co.kr/category/news/economy/feed/",
    "사회": "https://www.yonhapnewstv.co.kr/category/news/society/feed/",
    "국제": "https://www.yonhapnewstv.co.kr/category/news/international/feed/",
}
RSS_CATEGORIES = ("정치", "경제", "사회", "국제")

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
                "collected_at": now_kst().isoformat(timespec="seconds"),
            }
        )

    return news_list


def _rss_sort_time(candidate: dict) -> datetime:
    for field in ("published_at", "collected_at"):
        value = candidate.get(field)
        if not isinstance(value, str) or not value.strip():
            continue
        try:
            parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
        except ValueError:
            continue
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=KST)
        return parsed.astimezone(KST)
    return datetime.min.replace(tzinfo=KST)


def fetch_categorized_rss_news(limit: int = 20) -> list[dict]:
    """광역 카테고리 피드를 합치고 기사 ID·URL 중복을 안정적으로 제거합니다."""
    if limit <= 0:
        return []

    merged: list[dict] = []
    seen: set[str] = set()
    successful_feeds = 0

    for category in RSS_CATEGORIES:
        try:
            category_news = fetch_rss_news(category=category, limit=limit)
        except RuntimeError:
            continue
        successful_feeds += 1
        for candidate in category_news:
            identity = (
                str(candidate.get("source_id", "")).strip()
                or str(candidate.get("url", "")).strip().rstrip("/")
            )
            if not identity or identity in seen:
                continue
            seen.add(identity)
            merged.append(candidate)

    if successful_feeds == 0:
        raise RuntimeError("분류 RSS를 불러오지 못했습니다.")

    return sorted(
        merged,
        key=lambda candidate: (
            _rss_sort_time(candidate),
            str(candidate.get("source_id", "")),
            str(candidate.get("url", "")),
        ),
        reverse=True,
    )[:limit]
