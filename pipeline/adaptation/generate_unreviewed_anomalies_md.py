"""Generate Markdown representation for the 69 unreviewed anomalies."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
JSON_PATH = REPO_ROOT / "data" / "reports" / "teacher_review_batches" / "review_batch_unreviewed_anomalies_0069.json"
MD_PATH = REPO_ROOT / "data" / "reports" / "teacher_review_batches" / "review_batch_unreviewed_anomalies_0069.md"

with open(JSON_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

md_lines = [
    "# Teacher Review Packet — Full Corpus Deep Scan Anomalies (69 Questions)",
    "",
    f"**Generated**: {data['metadata']['scan_timestamp']}  ",
    "**Status**: `PREPARED (PENDING HQ TEACHER REVIEW)`  ",
    f"**Total Unreviewed Anomalies Found**: {len(data['questions'])}  ",
    "",
    "---",
    "",
    "## Summary Table",
    "",
    "| # | QID | Level | Response Model | Exercise | Topic | Anomaly Triggers | Correct Answer |",
    "| :---: | :---: | :---: | :---: | :---: | :--- | :--- | :--- |",
]

for idx, q in enumerate(data["questions"], 1):
    ans_str = ", ".join([str(x) for x in q["adapted_correct_answer"]]) if len(q["adapted_correct_answer"]) <= 2 else f"{q['adapted_correct_answer'][0]}... ({len(q['adapted_correct_answer'])})"
    reasons = " <br> ".join(q["anomaly_reasons"])
    md_lines.append(
        f"| {idx} | **{q['qid']}** | `{q['level']}` | `{q['response_model']}` | `{q['exercise_id']}` | {q['grammar_target']} | {reasons} | `{ans_str}` |"
    )

md_lines.extend([
    "",
    "---",
    "",
    "## Questions for HQ Review",
    "",
])

for idx, q in enumerate(data["questions"], 1):
    md_lines.append(f"### Item #{idx} — QID {q['qid']} ({q['level']})")
    md_lines.append(f"- **Exercise**: `{q['exercise_id']}` ({q['exercise_title']}) | **Topic**: `{q['grammar_target']}`")
    md_lines.append(f"- **Response Model**: `{q['response_model']}` | **Correct Answer**: `{q['adapted_correct_answer']}`")
    if q["adapted_options"]:
        opts_summary = [f"{o['text']} ({'✓' if o['is_correct'] else '✗'})" for o in q["adapted_options"]]
        md_lines.append(f"- **Options**: {', '.join(opts_summary)}")
    md_lines.append(f"- **Adapted Text**:\n  > {q['adapted_text'].replace(chr(10), ' ')}")
    md_lines.append(f"- **Source Text**:\n  > {q['source_text'].replace(chr(10), ' ')}")
    md_lines.append(f"- **Anomaly Triggers**:\n  - " + "\n  - ".join(q["anomaly_reasons"]))
    md_lines.append("")
    md_lines.append("---")
    md_lines.append("")

with open(MD_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(md_lines).strip() + "\n")

print(f"Saved {MD_PATH}")
