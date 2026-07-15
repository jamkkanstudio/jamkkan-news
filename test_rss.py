import unittest
from types import SimpleNamespace
from unittest.mock import patch

from services.rss_service import fetch_categorized_rss_news, fetch_rss_news


class FetchRssNewsTest(unittest.TestCase):
    def test_fetch_rss_news_normalizes_feed_entry(self) -> None:
        feed = SimpleNamespace(
            bozo=False,
            entries=[
                {
                    "title": " 테스트 기사 ",
                    "link": " https://example.com/news ",
                    "summary": "테스트 요약",
                    "published": "Wed, 15 Jul 2026 09:00:00 +0900",
                }
            ],
        )

        response = unittest.mock.MagicMock()
        response.__enter__.return_value.read.return_value = b"rss"

        with (
            patch("services.rss_service.urlopen", return_value=response),
            patch("services.rss_service.feedparser.parse", return_value=feed),
        ):
            news_list = fetch_rss_news(category="경제", limit=1)

        self.assertEqual(len(news_list), 1)
        self.assertEqual(news_list[0]["title"], "테스트 기사")
        self.assertEqual(news_list[0]["url"], "https://example.com/news")
        self.assertEqual(news_list[0]["category"], "경제")
        self.assertEqual(news_list[0]["source_id"], "")

    def test_fetch_rss_news_rejects_unknown_category(self) -> None:
        with self.assertRaises(ValueError):
            fetch_rss_news(category="지원하지 않음")

    def test_categorized_feed_keeps_broad_category_and_deduplicates(self) -> None:
        shared = {
            "title": "공통 기사",
            "url": "https://example.com/shared",
            "source_id": "shared-id",
            "published_at": "2026-07-15T09:00:00+09:00",
        }

        def category_result(*, category: str, limit: int) -> list[dict]:
            if category == "정치":
                return [{**shared, "category": "정치"}]
            if category == "경제":
                return [
                    {**shared, "category": "경제"},
                    {
                        "title": "경제 기사",
                        "url": "https://example.com/economy",
                        "source_id": "economy-id",
                        "category": "경제",
                        "published_at": "2026-07-15T10:00:00+09:00",
                    },
                ]
            return []

        with patch(
            "services.rss_service.fetch_rss_news",
            side_effect=category_result,
        ):
            news_list = fetch_categorized_rss_news(limit=20)

        self.assertEqual(len(news_list), 2)
        self.assertEqual(news_list[0]["category"], "경제")
        shared_result = next(
            news for news in news_list if news["source_id"] == "shared-id"
        )
        self.assertEqual(shared_result["category"], "정치")

    def test_categorized_feed_keeps_working_when_one_category_fails(self) -> None:
        def category_result(*, category: str, limit: int) -> list[dict]:
            if category == "정치":
                raise RuntimeError("feed unavailable")
            if category == "사회":
                return [
                    {
                        "title": "사회 기사",
                        "url": "https://example.com/society",
                        "source_id": "society-id",
                        "category": "사회",
                        "published_at": "2026-07-15T10:00:00+09:00",
                    }
                ]
            return []

        with patch(
            "services.rss_service.fetch_rss_news",
            side_effect=category_result,
        ):
            news_list = fetch_categorized_rss_news(limit=20)

        self.assertEqual([news["category"] for news in news_list], ["사회"])


if __name__ == "__main__":
    unittest.main()
