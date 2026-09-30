"""
Browser-Assisted Remote CDP Acquisition Engine

Acquires authorized HTML content from Test-English using an active user browser
session via Chrome DevTools Protocol (CDP).

Architectural Boundaries (ADR-003):
- Acquisition tool is decoupled from Parser and Universal Model.
- Does NOT store cookies or session credentials in project files.
- Uses source_catalog.json as an input manifest; NEVER modifies source_catalog.json.
- Validates page content integrity: rejects challenge/error pages.
- Writes acquired HTML to data/cache/html/ and logs audit records to
  data/cache/acquisition_manifest.json.
- Offline discovery (npm run catalog:discover -- --offline) reads the populated cache.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
from pathlib import Path
import re
import sys
import time
from typing import Any, Dict, List, Optional, Tuple
import urllib.error
import urllib.parse
import urllib.request

from bs4 import BeautifulSoup
from websockets.sync.client import connect as ws_connect


# ---------------------------------------------------------------------------
# CONSTANTS & CONTENT SIGNATURES
# ---------------------------------------------------------------------------

DEFAULT_CDP_URL = "http://127.0.0.1:9222"
DEFAULT_CATALOG_PATH = Path("data/catalog/source_catalog.json")
DEFAULT_CACHE_DIR = Path("data/cache/html")
DEFAULT_MANIFEST_PATH = Path("data/cache/acquisition_manifest.json")

CHALLENGE_PATTERNS = [
    re.compile(r"Just a moment\.\.\.", re.IGNORECASE),
    re.compile(r"cf-browser-verification", re.IGNORECASE),
    re.compile(r"cf-turnstile", re.IGNORECASE),
    re.compile(r"challenge-running", re.IGNORECASE),
    re.compile(r"Enable JavaScript and cookies to continue", re.IGNORECASE),
    re.compile(r"Checking your browser before accessing", re.IGNORECASE),
    re.compile(r"<title>\s*Attention Required!\s*\|\s*Cloudflare\s*</title>", re.IGNORECASE),
]

EXPECTED_CONTENT_PATTERNS = [
    re.compile(r"lesson-page-header", re.IGNORECASE),
    re.compile(r"page-header", re.IGNORECASE),
    re.compile(r"watupro", re.IGNORECASE),
    re.compile(r"grammar-points", re.IGNORECASE),
    re.compile(r"entry-content", re.IGNORECASE),
    re.compile(r"page-primary", re.IGNORECASE),
]

MINIMUM_PAGE_LENGTH = 10000


# ---------------------------------------------------------------------------
# CONTENT VALIDATION
# ---------------------------------------------------------------------------

def validate_page_content(html_content: str) -> Tuple[bool, str, str]:
    """
    Validates acquired HTML to ensure it is authentic lesson content
    and not a Cloudflare challenge, block, or truncated error page.

    Returns:
        (is_valid: bool, acquisition_result: str, reason: str)
    """
    if not html_content:
        return False, "invalid_content", "Empty HTML content"

    # 1. Check for challenge signatures
    for pattern in CHALLENGE_PATTERNS:
        if pattern.search(html_content):
            return False, "challenge_detected", "Cloudflare challenge page detected"

    # 2. Check minimum byte length
    if len(html_content) < MINIMUM_PAGE_LENGTH:
        return False, "invalid_content", f"Content too short ({len(html_content)} bytes < {MINIMUM_PAGE_LENGTH})"

    # 3. Check for expected page domain structures
    has_expected_marker = any(p.search(html_content) for p in EXPECTED_CONTENT_PATTERNS)
    if not has_expected_marker:
        return False, "invalid_content", "Expected Test-English structural elements not found"

    return True, "success", ""


def url_to_cache_path(url: str, cache_dir: Path) -> Path:
    """Computes canonical safe cache filename matching ContentFetcher conventions."""
    safe_name = re.sub(r"[^a-zA-Z0-9_\-\.]", "_", url).strip("_")
    if len(safe_name) > 180:
        safe_name = safe_name[:180] + "_" + str(abs(hash(url)))
    return cache_dir / f"{safe_name}.html"


# ---------------------------------------------------------------------------
# MANIFEST MANAGER
# ---------------------------------------------------------------------------

class AcquisitionManifest:
    """Manages the persistent audit record of all acquired pages."""

    def __init__(self, manifest_path: Path):
        self.path = manifest_path
        self.data: Dict[str, Any] = {
            "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "total_cached_pages": 0,
            "pages": {},
        }
        self.load()

    def load(self) -> None:
        if self.path.exists():
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except Exception:
                pass

    def save(self) -> None:
        self.data["updated_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        pages = self.data.get("pages", {})
        successful_pages = sum(1 for p in pages.values() if p.get("acquisition_result") == "success")
        self.data["total_cached_pages"] = successful_pages

        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def record_result(
        self,
        url: str,
        topic_id: str,
        page: int,
        status: int,
        acquisition_result: str,
        content_validation: str,
        error: Optional[str] = None,
        local_cache_path: Optional[str] = None,
        content_length: int = 0,
        sha256: Optional[str] = None,
    ) -> None:
        pages = self.data.setdefault("pages", {})
        pages[url] = {
            "url": url,
            "topic_id": topic_id,
            "page": page,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "status": status,
            "acquisition_result": acquisition_result,
            "content_validation": content_validation,
            "error": error,
            "local_cache_path": local_cache_path,
            "content_length": content_length,
            "sha256": sha256,
        }

    def is_cached_and_valid(self, url: str, cache_dir: Path) -> bool:
        """Checks if a page has a recorded successful acquisition and exists on disk."""
        pages = self.data.get("pages", {})
        record = pages.get(url)
        if not record or record.get("acquisition_result") != "success":
            return False
        cache_path = url_to_cache_path(url, cache_dir)
        return cache_path.exists() and cache_path.stat().st_size > 0


# ---------------------------------------------------------------------------
# REMOTE CDP CLIENT
# ---------------------------------------------------------------------------

class RemoteCdpClient:
    """
    Connects to a running user Chrome or Edge instance via Remote CDP.
    Navigates tabs, waits for document readiness, and extracts HTML.
    """

    def __init__(self, cdp_url: str = DEFAULT_CDP_URL, timeout: float = 20.0):
        self.cdp_url = cdp_url.rstrip("/")
        self.timeout = timeout

    def check_connection(self) -> bool:
        """Verifies that the browser's CDP endpoint is reachable."""
        try:
            req = urllib.request.Request(f"{self.cdp_url}/json/version")
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                return resp.status == 200
        except Exception:
            return False

    def list_targets(self) -> List[Dict[str, Any]]:
        """Lists active browser targets (tabs/pages)."""
        req = urllib.request.Request(f"{self.cdp_url}/json")
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def acquire_page_html(self, url: str, wait_after_load: float = 1.0) -> str:
        """
        Navigates an existing page or creates a new target via CDP,
        waits for completion, and extracts document outerHTML.
        """
        if not self.check_connection():
            raise ConnectionError(
                f"Cannot connect to browser CDP at {self.cdp_url}.\n"
                "Please ensure Chrome or Edge is running with remote debugging enabled.\n"
                "Example command to launch your browser:\n"
                "  chrome.exe --remote-debugging-port=9222 --remote-allow-origins=*\n"
                "  or\n"
                "  msedge.exe --remote-debugging-port=9222 --remote-allow-origins=*"
            )

        # 1. Open a new tab or reuse target
        encoded_url = urllib.parse.quote(url, safe="")
        create_req = urllib.request.Request(f"{self.cdp_url}/json/new?{encoded_url}")
        target_info = None
        try:
            with urllib.request.urlopen(create_req, timeout=self.timeout) as resp:
                target_info = json.loads(resp.read().decode("utf-8"))
        except Exception as err:
            raise RuntimeError(f"Failed to create new CDP target for {url}: {err}") from err

        target_id = target_info.get("id")
        ws_url = target_info.get("webSocketDebuggerUrl")
        if not ws_url:
            raise RuntimeError(f"No webSocketDebuggerUrl returned for target {target_id}")

        html_content = ""
        try:
            # 2. Connect via WebSocket and wait for DOM load
            with ws_connect(ws_url, close_timeout=5) as websocket:
                # Enable Page domain
                websocket.send(json.dumps({"id": 1, "method": "Page.enable"}))
                _ = websocket.recv()

                # Poll readyState until 'complete'
                start_time = time.time()
                while time.time() - start_time < self.timeout:
                    msg_id = int(time.time() * 1000) % 100000
                    websocket.send(json.dumps({
                        "id": msg_id,
                        "method": "Runtime.evaluate",
                        "params": {"expression": "document.readyState"}
                    }))
                    resp = json.loads(websocket.recv())
                    val = resp.get("result", {}).get("result", {}).get("value")
                    if val == "complete":
                        break
                    time.sleep(0.5)

                if wait_after_load > 0:
                    time.sleep(wait_after_load)

                # Extract outerHTML
                websocket.send(json.dumps({
                    "id": 999,
                    "method": "Runtime.evaluate",
                    "params": {"expression": "document.documentElement.outerHTML"}
                }))
                outer_resp = json.loads(websocket.recv())
                html_content = outer_resp.get("result", {}).get("result", {}).get("value", "")

        finally:
            # 3. Clean up / close the tab
            if target_id:
                try:
                    close_req = urllib.request.Request(f"{self.cdp_url}/json/close/{target_id}")
                    with urllib.request.urlopen(close_req, timeout=5.0) as _:
                        pass
                except Exception:
                    pass

        return html_content


# ---------------------------------------------------------------------------
# ACQUISITION ORCHESTRATOR
# ---------------------------------------------------------------------------

def extract_subsequent_pages(html_content: str, base_topic_url: str) -> List[str]:
    """Extracts additional exercise page URLs from .page-links if present."""
    soup = BeautifulSoup(html_content, "html.parser")
    page_links_div = soup.select_one(".page-links")
    if not page_links_div:
        return []

    clean_topic_url = base_topic_url.rstrip("/") + "/"
    found_urls = []

    for a in page_links_div.find_all("a", href=True):
        href = a["href"].strip()
        full_href = urllib.parse.urljoin(clean_topic_url, href)
        m = re.search(r"/(\d+)/?$", full_href)
        if m:
            page_num = int(m.group(1))
            if page_num > 1:
                norm_page_url = f"{clean_topic_url}{page_num}/"
                if norm_page_url not in found_urls:
                    found_urls.append(norm_page_url)

    return found_urls


def collect_topic_pages(
    topic: Dict[str, Any],
    cdp_client: RemoteCdpClient,
    manifest: AcquisitionManifest,
    cache_dir: Path,
    delay: float = 1.0,
    force: bool = False,
) -> Dict[str, Any]:
    """
    Acquires all pages for a given topic:
    1. Acquires Page 1.
    2. Validates content.
    3. Discovers and acquires Pages 2, 3... if multi-page.
    4. Updates manifest and cache.
    Does NOT modify the topic or source_catalog.json.
    """
    topic_id = topic["topic_id"]
    topic_url = topic["url"]
    print(f"[ACQUISITION] Topic: {topic_id} ({topic_url})")

    acquired_count = 0
    failed_count = 0

    # Page 1
    page1_url = topic_url
    if not force and manifest.is_cached_and_valid(page1_url, cache_dir):
        print(f"   [SKIP] Page 1 already cached and valid: {page1_url}")
        cache_path = url_to_cache_path(page1_url, cache_dir)
        html_page1 = cache_path.read_text(encoding="utf-8", errors="replace")
    else:
        try:
            print(f"   [FETCH] Acquiring Page 1 via CDP: {page1_url}")
            html_page1 = cdp_client.acquire_page_html(page1_url)
            is_valid, acq_result, reason = validate_page_content(html_page1)

            if is_valid:
                cache_path = url_to_cache_path(page1_url, cache_dir)
                cache_path.write_text(html_page1, encoding="utf-8", errors="replace")
                content_hash = hashlib.sha256(html_page1.encode("utf-8")).hexdigest()

                manifest.record_result(
                    url=page1_url,
                    topic_id=topic_id,
                    page=1,
                    status=200,
                    acquisition_result="success",
                    content_validation="passed",
                    error=None,
                    local_cache_path=str(cache_path),
                    content_length=len(html_page1),
                    sha256=content_hash,
                )
                acquired_count += 1
                print(f"   [SUCCESS] Saved Page 1: {cache_path} ({len(html_page1)} bytes)")
            else:
                manifest.record_result(
                    url=page1_url,
                    topic_id=topic_id,
                    page=1,
                    status=403 if acq_result == "challenge_detected" else 422,
                    acquisition_result=acq_result,
                    content_validation="failed",
                    error=reason,
                    local_cache_path=None,
                    content_length=len(html_page1),
                    sha256=None,
                )
                failed_count += 1
                print(f"   [ERROR] Content validation failed for Page 1: {acq_result} - {reason}", file=sys.stderr)
                manifest.save()
                return {"topic_id": topic_id, "acquired": acquired_count, "failed": failed_count}

        except Exception as err:
            manifest.record_result(
                url=page1_url,
                topic_id=topic_id,
                page=1,
                status=500,
                acquisition_result="error",
                content_validation="failed",
                error=str(err),
                local_cache_path=None,
            )
            failed_count += 1
            print(f"   [ERROR] CDP acquisition failed: {err}", file=sys.stderr)
            manifest.save()
            return {"topic_id": topic_id, "acquired": acquired_count, "failed": failed_count}

    # Discover additional exercise pages
    subsequent_urls = extract_subsequent_pages(html_page1, topic_url)
    if subsequent_urls:
        print(f"   [PAGINATION] Discovered {len(subsequent_urls)} additional pages for {topic_id}")

    for idx, sub_url in enumerate(subsequent_urls, start=2):
        if not force and manifest.is_cached_and_valid(sub_url, cache_dir):
            print(f"   [SKIP] Page {idx} already cached and valid: {sub_url}")
            continue

        time.sleep(delay)
        try:
            print(f"   [FETCH] Acquiring Page {idx} via CDP: {sub_url}")
            sub_html = cdp_client.acquire_page_html(sub_url)
            is_valid, acq_result, reason = validate_page_content(sub_html)

            if is_valid:
                cache_path = url_to_cache_path(sub_url, cache_dir)
                cache_path.write_text(sub_html, encoding="utf-8", errors="replace")
                content_hash = hashlib.sha256(sub_html.encode("utf-8")).hexdigest()

                manifest.record_result(
                    url=sub_url,
                    topic_id=topic_id,
                    page=idx,
                    status=200,
                    acquisition_result="success",
                    content_validation="passed",
                    error=None,
                    local_cache_path=str(cache_path),
                    content_length=len(sub_html),
                    sha256=content_hash,
                )
                acquired_count += 1
                print(f"   [SUCCESS] Saved Page {idx}: {cache_path} ({len(sub_html)} bytes)")
            else:
                manifest.record_result(
                    url=sub_url,
                    topic_id=topic_id,
                    page=idx,
                    status=403 if acq_result == "challenge_detected" else 422,
                    acquisition_result=acq_result,
                    content_validation="failed",
                    error=reason,
                    local_cache_path=None,
                    content_length=len(sub_html),
                    sha256=None,
                )
                failed_count += 1
                print(f"   [ERROR] Content validation failed for Page {idx}: {acq_result} - {reason}", file=sys.stderr)

        except Exception as err:
            manifest.record_result(
                url=sub_url,
                topic_id=topic_id,
                page=idx,
                status=500,
                acquisition_result="error",
                content_validation="failed",
                error=str(err),
                local_cache_path=None,
            )
            failed_count += 1
            print(f"   [ERROR] Failed to acquire Page {idx}: {err}", file=sys.stderr)

    manifest.save()
    return {"topic_id": topic_id, "acquired": acquired_count, "failed": failed_count}


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
        description="Browser-Assisted Remote CDP Acquisition Engine for Test-English"
    )
    parser.add_argument(
        "--catalog",
        default=str(DEFAULT_CATALOG_PATH),
        help=f"Path to source catalog manifest (default: {DEFAULT_CATALOG_PATH})",
    )
    parser.add_argument(
        "--cache-dir",
        default=str(DEFAULT_CACHE_DIR),
        help=f"Path to local HTML cache directory (default: {DEFAULT_CACHE_DIR})",
    )
    parser.add_argument(
        "--manifest",
        default=str(DEFAULT_MANIFEST_PATH),
        help=f"Path to acquisition manifest audit file (default: {DEFAULT_MANIFEST_PATH})",
    )
    parser.add_argument(
        "--cdp-url",
        default=DEFAULT_CDP_URL,
        help=f"Remote CDP URL (default: {DEFAULT_CDP_URL})",
    )
    parser.add_argument(
        "--topic-id",
        default=None,
        help="Acquire specific topic by ID (e.g. 'questions')",
    )
    parser.add_argument(
        "--level",
        default=None,
        help="Filter topics by level (e.g. 'a1')",
    )
    parser.add_argument(
        "--only-partial",
        action="store_true",
        default=True,
        help="Only acquire topics marked discovery_status='partial' (default: True)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum topics to acquire in this run",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.5,
        help="Polite delay in seconds between page requests (default: 1.5)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-acquisition even if already in cache and manifest",
    )

    args = parser.parse_args()

    catalog_path = Path(args.catalog)
    cache_dir = Path(args.cache_dir)
    manifest_path = Path(args.manifest)

    cache_dir.mkdir(parents=True, exist_ok=True)

    if not catalog_path.exists():
        print(f"[ERROR] Source catalog manifest not found: {catalog_path}", file=sys.stderr)
        sys.exit(1)

    with open(catalog_path, "r", encoding="utf-8") as f:
        catalog_data = json.load(f)

    manifest = AcquisitionManifest(manifest_path)
    cdp_client = RemoteCdpClient(cdp_url=args.cdp_url)

    # Check connection early
    if not cdp_client.check_connection():
        print(
            f"\n[ERROR] Cannot connect to browser CDP endpoint at {args.cdp_url}.\n"
            "Please start Chrome or Microsoft Edge with remote debugging enabled.\n"
            "Command examples:\n"
            "  chrome.exe --remote-debugging-port=9222 --remote-allow-origins=*\n"
            "  or\n"
            "  msedge.exe --remote-debugging-port=9222 --remote-allow-origins=*\n",
            file=sys.stderr,
        )
        sys.exit(2)

    # Collect candidate topics
    candidates: List[Dict[str, Any]] = []
    for lvl in catalog_data.get("levels", []):
        lvl_id = lvl.get("level_id", "").lower()
        if args.level and lvl_id != args.level.lower():
            continue

        for topic in lvl.get("topics", []):
            if args.topic_id and topic.get("topic_id") != args.topic_id:
                continue
            if args.only_partial and topic.get("discovery_status") == "complete":
                continue
            candidates.append(topic)

    if args.limit and args.limit > 0:
        candidates = candidates[:args.limit]

    print(f"[INFO] Selected {len(candidates)} candidate topics for acquisition.")
    total_acquired = 0
    total_failed = 0

    for idx, topic in enumerate(candidates, start=1):
        print(f"\n--- [{idx}/{len(candidates)}] ---")
        res = collect_topic_pages(
            topic=topic,
            cdp_client=cdp_client,
            manifest=manifest,
            cache_dir=cache_dir,
            delay=args.delay,
            force=args.force,
        )
        total_acquired += res.get("acquired", 0)
        total_failed += res.get("failed", 0)

    print(f"\n[SUMMARY] Acquisition finished: {total_acquired} pages acquired, {total_failed} failures.")
    print(f"[INFO] Audit log saved: {manifest_path}")


if __name__ == "__main__":
    main()
