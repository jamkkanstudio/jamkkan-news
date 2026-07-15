import unittest

from components.design_system import get_topic_counts


class DesignSystemTest(unittest.TestCase):
    def test_topic_counts_use_existing_categories_in_frequency_order(self) -> None:
        news = [
            {"category": "AI"},
            {"category": "경제"},
            {"category": "AI"},
            {"category": ""},
            {},
        ]

        self.assertEqual(
            get_topic_counts(news),
            [("AI", 2), ("기타", 2), ("경제", 1)],
        )

    def test_topic_counts_respect_display_limit(self) -> None:
        news = [{"category": category} for category in ["AI", "경제", "국제"]]

        self.assertEqual(get_topic_counts(news, limit=2), [("AI", 1), ("경제", 1)])


if __name__ == "__main__":
    unittest.main()
