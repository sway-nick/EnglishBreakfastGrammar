"""
Unit tests for pipeline/catalog/source_catalog_builder.py (TASK-005)

Verifies:
- Parsing level listing HTML into topics
- Filtering service/content pages
- Parsing exercise pagination (.page-links)
- Single-page fallback for topics without pagination
- Dynamic statistics computation (never hardcoded)
- Markdown summary report generation
"""

import sys
from pathlib import Path
import unittest

# Ensure repo root and pipeline/catalog are in sys.path
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
CATALOG_DIR = REPO_ROOT / "pipeline" / "catalog"
if str(CATALOG_DIR) not in sys.path:
    sys.path.insert(0, str(CATALOG_DIR))

from source_catalog_builder import (
    clean_title,
    parse_level_topics_html,
    parse_exercise_pagination_html,
    compute_catalog_stats,
    generate_summary_markdown,
)


class TestSourceCatalog(unittest.TestCase):

    def test_clean_title(self):
        self.assertEqual(
            clean_title("Present simple forms of &#039;to be&#039;: am/is/are - Test-English"),
            "Present simple forms of 'to be': am/is/are"
        )
        self.assertEqual(
            clean_title("Past Simple - Page 2 of 4 - Test-English"),
            "Past Simple"
        )
        self.assertEqual(clean_title(""), "")

    def test_parse_level_topics_from_html(self):
        sample_html = """
        <html>
        <body>
          <div class="topics">
            <a href="https://test-english.com/grammar-points/a1/present-simple-forms-of-to-be/">
              Present simple forms of &#039;to be&#039;: am/is/are - Test-English
            </a>
            <a href="https://test-english.com/grammar-points/a1/this-that-these-those/">
              This, that, these, those
            </a>
            <!-- Duplicate link that should be deduplicated -->
            <a href="https://test-english.com/grammar-points/a1/this-that-these-those/">
              This, that, these, those
            </a>
            <!-- Service / contents page that must be excluded -->
            <a href="https://test-english.com/grammar-points/a1/contents-a1/">
              Table of grammar contents - A1
            </a>
            <!-- Pagination / subpage that must be excluded -->
            <a href="https://test-english.com/grammar-points/a1/present-simple-forms-of-to-be/2/">
              Page 2
            </a>
            <!-- Different level that must be ignored -->
            <a href="https://test-english.com/grammar-points/a2/past-simple/">
              Past Simple
            </a>
          </div>
        </body>
        </html>
        """
        topics = parse_level_topics_html(sample_html, "a1")
        self.assertEqual(len(topics), 2)

        t1 = topics[0]
        self.assertEqual(t1["topic_id"], "present-simple-forms-of-to-be")
        self.assertEqual(t1["title"], "Present simple forms of 'to be': am/is/are")
        self.assertEqual(t1["url"], "https://test-english.com/grammar-points/a1/present-simple-forms-of-to-be/")
        self.assertEqual(t1["order"], 1)

        t2 = topics[1]
        self.assertEqual(t2["topic_id"], "this-that-these-those")
        self.assertEqual(t2["title"], "This, that, these, those")
        self.assertEqual(t2["url"], "https://test-english.com/grammar-points/a1/this-that-these-those/")
        self.assertEqual(t2["order"], 2)

    def test_parse_exercise_pagination_multi_page(self):
        sample_topic_html = """
        <html>
        <body>
          <div class="content">
            <h1>Present simple forms of 'to be'</h1>
            <div class="page-links">
              Exercises:
              <span aria-current="page" class="post-page-numbers current"><span class="hoverable">1</span></span>
              <a class="post-page-numbers" href="https://test-english.com/grammar-points/a1/present-simple-forms-of-to-be/2/"><span class="hoverable">2</span></a>
              <a class="post-page-numbers" href="https://test-english.com/grammar-points/a1/present-simple-forms-of-to-be/3/"><span class="hoverable">3</span></a>
              <a class="post-page-numbers" href="https://test-english.com/grammar-points/a1/present-simple-forms-of-to-be/4/"><span class="hoverable">4</span></a>
            </div>
          </div>
        </body>
        </html>
        """
        topic_url = "https://test-english.com/grammar-points/a1/present-simple-forms-of-to-be/"
        exercises = parse_exercise_pagination_html(sample_topic_html, topic_url)

        self.assertEqual(len(exercises), 4)
        self.assertEqual(exercises[0], {"order": 1, "page": 1, "url": "https://test-english.com/grammar-points/a1/present-simple-forms-of-to-be/"})
        self.assertEqual(exercises[1], {"order": 2, "page": 2, "url": "https://test-english.com/grammar-points/a1/present-simple-forms-of-to-be/2/"})
        self.assertEqual(exercises[2], {"order": 3, "page": 3, "url": "https://test-english.com/grammar-points/a1/present-simple-forms-of-to-be/3/"})
        self.assertEqual(exercises[3], {"order": 4, "page": 4, "url": "https://test-english.com/grammar-points/a1/present-simple-forms-of-to-be/4/"})

    def test_parse_exercise_pagination_single_page(self):
        sample_single_html = """
        <html>
        <body>
          <div class="content">
            <h1>Single Page Topic</h1>
            <p>Some explanation and one quiz without page links.</p>
          </div>
        </body>
        </html>
        """
        topic_url = "https://test-english.com/grammar-points/a1/single-topic/"
        exercises = parse_exercise_pagination_html(sample_single_html, topic_url)

        self.assertEqual(len(exercises), 1)
        self.assertEqual(exercises[0], {"order": 1, "page": 1, "url": "https://test-english.com/grammar-points/a1/single-topic/"})

    def test_catalog_statistics_dynamic_calculation(self):
        # Sample levels structure
        levels_data = [
            {
                "level_id": "a1",
                "topics": [
                    {"exercise_count": 4},
                    {"exercise_count": 3},
                ],
            },
            {
                "level_id": "a2",
                "topics": [
                    {"exercise_count": 3},
                    {"exercise_count": 2},
                    {"exercise_count": 1},
                ],
            },
        ]

        stats = compute_catalog_stats(levels_data)
        self.assertEqual(stats["total_levels"], 2)
        self.assertEqual(stats["total_topics"], 5)
        self.assertEqual(stats["total_exercises"], 13)

        # Empty levels
        empty_stats = compute_catalog_stats([])
        self.assertEqual(empty_stats["total_levels"], 0)
        self.assertEqual(empty_stats["total_topics"], 0)
        self.assertEqual(empty_stats["total_exercises"], 0)

    def test_summary_markdown_generation(self):
        catalog = {
            "source_provider": "test-english",
            "base_url": "https://test-english.com",
            "discovered_at": "2026-09-30T12:00:00Z",
            "stats": {
                "total_levels": 1,
                "total_topics": 2,
                "total_exercises": 7,
            },
            "levels": [
                {
                    "level_id": "a1",
                    "title": "A1 Elementary",
                    "url": "https://test-english.com/grammar-points/a1/",
                    "topic_count": 2,
                    "exercise_count": 7,
                    "topics": [
                        {
                            "topic_id": "topic-1",
                            "order": 1,
                            "title": "Topic 1",
                            "url": "https://test-english.com/grammar-points/a1/topic-1/",
                            "exercise_count": 4,
                        },
                        {
                            "topic_id": "topic-2",
                            "order": 2,
                            "title": "Topic 2",
                            "url": "https://test-english.com/grammar-points/a1/topic-2/",
                            "exercise_count": 3,
                        },
                    ],
                }
            ],
        }

        md = generate_summary_markdown(catalog)
        self.assertIn("# Source Catalog Summary", md)
        self.assertIn("Total Topics**: 2", md)
        self.assertIn("Total Exercises (Discovered)**: 7", md)
        self.assertIn("`a1`", md)
        self.assertIn("Topic 1", md)


if __name__ == "__main__":
    unittest.main()
