import unittest
from types import SimpleNamespace
from unittest.mock import patch

from services.rss_service import fetch_rss_news


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


if __name__ == "__main__":
    unittest.main()
