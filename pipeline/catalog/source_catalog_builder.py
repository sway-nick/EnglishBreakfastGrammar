"""
Source Catalog Discovery Engine (TASK-005)

Discovers all available CEFR grammar levels, topics, and exercise pages from
the source site (test-english.com), building a persistent canonical catalog.

Key Features:
- Discovers all levels: A1, A2, B1, B1-B2, B2, C1, Shorts
- Extracts canonical topic URLs, titles, slugs, and orders
- Discovers exercise pagination via .page-links container
- Single-page fallback for topics without pagination
- Dynamic calculation of statistics (total_topics, total_exercises)
- Local caching & offline execution mode
- Exports data/catalog/source_catalog.json and data/catalog/source_catalog_summary.md
"""

from __future__ import annotations

import argparse
import datetime
import html
import json
from pathlib import Path
import re
import sys
import time
from typing import Any, Dict, List, Optional
import urllib.error
import urllib.parse
import urllib.request

from bs4 import BeautifulSoup


# ---------------------------------------------------------------------------
# CONFIGURATION & CONSTANTS
# ---------------------------------------------------------------------------

DEFAULT_BASE_URL = "https://test-english.com"

DEFAULT_LEVELS = [
    {"level_id": "a1", "title": "A1 Elementary", "url": "https://test-english.com/grammar-points/a1/"},
    {"level_id": "a2", "title": "A2 Pre-intermediate", "url": "https://test-english.com/grammar-points/a2/"},
    {"level_id": "b1", "title": "B1 Intermediate", "url": "https://test-english.com/grammar-points/b1/"},
    {"level_id": "b1-b2", "title": "B1+ Upper-intermediate", "url": "https://test-english.com/grammar-points/b1-b2/"},
    {"level_id": "b2", "title": "B2 Pre-advanced", "url": "https://test-english.com/grammar-points/b2/"},
    {"level_id": "c1", "title": "C1 Advanced", "url": "https://test-english.com/grammar-points/c1/"},
    {"level_id": "shorts", "title": "Grammar Shorts", "url": "https://test-english.com/grammar-points/shorts/"},
]

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


# ---------------------------------------------------------------------------
# HTTP & CACHING HELPERS
# ---------------------------------------------------------------------------

class ContentFetcher:
    """Handles HTTP requests with caching, headers, and polite rate limiting."""

    def __init__(self, cache_dir: Optional[Path] = None, offline: bool = False, delay: float = 0.3):
        self.cache_dir = cache_dir
        self.offline = offline
        self.delay = delay
        if self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _url_to_cache_path(self, url: str) -> Optional[Path]:
        if not self.cache_dir:
            return None
        # Sanitize URL to safe filename
        safe_name = re.sub(r"[^a-zA-Z0-9_\-\.]", "_", url).strip("_")
        if len(safe_name) > 180:
            safe_name = safe_name[:180] + "_" + str(abs(hash(url)))
        return self.cache_dir / f"{safe_name}.html"

    def fetch(self, url: str) -> str:
        """Fetches page content from cache or network."""
        cache_path = self._url_to_cache_path(url)
        if cache_path and cache_path.exists():
            return cache_path.read_text(encoding="utf-8", errors="replace")

        if self.offline:
            raise FileNotFoundError(f"[OFFLINE] Cache miss for URL: {url}")

        time.sleep(self.delay)
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})

        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                raw_bytes = resp.read()
                encoding = resp.headers.get_content_charset() or "utf-8"
                content = raw_bytes.decode(encoding, errors="replace")
        except urllib.error.URLError as err:
            raise RuntimeError(f"Network error fetching {url}: {err}") from err

        if cache_path:
            cache_path.write_text(content, encoding="utf-8", errors="replace")

        return content


# ---------------------------------------------------------------------------
# PARSING LOGIC
# ---------------------------------------------------------------------------

def clean_title(raw_title: str) -> str:
    """Normalizes title text, unescapes entities, and strips source suffixes."""
    if not raw_title:
        return ""
    text = html.unescape(raw_title)
    text = re.sub(r"\s*-\s*Test-English\s*$", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*-\s*Page\s+\d+\s+of\s+\d+", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def parse_level_topics_html(html_content: str, level_id: str, base_url: str = DEFAULT_BASE_URL) -> List[Dict[str, Any]]:
    """
    Parses a level listing page and returns an ordered list of topics.
    Excludes service links (e.g. contents-a1, pagination pages).
    """
    soup = BeautifulSoup(html_content, "html.parser")
    pattern = re.compile(rf"^https?://[^/]+/grammar-points/{re.escape(level_id)}/([^/]+)/?$")

    topics: List[Dict[str, Any]] = []
    seen_urls = set()

    for a in soup.find_all("a", href=True):
        raw_href = a["href"].strip()
        full_url = urllib.parse.urljoin(base_url, raw_href)

        m = pattern.match(full_url)
        if not m:
            continue

        slug = m.group(1).strip()
        # Ignore service / contents pages
        if slug.startswith("contents-") or slug.startswith("content-") or slug.isdigit():
            continue

        clean_url = f"{DEFAULT_BASE_URL}/grammar-points/{level_id}/{slug}/"
        if clean_url in seen_urls:
            continue
        seen_urls.add(clean_url)

        title = clean_title(a.get_text(strip=True))
        if not title:
            # Fallback to slug formatted as title
            title = slug.replace("-", " ").capitalize()

        topics.append({
            "topic_id": slug,
            "title": title,
            "url": clean_url,
        })

    # Number order
    for idx, topic in enumerate(topics, start=1):
        topic["order"] = idx

    return topics


def parse_exercise_pagination_html(html_content: str, topic_url: str) -> List[Dict[str, Any]]:
    """
    Extracts all exercise URLs from a topic's Page 1 HTML.
    Looks for WordPress .page-links container.
    Returns list of exercise dictionaries: [{"order": 1, "page": 1, "url": "..."}].
    If no pagination found, returns single-page fallback.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    page_links_div = soup.select_one(".page-links")

    # Base canonical topic url with trailing slash
    clean_topic_url = topic_url.rstrip("/") + "/"

    exercises = [
        {"order": 1, "page": 1, "url": clean_topic_url}
    ]

    if not page_links_div:
        return exercises

    # Find additional page links in .page-links (e.g. /2/, /3/, /4/)
    found_pages: Dict[int, str] = {1: clean_topic_url}

    for a in page_links_div.find_all("a", href=True):
        href = a["href"].strip()
        full_href = urllib.parse.urljoin(clean_topic_url, href)
        # Check if URL ends with /{digit}/ or /{digit}
        m = re.search(r"/(\d+)/?$", full_href)
        if m:
            page_num = int(m.group(1))
            if page_num > 1:
                norm_page_url = f"{clean_topic_url}{page_num}/"
                found_pages[page_num] = norm_page_url

    # Sort pages by page number
    sorted_pages = sorted(found_pages.items(), key=lambda kv: kv[0])
    result = []
    for order_idx, (p_num, p_url) in enumerate(sorted_pages, start=1):
        result.append({
            "order": order_idx,
            "page": p_num,
            "url": p_url,
        })

    return result


def compute_catalog_stats(levels_data: List[Dict[str, Any]], network_errors: int = 0) -> Dict[str, int]:
    """
    Dynamically computes catalog statistics from the discovered tree.
    Never uses hardcoded constants.
    """
    all_topics = [t for lvl in levels_data for t in lvl.get("topics", [])]
    total_levels = len(levels_data)
    total_topics = len(all_topics)
    total_exercises = sum(t.get("exercise_count", 0) for t in all_topics)
    topics_complete = sum(1 for t in all_topics if t.get("discovery_status") == "complete")
    topics_partial = sum(1 for t in all_topics if t.get("discovery_status") == "partial")
    topics_with_pagination = sum(1 for t in all_topics if t.get("exercise_count", 0) > 1)
    topics_single_page_fallback = sum(1 for t in all_topics if t.get("exercise_count", 0) <= 1)

    return {
        "total_levels": total_levels,
        "total_topics": total_topics,
        "total_exercises": total_exercises,
        "topics_complete": topics_complete,
        "topics_partial": topics_partial,
        "topics_with_pagination": topics_with_pagination,
        "topics_single_page_fallback": topics_single_page_fallback,
        "network_errors": network_errors,
    }


def generate_summary_markdown(catalog: Dict[str, Any]) -> str:
    """Generates a human-readable Markdown summary report from catalog data."""
    stats = catalog.get("stats", {})
    levels = catalog.get("levels", [])
    discovered_at = catalog.get("discovered_at", "Unknown")

    lines = [
        "# Source Catalog Summary — Test-English Grammar",
        "",
        f"- **Source Provider**: {catalog.get('source_provider', 'test-english')}",
        f"- **Base URL**: {catalog.get('base_url', 'https://test-english.com')}",
        f"- **Discovered At**: {discovered_at}",
        f"- **Total Levels**: {stats.get('total_levels', 0)}",
        f"- **Total Topics**: {stats.get('total_topics', 0)}",
        f"- **Total Exercises (Discovered)**: {stats.get('total_exercises', 0)}",
        f"- **Topics Complete**: {stats.get('topics_complete', 0)}",
        f"- **Topics Partial**: {stats.get('topics_partial', 0)}",
        f"- **Topics With Pagination (>1 ex)**: {stats.get('topics_with_pagination', 0)}",
        f"- **Topics Single-Page Fallback**: {stats.get('topics_single_page_fallback', 0)}",
        f"- **Network Errors**: {stats.get('network_errors', 0)}",
        "",
        "## Levels Overview",
        "",
        "| Level ID | Level Title | Topics | Exercises | Complete | Partial |",
        "|---|---|:---:|:---:|:---:|:---:|",
    ]

    for lvl in levels:
        topics = lvl.get("topics", [])
        lvl_ex_count = lvl.get("exercise_count", 0)
        lvl_complete = sum(1 for t in topics if t.get("discovery_status") == "complete")
        lvl_partial = sum(1 for t in topics if t.get("discovery_status") == "partial")
        lines.append(
            f"| `{lvl.get('level_id')}` | {lvl.get('title')} | {len(topics)} | {lvl_ex_count} | {lvl_complete} | {lvl_partial} |"
        )

    lines.extend([
        "",
        "---",
        "## Detailed Topics by Level",
        "",
    ])

    for lvl in levels:
        lines.append(f"### {lvl.get('title')} (`{lvl.get('level_id')}`) — {len(lvl.get('topics', []))} topics")
        lines.append("")
        lines.append("| # | Topic Title | Status | Exercises | Topic URL |")
        lines.append("|:---:|---|:---:|:---:|---|")
        for t in lvl.get("topics", []):
            st = t.get("discovery_status", "complete")
            lines.append(f"| {t.get('order')} | {t.get('title')} | `{st}` | {t.get('exercise_count', 0)} | [{t.get('topic_id')}]({t.get('url')}) |")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# DISCOVERY ORCHESTRATOR
# ---------------------------------------------------------------------------

def build_source_catalog(
    levels_to_scan: Optional[List[str]] = None,
    cache_dir: Optional[Path] = None,
    offline: bool = False,
    delay: float = 0.3,
    max_topics_per_level: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Main discovery routine:
    1. Scans requested levels.
    2. Gathers topics for each level.
    3. Discovers exercise pages for each topic.
    4. Computes dynamic statistics.
    """
    fetcher = ContentFetcher(cache_dir=cache_dir, offline=offline, delay=delay)
    network_errors_count = 0

    selected_levels = DEFAULT_LEVELS
    if levels_to_scan:
        filter_ids = {lvl.strip().lower() for lvl in levels_to_scan}
        selected_levels = [lvl for lvl in DEFAULT_LEVELS if lvl["level_id"].lower() in filter_ids]

    levels_output: List[Dict[str, Any]] = []

    for lvl_info in selected_levels:
        lvl_id = lvl_info["level_id"]
        lvl_title = lvl_info["title"]
        lvl_url = lvl_info["url"]

        print(f"[INFO] Scanning level '{lvl_id}': {lvl_title} ({lvl_url}) ...")
        topics = []
        try:
            lvl_html = fetcher.fetch(lvl_url)
            topics = parse_level_topics_html(lvl_html, lvl_id)
        except Exception as err:
            network_errors_count += 1
            print(f"[WARN] Failed to fetch level page {lvl_url}: {err}", file=sys.stderr)

        # Fallback to master contents page if level page yielded no topics
        if not topics:
            try:
                contents_url = f"{DEFAULT_BASE_URL}/grammar-points/contents/"
                contents_html = fetcher.fetch(contents_url)
                topics = parse_level_topics_html(contents_html, lvl_id)
                if topics:
                    print(f"   [INFO] Recovered {len(topics)} topics for '{lvl_id}' from master contents page.")
            except Exception as err:
                network_errors_count += 1
                print(f"[WARN] Master contents fallback failed for '{lvl_id}': {err}", file=sys.stderr)

        if max_topics_per_level is not None and max_topics_per_level > 0:
            topics = topics[:max_topics_per_level]

        print(f"   -> Found {len(topics)} topics. Discovering exercises for each topic...")

        enriched_topics: List[Dict[str, Any]] = []
        for t in topics:
            topic_url = t["url"]
            discovery_status = "complete"
            try:
                topic_html = fetcher.fetch(topic_url)
                exercises = parse_exercise_pagination_html(topic_html, topic_url)
            except Exception as err:
                network_errors_count += 1
                discovery_status = "partial"
                print(f"[WARN] Failed to inspect exercises for {topic_url}: {err}. Falling back to 1 exercise.", file=sys.stderr)
                exercises = [{"order": 1, "page": 1, "url": topic_url}]

            t_obj = {
                "topic_id": t["topic_id"],
                "level": lvl_id.upper(),
                "order": t["order"],
                "title": t["title"],
                "url": topic_url,
                "discovery_status": discovery_status,
                "exercise_count": len(exercises),
                "exercises": exercises,
            }
            enriched_topics.append(t_obj)

        lvl_exercise_count = sum(t["exercise_count"] for t in enriched_topics)
        levels_output.append({
            "level_id": lvl_id,
            "title": lvl_title,
            "url": lvl_url,
            "topic_count": len(enriched_topics),
            "exercise_count": lvl_exercise_count,
            "topics": enriched_topics,
        })

    # Calculate dynamic stats
    stats = compute_catalog_stats(levels_output, network_errors=network_errors_count)

    catalog: Dict[str, Any] = {
        "source_provider": "test-english",
        "base_url": DEFAULT_BASE_URL,
        "discovered_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "stats": stats,
        "levels": levels_output,
    }

    return catalog


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
            sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            pass

    parser = argparse.ArgumentParser(
        description="Source Catalog Discovery Engine for Test-English grammar"
    )
    parser.add_argument(
        "--levels", "-l",
        default=None,
        help="Comma-separated levels to scan (e.g. 'a1,a2' or 'a1'). Default: all levels.",
    )
    parser.add_argument(
        "--output-dir", "-o",
        default="data/catalog",
        help="Directory where source_catalog.json and summary will be saved (default: data/catalog).",
    )
    parser.add_argument(
        "--cache-dir", "-c",
        default="data/cache/html",
        help="Directory to cache downloaded HTML pages (default: data/cache/html).",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Run in offline mode using only previously cached HTML.",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.3,
        help="Delay in seconds between HTTP requests (default: 0.3).",
    )
    parser.add_argument(
        "--max-topics",
        type=int,
        default=None,
        help="Maximum topics per level to scan (useful for quick smoke tests).",
    )

    args = parser.parse_args()

    levels_list = None
    if args.levels:
        levels_list = [lvl.strip() for lvl in args.levels.split(",") if lvl.strip()]

    out_dir = Path(args.output_dir)
    cache_dir = Path(args.cache_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print("[INFO] Starting Source Catalog Discovery...")
    catalog = build_source_catalog(
        levels_to_scan=levels_list,
        cache_dir=cache_dir,
        offline=args.offline,
        delay=args.delay,
        max_topics_per_level=args.max_topics,
    )

    # 1. Save JSON
    json_path = out_dir / "source_catalog.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)
    print(f"[SUCCESS] Saved canonical JSON catalog: {json_path}")

    # 2. Save Markdown Summary
    summary_md = generate_summary_markdown(catalog)
    md_path = out_dir / "source_catalog_summary.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(summary_md)
    print(f"[SUCCESS] Saved catalog summary report: {md_path}")

    stats = catalog.get("stats", {})
    print(
        f"\n[SUMMARY] Discovered {stats.get('total_levels', 0)} levels, "
        f"{stats.get('total_topics', 0)} topics, "
        f"{stats.get('total_exercises', 0)} exercises."
    )


if __name__ == "__main__":
    main()
