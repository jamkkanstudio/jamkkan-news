import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent


class NewsSchedulerConfigTest(unittest.TestCase):
    def test_workflow_is_dispatch_only_and_labels_automation_source(self):
        workflow = (ROOT / ".github/workflows/collect-news.yml").read_text(
            encoding="utf-8"
        )

        self.assertIn("workflow_dispatch:", workflow)
        self.assertIn("trigger_source:", workflow)
        self.assertNotIn("\n  schedule:\n", workflow)

    def test_scheduler_reads_token_only_from_vault(self):
        scheduler = (ROOT / "supabase/news_collection_scheduler.sql").read_text(
            encoding="utf-8"
        )
        verification = (
            ROOT / "supabase/verify_news_collection_scheduler.sql"
        ).read_text(encoding="utf-8")

        self.assertIn("vault.decrypted_secrets", scheduler)
        self.assertIn("jamkkan_github_actions_token", scheduler)
        self.assertIn("'trigger_source', 'supabase-cron'", scheduler)
        self.assertNotIn("github_pat_", scheduler)
        self.assertNotIn("ghp_", scheduler)
        self.assertNotIn("vault.decrypted_secrets", verification)

    def test_rollback_unschedules_only_the_jamkkan_job(self):
        rollback = (
            ROOT / "supabase/rollback_news_collection_scheduler.sql"
        ).read_text(encoding="utf-8")

        self.assertIn("cron.unschedule", rollback)
        self.assertIn("jamkkan-news-collection", rollback)
        self.assertNotIn("drop extension", rollback.lower())


if __name__ == "__main__":
    unittest.main()
