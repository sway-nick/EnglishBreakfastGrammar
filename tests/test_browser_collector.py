"""
Unit tests for Browser-Assisted Remote CDP Acquisition Engine (TASK-005/006)
"""

import json
from pathlib import Path
import tempfile
import unittest

from pipeline.acquisition.browser_collector import (
    AcquisitionManifest,
    RemoteCdpClient,
    extract_subsequent_pages,
    url_to_cache_path,
    validate_page_content,
)


class TestBrowserCollector(unittest.TestCase):

    def test_validate_page_content_valid(self):
        valid_html = (
            "<!DOCTYPE html><html><head><title>Lesson</title></head><body>"
            "<div id='page-header' class='lesson-page-header'><h1>Grammar</h1></div>"
            "<div class='page-primary'>Content here</div>"
            + ("<p>Text</p>" * 1000)
            + "</body></html>"
        )
        is_valid, acq_result, reason = validate_page_content(valid_html)
        self.assertTrue(is_valid)
        self.assertEqual(acq_result, "success")
        self.assertEqual(reason, "")

    def test_validate_page_content_challenge(self):
        challenge_html = (
            "<!DOCTYPE html><html><head><title>Just a moment...</title></head><body>"
            "<div class='cf-browser-verification'>Checking your browser before accessing</div>"
            + ("x" * 20000)
            + "</body></html>"
        )
        is_valid, acq_result, reason = validate_page_content(challenge_html)
        self.assertFalse(is_valid)
        self.assertEqual(acq_result, "challenge_detected")
        self.assertIn("Cloudflare", reason)

    def test_validate_page_content_too_short(self):
        short_html = "<html><body>Short error</body></html>"
        is_valid, acq_result, reason = validate_page_content(short_html)
        self.assertFalse(is_valid)
        self.assertEqual(acq_result, "invalid_content")
        self.assertIn("too short", reason)

    def test_validate_page_content_missing_structure(self):
        long_but_foreign_html = "<html><body>" + ("<div>Some other site text</div>" * 1000) + "</body></html>"
        is_valid, acq_result, reason = validate_page_content(long_but_foreign_html)
        self.assertFalse(is_valid)
        self.assertEqual(acq_result, "invalid_content")
        self.assertIn("structural elements not found", reason)

    def test_url_to_cache_path(self):
        cache_dir = Path("/mock/cache")
        p = url_to_cache_path("https://test-english.com/grammar-points/a1/questions/", cache_dir)
        self.assertEqual(
            p.name,
            "https___test-english.com_grammar-points_a1_questions.html"
        )

    def test_extract_subsequent_pages(self):
        html_with_pages = """
        <div class="page-links">
            <span class="post-page-numbers current">1</span>
            <a href="https://test-english.com/grammar-points/a1/questions/2/" class="post-page-numbers">2</a>
            <a href="https://test-english.com/grammar-points/a1/questions/3/" class="post-page-numbers">3</a>
        </div>
        """
        urls = extract_subsequent_pages(html_with_pages, "https://test-english.com/grammar-points/a1/questions/")
        self.assertEqual(len(urls), 2)
        self.assertEqual(urls[0], "https://test-english.com/grammar-points/a1/questions/2/")
        self.assertEqual(urls[1], "https://test-english.com/grammar-points/a1/questions/3/")

    def test_manifest_recording_and_persistence(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            manifest_file = tmp_path / "manifest.json"
            manifest = AcquisitionManifest(manifest_file)

            # Record success
            dummy_file = tmp_path / "test.html"
            dummy_file.write_text("dummy content", encoding="utf-8")

            manifest.record_result(
                url="https://test-english.com/topic-1/",
                topic_id="topic-1",
                page=1,
                status=200,
                acquisition_result="success",
                content_validation="passed",
                local_cache_path=str(dummy_file),
                content_length=13,
                sha256="abc123hash",
            )
            # Record failure
            manifest.record_result(
                url="https://test-english.com/topic-2/",
                topic_id="topic-2",
                page=1,
                status=403,
                acquisition_result="challenge_detected",
                content_validation="failed",
                error="Challenge detected",
            )
            manifest.save()

            # Verify saved JSON
            self.assertTrue(manifest_file.exists())
            with open(manifest_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.assertEqual(data["total_cached_pages"], 1)
            self.assertIn("https://test-english.com/topic-1/", data["pages"])
            self.assertEqual(data["pages"]["https://test-english.com/topic-1/"]["acquisition_result"], "success")
            self.assertEqual(data["pages"]["https://test-english.com/topic-2/"]["content_validation"], "failed")

    def test_remote_cdp_client_offline_behavior(self):
        # Port 9999 is definitely not running CDP
        client = RemoteCdpClient(cdp_url="http://127.0.0.1:9999", timeout=1.0)
        self.assertFalse(client.check_connection())
        with self.assertRaises(ConnectionError) as ctx:
            client.acquire_page_html("https://test-english.com/some-page/")
        self.assertIn("Cannot connect to browser CDP", str(ctx.exception))

    def test_collect_topic_pages_and_offline_discovery_flow(self):
        """
        Tests the end-to-end flow:
        1. Acquisition tool collects topic and discovers Page 2.
        2. Manifest records results, status, sha256, content_validation.
        3. Offline catalog discover reads populated cache and marks topic 'complete'.
        """
        from pipeline.acquisition.browser_collector import collect_topic_pages
        from pipeline.catalog.source_catalog_builder import build_source_catalog

        topic_url = "https://test-english.com/grammar-points/a1/questions/"
        sub_url = "https://test-english.com/grammar-points/a1/questions/2/"

        page1_html = (
            "<!DOCTYPE html><html><head><title>Questions - Page 1</title></head><body>"
            "<div class='lesson-page-header'><h1>Questions: Word order</h1></div>"
            "<div class='page-primary'>Content for page 1</div>"
            "<div class='page-links'>"
            "<span class='post-page-numbers current'>1</span>"
            f"<a href='{sub_url}' class='post-page-numbers'>2</a>"
            "</div>"
            + ("<p>Text</p>" * 1000)
            + "</body></html>"
        )
        page2_html = (
            "<!DOCTYPE html><html><head><title>Questions - Page 2</title></head><body>"
            "<div class='lesson-page-header'><h1>Questions: Exercise 2</h1></div>"
            "<div class='page-primary'>Content for page 2</div>"
            + ("<p>Text</p>" * 1000)
            + "</body></html>"
        )

        class MockCdp:
            def acquire_page_html(self, url: str) -> str:
                if url == topic_url:
                    return page1_html
                elif url == sub_url:
                    return page2_html
                raise ValueError(f"Unknown URL {url}")

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            cache_dir = tmp_path / "cache" / "html"
            manifest_file = tmp_path / "cache" / "acquisition_manifest.json"
            cache_dir.mkdir(parents=True, exist_ok=True)

            manifest = AcquisitionManifest(manifest_file)
            mock_cdp = MockCdp()

            topic = {
                "topic_id": "questions",
                "title": "Questions: Word order and question words",
                "url": topic_url,
            }

            # 1. Run acquisition
            res = collect_topic_pages(
                topic=topic,
                cdp_client=mock_cdp,  # type: ignore
                manifest=manifest,
                cache_dir=cache_dir,
                delay=0.0,
            )
            self.assertEqual(res["acquired"], 2)
            self.assertEqual(res["failed"], 0)

            # 2. Verify cache files
            p1_cache = url_to_cache_path(topic_url, cache_dir)
            p2_cache = url_to_cache_path(sub_url, cache_dir)
            self.assertTrue(p1_cache.exists())
            self.assertTrue(p2_cache.exists())

            # 3. Verify manifest contents
            manifest.load()
            pages = manifest.data.get("pages", {})
            self.assertIn(topic_url, pages)
            self.assertIn(sub_url, pages)
            self.assertEqual(pages[topic_url]["acquisition_result"], "success")
            self.assertEqual(pages[topic_url]["content_validation"], "passed")
            self.assertEqual(pages[topic_url]["page"], 1)
            self.assertIsNotNone(pages[topic_url]["sha256"])
            self.assertEqual(pages[sub_url]["page"], 2)

            # 4. Prepare level page in cache for offline catalog builder
            level_url = "https://test-english.com/grammar-points/a1/"
            level_html = (
                "<!DOCTYPE html><html><body>"
                f"<a href='{topic_url}'>Questions: Word order</a>"
                "</body></html>"
            )
            level_cache = url_to_cache_path(level_url, cache_dir)
            level_cache.write_text(level_html, encoding="utf-8")

            # 5. Run catalog:discover --offline
            catalog = build_source_catalog(
                levels_to_scan=["a1"],
                cache_dir=cache_dir,
                offline=True,
            )

            # Verify catalog marked topic complete with confirmed 2 exercises!
            a1_level = catalog["levels"][0]
            self.assertEqual(len(a1_level["topics"]), 1)
            discovered_topic = a1_level["topics"][0]
            self.assertEqual(discovered_topic["topic_id"], "questions")
            self.assertEqual(discovered_topic["discovery_status"], "complete")
            self.assertEqual(discovered_topic["exercise_count"], 2)
            self.assertEqual(discovered_topic["exercises"][0]["url"], topic_url)
            self.assertEqual(discovered_topic["exercises"][1]["url"], sub_url)
            self.assertEqual(catalog["stats"]["topics_complete"], 1)
            self.assertEqual(catalog["stats"]["topics_partial"], 0)

    def test_idempotency_and_force(self):
        """Verifies skipping cached pages unless --force is specified."""
        from pipeline.acquisition.browser_collector import collect_topic_pages

        topic_url = "https://test-english.com/grammar-points/a1/questions/"
        page1_html = (
            "<!DOCTYPE html><html><body><div class='page-primary'><h1>Questions</h1></div>"
            + ("<p>Text</p>" * 1000)
            + "</body></html>"
        )

        call_count = 0
        class CountingCdp:
            def acquire_page_html(self, url: str) -> str:
                nonlocal call_count
                call_count += 1
                return page1_html

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            cache_dir = tmp_path / "cache" / "html"
            manifest_file = tmp_path / "cache" / "manifest.json"
            cache_dir.mkdir(parents=True, exist_ok=True)
            manifest = AcquisitionManifest(manifest_file)
            cdp = CountingCdp()
            topic = {"topic_id": "questions", "url": topic_url}

            # 1. Initial collection
            res1 = collect_topic_pages(topic, cdp, manifest, cache_dir, force=False)
            self.assertEqual(res1["acquired"], 1)
            self.assertEqual(call_count, 1)

            # 2. Idempotent re-run without force -> skipped
            res2 = collect_topic_pages(topic, cdp, manifest, cache_dir, force=False)
            self.assertEqual(res2["acquired"], 0)
            self.assertEqual(call_count, 1)  # No new network/CDP calls!

            # 3. Re-run with force=True -> re-acquired
            res3 = collect_topic_pages(topic, cdp, manifest, cache_dir, force=True)
            self.assertEqual(res3["acquired"], 1)
            self.assertEqual(call_count, 2)

    def test_failure_safety_challenge_and_invalid(self):
        """Verifies challenge/invalid pages are never saved to cache and recorded as failures."""
        from pipeline.acquisition.browser_collector import collect_topic_pages

        topic_url = "https://test-english.com/grammar-points/a1/questions/"
        challenge_html = "<!DOCTYPE html><html><head><title>Just a moment...</title></head><body>cf-browser-verification" + ("x" * 20000) + "</body></html>"

        class ChallengeCdp:
            def acquire_page_html(self, url: str) -> str:
                return challenge_html

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            cache_dir = tmp_path / "cache" / "html"
            manifest_file = tmp_path / "cache" / "manifest.json"
            cache_dir.mkdir(parents=True, exist_ok=True)
            manifest = AcquisitionManifest(manifest_file)
            topic = {"topic_id": "questions", "url": topic_url}

            # 1. Collect challenge page
            res = collect_topic_pages(topic, ChallengeCdp(), manifest, cache_dir)
            self.assertEqual(res["acquired"], 0)
            self.assertEqual(res["failed"], 1)

            # 2. Ensure NO HTML file was saved to cache
            cache_path = url_to_cache_path(topic_url, cache_dir)
            self.assertFalse(cache_path.exists())

            # 3. Ensure manifest records failure and null cache path
            manifest.load()
            rec = manifest.data["pages"][topic_url]
            self.assertEqual(rec["acquisition_result"], "challenge_detected")
            self.assertEqual(rec["content_validation"], "failed")
            self.assertIsNone(rec["local_cache_path"])
            self.assertIsNone(rec["sha256"])


if __name__ == "__main__":
    unittest.main()

