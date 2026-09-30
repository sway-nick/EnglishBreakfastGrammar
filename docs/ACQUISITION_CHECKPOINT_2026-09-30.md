# Acquisition Checkpoint — 2026-09-30

## Executive Summary

The authorized content acquisition phase for the complete Test-English catalog has been completed successfully via the Browser-Assisted Remote CDP Acquisition Engine (`pipeline/acquisition/browser_collector.py`).

The entire HTML corpus is now cached locally in `data/cache/html` and fully audited in `data/cache/acquisition_manifest.json`.

---

## Key Metrics

- **Catalog Scope:** 225 topics across 7 levels (`A1`, `A2`, `B1`, `B1-B2`, `B2`, `C1`, `Shorts`).
- **Acquired Topics:** 225 / 225 (100% complete).
- **Remaining Partial Topics:** 0.
- **Acquisition Failures:** 0.
- **Cloudflare Challenges Encountered (`challenge_detected`):** 0.
- **Acquisition Manifest Status:** 646 / 646 successful entries (`status=200`, `content_validation="passed"`, sha256 recorded).
- **Total HTML Cache Files on Disk:** 646 files (~206.9 MB).
- **Exercise HTML Pages in Cache:** 638 unique files.
- **Category / Index HTML Pages in Cache:** 8 files.
- **Logical Exercise Pages across Levels:** 675 pages.
  > *Note on logical vs. unique pages:* 6 topics in the Test-English catalog are cross-referenced across two levels simultaneously (e.g. `present-simple-present-continuous` in both A1 and B1). The browser collector's built-in idempotency detected already cached entries and safely avoided duplicate fetches, resulting in 638 unique exercise files stored on disk representing 675 logical level-topic assignments.

---

## Breakdown by Level

| Level | Level Name | Catalog Topics | Logical Exercise Pages | Page Distribution per Topic | Status |
| :--- | :--- | :---: | :---: | :--- | :---: |
| **A1** | A1 Elementary | 36 | 114 | 32 topics × 3 pp., 3 topics × 4 pp., 1 topic × 6 pp. | **100% Complete** |
| **A2** | A2 Pre-intermediate | 41 | 141 | 33 topics × 3 pp., 3 topics × 4 pp., 3 topics × 6 pp., 1 × 5 pp., 1 × 7 pp. | **100% Complete** |
| **B1** | B1 Intermediate | 41 | 140 | 33 topics × 3 pp., 4 topics × 4 pp., 3 topics × 6 pp., 1 × 7 pp. | **100% Complete** |
| **B1-B2** | B1+ Upper-intermediate | 36 | 116 | 30 topics × 3 pp., 3 topics × 4 pp., 2 topics × 6 pp., 1 × 2 pp. | **100% Complete** |
| **B2** | B2 Pre-advanced | 33 | 106 | 26 topics × 3 pp., 5 topics × 4 pp., 1 topic × 6 pp., 1 × 2 pp. | **100% Complete** |
| **C1** | C1 Advanced | 10 | 30 | 10 topics × 3 pp. | **100% Complete** |
| **Shorts** | Grammar Shorts | 28 | 28 | 28 topics × 1 p. | **100% Complete** |
| **Total** | **All 7 Levels** | **225** | **675** (638 unique on disk) | — | **100% Complete** |

---

## Checkpoint & Safety Guarantees

1. **Existing Checkpoint Preserved:**
   - `C:\Users\user\Desktop\english_cms_gemini_all_182.xlsx` is preserved and untouched.
   - `C:\Users\user\Desktop\english_cms.xlsx` is preserved and untouched.
   - `C:\Users\user\Desktop\quiz-258_gemini_results.xlsx` is preserved and untouched.
2. **Zero Gemini/API Invocations:**
   - No Gemini API calls were made during the mass acquisition phase; no AI quotas were spent.
3. **Resumability & Cache Integrity:**
   - Acquisition is 100% complete and fully resumable/verifiable offline from `data/cache/html/` and `data/cache/acquisition_manifest.json`.
4. **Git Hygiene:**
   - All `data/` cache files, raw HTML, and Excel files remain strictly git-ignored (`.gitignore`).

---

## Next Recommended Phase

**Phase: Offline Parsing & CMS Ingestion**
- Step 1: Run offline catalog discovery (`npm run catalog:discover -- --offline`) to sync `source_catalog.json` with the populated local HTML cache.
- Step 2: Batch execute the offline parser (`pipeline/parser/test_english_parser.py`) across the 638 cached exercise pages.
- Step 3: Run Universal Collector and generate CMS workbook.
- Step 4: Answer enrichment (Google Sheets Gemini).
- Step 5: Content adaptation / rewrite.
- Step 6: Final validation and database import.
