import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from services.news_collection_service import (
    CollectionError,
    article_id,
    canonicalize_url,
    collect_latest_news,
    collection_lock,
    format_collection_time_kst,
    is_collection_status_stale,
)


def rss_candidate(
    *,
    source_id: str = "article-1",
    url: str = "https://example.com/news/1",
    category: str = "경제",
) -> dict:
    return {
        "title": "테스트 기사",
        "url": url,
        "source_id": source_id,
        "summary": "테스트 기사 요약입니다.",
        "source": "테스트 언론사",
        "category": category,
        "published_at": "2026-07-15T09:00:00+09:00",
    }


class NewsCollectionServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.snapshot_loader = patch(
            "services.news_collection_service.load_global_daily_briefing",
            return_value={
                "date": "2026-07-15",
                "candidate_ids": ["frozen"],
            },
        ).start()
        self.addCleanup(patch.stopall)

    def test_collection_status_time_is_shown_in_kst(self) -> None:
        self.assertEqual(
            format_collection_time_kst("2026-07-15T07:37:01Z"),
            "2026-07-15 16:37 KST",
        )
        self.assertEqual(format_collection_time_kst("invalid"), "확인 불가")

    def test_collection_status_is_stale_after_thirty_minutes(self) -> None:
        now = datetime(2026, 7, 15, 8, 7, 1, tzinfo=timezone.utc)
        self.assertTrue(
            is_collection_status_stale(
                {"last_success_at": "2026-07-15T07:37:01Z"},
                now=now,
            )
        )
        self.assertFalse(
            is_collection_status_stale(
                {"last_success_at": "2026-07-15T07:37:02Z"},
                now=now,
            )
        )

    def test_canonical_url_removes_tracking_and_fragment(self) -> None:
        self.assertEqual(
            canonicalize_url(
                "HTTPS://Example.COM/news/?b=2&utm_source=test&a=1#top"
            ),
            "https://example.com/news?a=1&b=2",
        )

    def test_article_id_is_stable_for_source_id(self) -> None:
        first = article_id(
            "언론사",
            "source-1",
            "https://example.com/one",
        )
        second = article_id(
            "언론사",
            "source-1",
            "https://example.com/two",
        )
        self.assertEqual(first, second)

    def test_collect_adds_unique_news_to_supabase_before_json(self) -> None:
        operations = []

        with tempfile.TemporaryDirectory() as temp_dir:
            lock_file = Path(temp_dir) / "collection.lock"
            with (
                patch(
                    "services.news_collection_service.require_automation_admin"
                ),
                patch(
                    "services.news_collection_service.load_collection_status",
                    return_value=None,
                ),
                patch(
                    "services.news_collection_service.fetch_categorized_rss_news",
                    return_value=[rss_candidate()],
                ),
                patch(
                    "services.news_collection_service.load_news",
                    return_value=[],
                ),
                patch(
                    "services.news_collection_service.save_news_to_supabase",
                    side_effect=lambda news: operations.append("supabase") or True,
                ),
                patch(
                    "services.news_collection_service.save_news",
                    side_effect=lambda news: operations.append("json"),
                ) as save_json,
                patch(
                    "services.news_collection_service.upsert_setting",
                    return_value=True,
                ) as save_status,
            ):
                status = collect_latest_news(lock_file=lock_file)

        self.assertEqual(operations, ["supabase", "json"])
        self.assertEqual(status.added_count, 1)
        self.assertEqual(save_json.call_args.args[0][0]["category"], "경제")
        save_status.assert_called_once()

    def test_summary_failure_isolated_and_next_article_still_saves(self) -> None:
        candidates = [
            rss_candidate(),
            rss_candidate(
                source_id="article-2",
                url="https://example.com/news/2",
            ),
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            with (
                patch(
                    "services.news_collection_service.require_automation_admin"
                ),
                patch(
                    "services.news_collection_service.load_collection_status",
                    return_value=None,
                ),
                patch(
                    "services.news_collection_service.fetch_categorized_rss_news",
                    return_value=candidates,
                ),
                patch(
                    "services.news_collection_service.load_news",
                    return_value=[],
                ),
                patch(
                    "services.news_collection_service.create_collected_summary",
                    side_effect=[RuntimeError("parser bug"), "원문 핵심 요약"],
                ),
                patch(
                    "services.news_collection_service.save_news_to_supabase",
                    return_value=True,
                ),
                patch(
                    "services.news_collection_service.save_news"
                ) as save_json,
                patch(
                    "services.news_collection_service.upsert_setting",
                    return_value=True,
                ),
            ):
                status = collect_latest_news(
                    add_limit=2,
                    lock_file=Path(temp_dir) / "collection.lock",
                )

        saved = save_json.call_args.args[0]
        self.assertEqual(status.added_count, 2)
        self.assertEqual(saved[0]["summary"], "테스트 기사 요약입니다.")
        self.assertEqual(saved[1]["summary"], "원문 핵심 요약")

    def test_collect_deduplicates_canonical_url_and_source_id(self) -> None:
        existing = {
            "id": article_id(
                "테스트 언론사",
                "article-1",
                "https://example.com/news/1",
            ),
            "url": "https://example.com/news/1",
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            with (
                patch(
                    "services.news_collection_service.require_automation_admin"
                ),
                patch(
                    "services.news_collection_service.load_collection_status",
                    return_value=None,
                ),
                patch(
                    "services.news_collection_service.fetch_categorized_rss_news",
                    return_value=[
                        rss_candidate(),
                        rss_candidate(
                            source_id="article-2",
                            url=(
                                "https://example.com/news/1"
                                "?utm_source=rss#section"
                            ),
                        ),
                    ],
                ),
                patch(
                    "services.news_collection_service.load_news",
                    return_value=[existing],
                ),
                patch(
                    "services.news_collection_service.save_news_to_supabase"
                ) as save_supabase,
                patch(
                    "services.news_collection_service.save_news"
                ) as save_json,
                patch(
                    "services.news_collection_service.upsert_setting",
                    return_value=True,
                ),
            ):
                status = collect_latest_news(
                    lock_file=Path(temp_dir) / "collection.lock"
                )

        self.assertEqual(status.added_count, 0)
        self.assertEqual(status.duplicate_count, 2)
        save_supabase.assert_not_called()
        save_json.assert_not_called()

    def test_mirror_failure_does_not_write_json_and_records_safe_code(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            with (
                patch(
                    "services.news_collection_service.require_automation_admin"
                ),
                patch(
                    "services.news_collection_service.load_collection_status",
                    return_value={"last_success_at": "previous"},
                ),
                patch(
                    "services.news_collection_service.fetch_categorized_rss_news",
                    return_value=[rss_candidate()],
                ),
                patch(
                    "services.news_collection_service.load_news",
                    return_value=[],
                ),
                patch(
                    "services.news_collection_service.save_news_to_supabase",
                    return_value=False,
                ),
                patch(
                    "services.news_collection_service.save_news"
                ) as save_json,
                patch(
                    "services.news_collection_service.upsert_setting",
                    return_value=True,
                ) as save_status,
            ):
                with self.assertRaisesRegex(
                    CollectionError,
                    "news_mirror_failed",
                ):
                    collect_latest_news(
                        lock_file=Path(temp_dir) / "collection.lock"
                    )

        save_json.assert_not_called()
        saved_status = save_status.call_args.args[1]
        self.assertEqual(saved_status["failure_code"], "news_mirror_failed")
        self.assertEqual(saved_status["seen_fingerprints"], [])
        self.assertNotIn("url", saved_status)

    def test_seen_fingerprint_prevents_deleted_article_from_returning(self) -> None:
        candidate = rss_candidate()
        fingerprint_status = {}

        with tempfile.TemporaryDirectory() as temp_dir:
            lock_file = Path(temp_dir) / "collection.lock"
            with (
                patch(
                    "services.news_collection_service.require_automation_admin"
                ),
                patch(
                    "services.news_collection_service.load_collection_status",
                    side_effect=lambda: fingerprint_status or None,
                ),
                patch(
                    "services.news_collection_service.fetch_categorized_rss_news",
                    return_value=[candidate],
                ),
                patch(
                    "services.news_collection_service.load_news",
                    return_value=[],
                ),
                patch(
                    "services.news_collection_service.save_news_to_supabase",
                    return_value=True,
                ) as save_supabase,
                patch(
                    "services.news_collection_service.save_news"
                ) as save_json,
                patch(
                    "services.news_collection_service.upsert_setting",
                    side_effect=lambda key, value: fingerprint_status.update(value)
                    or True,
                ),
            ):
                first = collect_latest_news(lock_file=lock_file)
                second = collect_latest_news(lock_file=lock_file)

        self.assertEqual(first.added_count, 1)
        self.assertEqual(second.added_count, 0)
        self.assertEqual(second.duplicate_count, 1)
        self.assertEqual(save_supabase.call_count, 1)
        self.assertEqual(save_json.call_count, 1)

    def test_daily_snapshot_freezes_only_kst_today_candidates(self) -> None:
        self.snapshot_loader.return_value = None
        yesterday = {
            "id": "yesterday-id",
            "url": "https://example.com/yesterday",
            "title": "어제 기사",
            "created_at": "2026-07-14T23:59:59+09:00",
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            with (
                patch(
                    "services.news_collection_service.require_automation_admin"
                ),
                patch(
                    "services.news_collection_service.load_collection_status",
                    return_value=None,
                ),
                patch(
                    "services.news_collection_service.fetch_categorized_rss_news",
                    return_value=[rss_candidate()],
                ),
                patch(
                    "services.news_collection_service.load_news",
                    return_value=[yesterday],
                ),
                patch(
                    "services.news_collection_service.save_news_to_supabase",
                    return_value=True,
                ),
                patch("services.news_collection_service.save_news"),
                patch(
                    "services.news_collection_service.save_global_daily_briefing",
                    return_value=True,
                ) as save_briefing,
                patch(
                    "services.news_collection_service.upsert_setting",
                    return_value=True,
                ),
            ):
                collect_latest_news(
                    lock_file=Path(temp_dir) / "collection.lock",
                    now=datetime.fromisoformat(
                        "2026-07-15T09:00:00+09:00"
                    ),
                )

        snapshot = save_briefing.call_args.args[0]
        self.assertEqual(snapshot["date"], "2026-07-15")
        self.assertEqual(len(snapshot["candidate_ids"]), 1)
        self.assertNotIn("yesterday-id", snapshot["candidate_ids"])

    def test_active_lock_rejects_overlapping_run(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            lock_file = Path(temp_dir) / "collection.lock"
            with collection_lock(lock_file):
                with self.assertRaisesRegex(
                    CollectionError,
                    "collection_locked",
                ):
                    with collection_lock(lock_file):
                        pass


if __name__ == "__main__":
    unittest.main()
