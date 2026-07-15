import unittest
from pathlib import Path
from unittest.mock import patch

from services.article_summary_service import (
    clean_article_text,
    create_collected_summary,
    create_extractive_brief,
    extract_article_text,
)


FIXTURE = Path("tests/fixtures/yonhap_article.html")
TITLE = "비강남 신축이 강남보다 비싸다…분상제 역설도"


class ArticleSummaryServiceTest(unittest.TestCase):
    def fixture_text(self) -> str:
        return FIXTURE.read_text(encoding="utf-8")

    def test_source_fixture_removes_roles_credits_duplicates_and_title(self) -> None:
        extracted = extract_article_text(self.fixture_text())
        cleaned = clean_article_text(extracted, title=TITLE)

        self.assertIn("서울 아파트 분양가", extracted)
        self.assertNotIn("[앵커]", cleaned)
        self.assertNotIn("정다미 기자", cleaned)
        self.assertNotIn("연합뉴스TV 정다미", cleaned)
        self.assertNotIn("자료사진", cleaned)
        self.assertNotIn("기사문의", cleaned)
        self.assertNotIn(TITLE, cleaned)
        self.assertEqual(cleaned.count("8천만원을 돌파"), 1)

    def test_extractive_brief_uses_only_source_sentences_under_limit(self) -> None:
        extracted = extract_article_text(self.fixture_text())
        brief = create_extractive_brief(extracted, title=TITLE)

        self.assertIsNotNone(brief)
        self.assertLessEqual(len(brief), 140)
        for sentence in brief.split(". "):
            self.assertIn(sentence.rstrip(".")[:20], extracted)

    def test_timeout_falls_back_to_existing_rss_description(self) -> None:
        candidate = {
            "title": TITLE,
            "summary": "RSS에서 받은 안전한 설명입니다.",
            "source": "연합뉴스TV",
            "url": "https://www.yonhapnewstv.co.kr/news/TEST123",
        }
        with patch(
            "services.article_summary_service.fetch_article_html",
            side_effect=TimeoutError,
        ):
            summary = create_collected_summary(candidate)

        self.assertEqual(summary, "RSS에서 받은 안전한 설명입니다.")

    def test_unapproved_source_uses_rss_without_fetching(self) -> None:
        candidate = {
            "title": "다른 출처 기사",
            "summary": "다른 출처의 RSS 설명입니다.",
            "source": "다른 언론사",
            "url": "https://example.com/article",
        }
        with patch(
            "services.article_summary_service.fetch_article_html"
        ) as fetch:
            summary = create_collected_summary(candidate)

        self.assertEqual(summary, "다른 출처의 RSS 설명입니다.")
        fetch.assert_not_called()

    def test_unapproved_article_url_never_opens_network(self) -> None:
        candidate = {
            "title": TITLE,
            "summary": "허용되지 않은 URL의 RSS 설명입니다.",
            "source": "연합뉴스TV",
            "url": "https://example.com/private",
        }
        with patch("services.article_summary_service.urlopen") as open_url:
            summary = create_collected_summary(candidate)

        self.assertEqual(summary, "허용되지 않은 URL의 RSS 설명입니다.")
        open_url.assert_not_called()


if __name__ == "__main__":
    unittest.main()
