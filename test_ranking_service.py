import unittest
from datetime import date, datetime

from services.ranking_service import (
    calculate_importance,
    filter_news_for_date,
    is_same_topic,
    resolve_article_datetime,
    select_diverse_news,
    select_personal_top_news,
    select_today_top_news,
    sort_news_by_importance,
)
from services.time_service import KST


NOW = datetime(2026, 7, 15, 12, 0, tzinfo=KST)


def article(
    article_id: str,
    title: str,
    *,
    category: str = "사회",
    created_at: str = "2026-07-15T09:00:00+09:00",
    **extra,
) -> dict:
    return {
        "id": article_id,
        "title": title,
        "summary": "요약",
        "category": category,
        "importance": 50,
        "created_at": created_at,
        **extra,
    }


class RankingServiceTest(unittest.TestCase):
    def test_article_time_prefers_published_then_safe_fallbacks(self) -> None:
        news = article(
            "time",
            "시각 테스트",
            published_at="invalid",
            collected_at="2026-07-15T08:00:00Z",
            created_at="2026-07-14T09:00:00+09:00",
        )

        resolved = resolve_article_datetime(news)

        self.assertIsNotNone(resolved)
        self.assertEqual(resolved.isoformat(), "2026-07-15T17:00:00+09:00")

        news["published_at"] = "2026-07-15T07:30:00+09:00"
        self.assertEqual(
            resolve_article_datetime(news).isoformat(),
            "2026-07-15T07:30:00+09:00",
        )

    def test_today_filter_excludes_old_invalid_and_future_day_articles(self) -> None:
        candidates = [
            article("today", "오늘 기사"),
            article(
                "yesterday",
                "어제 기사",
                created_at="2026-07-14T23:59:59+09:00",
            ),
            article(
                "tomorrow",
                "내일 기사",
                created_at="2026-07-16T00:00:00+09:00",
            ),
            article("invalid", "시각 오류", created_at="unknown"),
        ]

        filtered = filter_news_for_date(candidates, date(2026, 7, 15))

        self.assertEqual([news["id"] for news in filtered], ["today"])

    def test_same_event_headlines_are_deduplicated(self) -> None:
        first = article("one", "서울 폭우 도로 침수 시민 대피")
        follow_up = article("two", "서울 폭우 시민 대피 도로 통제")
        different = article("three", "국회 연금 개혁안 본회의 통과", category="정치")

        self.assertTrue(is_same_topic(first, follow_up))
        self.assertFalse(is_same_topic(first, different))
        selected = select_diverse_news(
            [first, follow_up, different],
            scorer=lambda news: {"one": 80, "two": 70, "three": 60}[
                news["id"]
            ],
        )
        self.assertEqual([news["id"] for news in selected], ["one", "three"])

    def test_category_penalty_prevents_one_field_from_filling_top_five(self) -> None:
        candidates = [
            article("econ-1", "기준금리 결정", category="경제"),
            article("econ-2", "수출 지표 발표", category="경제"),
            article("econ-3", "증시 거래 동향", category="경제"),
            article("society", "학교 안전 기준 개정", category="사회"),
            article("world", "정상회담 공동 성명", category="국제"),
        ]
        scores = {
            "econ-1": 90,
            "econ-2": 88,
            "econ-3": 86,
            "society": 84,
            "world": 83,
        }

        selected = select_diverse_news(
            candidates,
            scorer=lambda news: scores[news["id"]],
        )

        self.assertEqual(selected[0]["id"], "econ-1")
        self.assertLess(
            [news["id"] for news in selected].index("society"),
            [news["id"] for news in selected].index("econ-2"),
        )

    def test_importance_balances_impact_urgency_and_freshness(self) -> None:
        high_impact = article(
            "impact",
            "정부 전국 산불 비상 대피 시행",
            created_at="2026-07-15T11:00:00+09:00",
        )
        finance_only = article(
            "finance",
            "반도체 주식 시장 전망",
            category="경제",
            created_at="2026-07-15T11:00:00+09:00",
        )

        self.assertGreater(
            calculate_importance(high_impact, now=NOW),
            calculate_importance(finance_only, now=NOW),
        )

    def test_both_rankings_only_use_kst_today_candidates(self) -> None:
        candidates = [
            article("today-social", "전국 학교 안전 점검", category="사회"),
            article("today-ai", "AI 산업 지원 정책", category="경제"),
            article(
                "old-ai",
                "AI 기업 대규모 투자",
                category="경제",
                created_at="2026-07-14T23:59:59+09:00",
            ),
        ]

        public = select_today_top_news(
            candidates,
            target_date=date(2026, 7, 15),
            now=NOW,
        )
        personal = select_personal_top_news(
            candidates,
            ["AI"],
            target_date=date(2026, 7, 15),
            now=NOW,
        )

        self.assertNotIn("old-ai", [news["id"] for news in public])
        self.assertNotIn("old-ai", [news["id"] for news in personal])
        self.assertEqual(personal[0]["id"], "today-ai")

    def test_equal_importance_prefers_newer_news_without_mutating_rows(self) -> None:
        older = article(
            "older",
            "일반 소식 하나",
            created_at="2026-07-15T08:00:00+09:00",
        )
        newer = article(
            "newer",
            "일반 소식 둘",
            created_at="2026-07-15T09:00:00+09:00",
        )

        ranked = sort_news_by_importance([older, newer])

        self.assertEqual([news["id"] for news in ranked], ["newer", "older"])
        self.assertEqual(older["importance"], 50)


if __name__ == "__main__":
    unittest.main()
