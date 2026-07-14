KEYWORDS = {
    "금리": 20,
    "한국은행": 20,
    "코스피": 15,
    "코스닥": 15,
    "환율": 15,
    "반도체": 15,
    "AI": 20,
    "OpenAI": 20,
    "엔비디아": 20,
    "비트코인": 15,
    "테슬라": 15,
    "삼성": 10,
    "애플": 10,
    "미국": 10,
    "중국": 10,
    "부동산": 15,
    "주식": 15,
    "관세": 15,
}


def calculate_importance(news: dict) -> int:
    """
    뉴스의 중요도를 계산합니다.
    0~100점 사이의 점수를 반환합니다.
    """

    score = 50

    text = (
        news.get("title", "")
        + " "
        + news.get("summary", "")
    ).lower()

    for keyword, point in KEYWORDS.items():
        if keyword.lower() in text:
            score += point

    return min(score, 100)


def sort_news_by_importance(news_list: list[dict]) -> list[dict]:
    """
    중요도 순으로 뉴스를 정렬합니다.
    """

    for news in news_list:
        news["importance"] = calculate_importance(news)

    return sorted(
        news_list,
        key=lambda news: (
            news["importance"],
            news.get("created_at", ""),
        ),
        reverse=True,
    )
