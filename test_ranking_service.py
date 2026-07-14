import unittest

from services.ranking_service import sort_news_by_importance


class RankingServiceTest(unittest.TestCase):
    def test_equal_importance_prefers_newer_news(self) -> None:
        older = {
            "id": "older",
            "title": "일반 소식",
            "summary": "요약",
            "created_at": "2026-07-15T08:00:00+09:00",
        }
        newer = {
            "id": "newer",
            "title": "일반 소식",
            "summary": "요약",
            "created_at": "2026-07-15T09:00:00+09:00",
        }

        ranked = sort_news_by_importance([older, newer])

        self.assertEqual([news["id"] for news in ranked], ["newer", "older"])


if __name__ == "__main__":
    unittest.main()
