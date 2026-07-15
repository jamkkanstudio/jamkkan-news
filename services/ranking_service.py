import re
from collections import Counter
from collections.abc import Iterable
from datetime import date, datetime
from typing import Callable

from services.time_service import KST, now_kst


BROAD_CATEGORIES = ("정치", "경제", "사회", "국제", "기타")
ARTICLE_TIME_FIELDS = ("published_at", "collected_at", "created_at")
CATEGORY_DIVERSITY_PENALTY = 10

IMPACT_SIGNALS = (
    "정부",
    "국회",
    "대통령",
    "법원",
    "헌재",
    "전국",
    "국민",
    "시민",
    "금리",
    "물가",
    "환율",
    "고용",
    "재난",
    "사고",
    "사망",
    "감염",
    "전쟁",
    "정상회담",
)
URGENCY_SIGNALS = (
    "긴급",
    "속보",
    "비상",
    "경보",
    "중단",
    "대피",
    "폭우",
    "태풍",
    "산불",
    "지진",
    "충돌",
    "체포",
    "시행",
)
TOPIC_STOPWORDS = {
    "관련",
    "대한",
    "오늘",
    "뉴스",
    "연합뉴스tv",
    "기자",
    "단독",
    "속보",
    "종합",
}


def _parse_datetime(value: object) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None

    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError:
        return None

    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=KST)
    return parsed.astimezone(KST)


def resolve_article_datetime(news: dict) -> datetime | None:
    """발행 시각을 우선하고 안전한 수집·생성 시각만 fallback으로 씁니다."""
    for field in ARTICLE_TIME_FIELDS:
        parsed = _parse_datetime(news.get(field))
        if parsed is not None:
            return parsed
    return None


def filter_news_for_date(
    news_list: list[dict],
    target_date: date,
) -> list[dict]:
    """유효한 기사 시각이 KST 대상 날짜인 기사만 반환합니다."""
    return [
        news
        for news in news_list
        if (
            (article_time := resolve_article_datetime(news)) is not None
            and article_time.date() == target_date
        )
    ]


def _matched_signal_count(text: str, signals: tuple[str, ...]) -> int:
    return sum(1 for signal in signals if signal.lower() in text)


def calculate_importance_breakdown(
    news: dict,
    *,
    now: datetime | None = None,
) -> dict[str, int]:
    """편집값·영향·시급성·KST 최신성의 설명 가능한 점수를 반환합니다."""
    try:
        stored_importance = int(news.get("importance", 50))
    except (TypeError, ValueError):
        stored_importance = 50
    stored_importance = min(max(stored_importance, 0), 100)

    text = " ".join(
        [
            str(news.get("title", "")),
            str(news.get("summary", "")),
        ]
    ).lower()

    editorial = round((stored_importance - 50) / 5)
    impact = min(_matched_signal_count(text, IMPACT_SIGNALS) * 5, 20)
    urgency = min(_matched_signal_count(text, URGENCY_SIGNALS) * 6, 18)

    freshness = 0
    article_time = resolve_article_datetime(news)
    current = now or now_kst()
    if current.tzinfo is None:
        current = current.replace(tzinfo=KST)
    else:
        current = current.astimezone(KST)

    if article_time is not None:
        age_hours = (current - article_time).total_seconds() / 3600
        if -1 <= age_hours <= 3:
            freshness = 12
        elif 3 < age_hours <= 8:
            freshness = 9
        elif 8 < age_hours <= 16:
            freshness = 6
        elif 16 < age_hours <= 24:
            freshness = 3

    total = min(max(50 + editorial + impact + urgency + freshness, 0), 100)
    return {
        "editorial": editorial,
        "impact": impact,
        "urgency": urgency,
        "freshness": freshness,
        "total": total,
    }


def calculate_importance(news: dict, *, now: datetime | None = None) -> int:
    return calculate_importance_breakdown(news, now=now)["total"]


def calculate_personal_score(
    news: dict,
    interests: list[str],
    *,
    now: datetime | None = None,
) -> int:
    """공통 중요도에 관심 주제 일치만 더해 별도 개인 알고리즘을 유지합니다."""
    searchable_text = " ".join(
        [
            str(news.get("title", "")),
            str(news.get("summary", "")),
            str(news.get("reason", "")),
            str(news.get("category", "")),
        ]
    ).lower()
    matched = sum(
        1
        for interest in interests
        if interest.strip() and interest.strip().lower() in searchable_text
    )
    return calculate_importance(news, now=now) + min(matched * 24, 48)


def _topic_tokens(title: object) -> set[str]:
    tokens = re.findall(r"[0-9a-z가-힣]+", str(title).lower())
    return {
        token
        for token in tokens
        if len(token) >= 2 and token not in TOPIC_STOPWORDS
    }


def is_same_topic(first: dict, second: dict) -> bool:
    """제목 핵심어 겹침으로 같은 사건의 후속·반복 기사를 설명 가능하게 묶습니다."""
    first_tokens = _topic_tokens(first.get("title", ""))
    second_tokens = _topic_tokens(second.get("title", ""))
    if not first_tokens or not second_tokens:
        return False
    if first_tokens == second_tokens:
        return True

    overlap = len(first_tokens & second_tokens)
    union = len(first_tokens | second_tokens)
    smaller = min(len(first_tokens), len(second_tokens))
    return (
        overlap >= 3 and overlap / smaller >= 0.6
    ) or (
        overlap >= 2 and overlap / union >= 0.5
    )


def _ranking_key(
    news: dict,
    scorer: Callable[[dict], int],
) -> tuple[int, float, str]:
    article_time = resolve_article_datetime(news)
    timestamp = article_time.timestamp() if article_time is not None else 0
    return (
        scorer(news),
        timestamp,
        str(news.get("id", "")),
    )


def _deduplicate_topics(
    news_list: list[dict],
    scorer: Callable[[dict], int],
) -> list[dict]:
    representatives: list[dict] = []
    for news in sorted(
        news_list,
        key=lambda item: _ranking_key(item, scorer),
        reverse=True,
    ):
        if any(is_same_topic(news, kept) for kept in representatives):
            continue
        representatives.append(news)
    return representatives


def select_diverse_news(
    news_list: list[dict],
    *,
    limit: int = 5,
    scorer: Callable[[dict], int] | None = None,
) -> list[dict]:
    """사건 중복을 제거하고 같은 분야 반복에 완만한 감점을 적용합니다."""
    if limit <= 0:
        return []
    score = scorer or calculate_importance
    remaining = _deduplicate_topics(news_list, score)
    selected: list[dict] = []
    category_counts: Counter[str] = Counter()

    while remaining and len(selected) < limit:
        chosen = max(
            remaining,
            key=lambda news: (
                score(news)
                - CATEGORY_DIVERSITY_PENALTY
                * category_counts[str(news.get("category", "기타"))],
                *_ranking_key(news, score)[1:],
            ),
        )
        selected.append(chosen)
        category_counts[str(chosen.get("category", "기타"))] += 1
        remaining.remove(chosen)

    return selected


def select_today_top_news(
    news_list: list[dict],
    *,
    target_date: date,
    limit: int = 5,
    now: datetime | None = None,
    excluded_ids: Iterable[str] = (),
) -> list[dict]:
    candidates = filter_news_for_date(news_list, target_date)
    ranked = select_diverse_news(
        candidates,
        limit=len(candidates),
        scorer=lambda news: calculate_importance(news, now=now),
    )
    excluded = {str(news_id) for news_id in excluded_ids}
    return [
        news
        for news in ranked
        if str(news.get("id", "")) not in excluded
    ][: max(limit, 0)]


def select_personal_top_news(
    news_list: list[dict],
    interests: list[str],
    *,
    target_date: date,
    limit: int = 5,
    now: datetime | None = None,
    excluded_ids: Iterable[str] = (),
) -> list[dict]:
    if not interests:
        return []
    candidates = filter_news_for_date(news_list, target_date)
    ranked = select_diverse_news(
        candidates,
        limit=len(candidates),
        scorer=lambda news: calculate_personal_score(
            news,
            interests,
            now=now,
        ),
    )
    excluded = {str(news_id) for news_id in excluded_ids}
    return [
        news
        for news in ranked
        if str(news.get("id", "")) not in excluded
    ][: max(limit, 0)]


def sort_news_by_importance(news_list: list[dict]) -> list[dict]:
    """기존 호출자를 위한 비변경 중요도 정렬입니다."""
    return sorted(
        news_list,
        key=lambda news: _ranking_key(news, calculate_importance),
        reverse=True,
    )
