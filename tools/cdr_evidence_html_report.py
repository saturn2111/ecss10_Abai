from __future__ import annotations

import argparse
import html
import json
import sys
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path

from tools.cdr_evidence_bundle import BUNDLE_SCHEMA, BUNDLE_WARNING

HTML_SCHEMA = "ecss-cdr-evidence-html-report-v1"


def _require_int(value: object, field: str) -> int:
    if type(value) is not int or value < 0:
        raise ValueError(f"{field} must be a non-negative exact integer")
    return value


def _validate_bundle(payload: object) -> list[dict[str, object]]:
    if type(payload) is not dict:
        raise ValueError("bundle must be a JSON object")
    if payload.get("schema") != BUNDLE_SCHEMA:
        raise ValueError("unsupported evidence bundle schema")
    if payload.get("warning") != BUNDLE_WARNING:
        raise ValueError("unexpected evidence bundle semantic warning")
    items = payload.get("items")
    if type(items) is not list:
        raise ValueError("bundle items must be a list")

    validated: list[dict[str, object]] = []
    seen: set[str] = set()
    for index, item in enumerate(items):
        if type(item) is not dict:
            raise ValueError(f"items[{index}] must be an object")
        label = item.get("label")
        report = item.get("report")
        if type(label) is not str or not label or label.strip() != label:
            raise ValueError(f"items[{index}].label must be an exact non-empty string")
        if label in seen:
            raise ValueError(f"duplicate bundle label: {label}")
        if type(report) is not dict:
            raise ValueError(f"items[{index}].report must be an object")
        if report.get("warning") != BUNDLE_WARNING.replace("evidence-only bundle; ", "raw timing fields only; "):
            raise ValueError(f"items[{index}] has unexpected report semantic warning")

        caller_ref = report.get("caller_ref")
        evidence = report.get("evidence")
        if type(caller_ref) is not str or not caller_ref:
            raise ValueError(f"items[{index}].report.caller_ref must be a non-empty string")
        if type(evidence) is not str or not evidence:
            raise ValueError(f"items[{index}].report.evidence must be a non-empty string")
        records = _require_int(report.get("records"), f"items[{index}].report.records")
        complete = _require_int(report.get("complete"), f"items[{index}].report.complete")
        incomplete = _require_int(report.get("incomplete"), f"items[{index}].report.incomplete")
        if complete + incomplete != records:
            raise ValueError(f"items[{index}] timing cardinality is inconsistent")

        for timing_name in ("raw_t_ecd_seconds", "raw_t_dba_seconds"):
            timing = report.get(timing_name)
            if timing is not None and type(timing) not in (int, float):
                raise ValueError(f"items[{index}].report.{timing_name} must be numeric or null")

        seen.add(label)
        validated.append(item)
    return validated


def _timing(value: object) -> str:
    return "n/a" if value is None else html.escape(str(value))


def build_html_report(payload: Mapping[str, object]) -> str:
    items = _validate_bundle(payload)
    classification_counts = Counter(str(item["report"]["evidence"]) for item in items)  # type: ignore[index]
    total_records = sum(int(item["report"]["records"]) for item in items)  # type: ignore[index]
    total_complete = sum(int(item["report"]["complete"]) for item in items)  # type: ignore[index]
    total_incomplete = sum(int(item["report"]["incomplete"]) for item in items)  # type: ignore[index]

    rows: list[str] = []
    for item in items:
        label = html.escape(str(item["label"]))
        report = item["report"]
        assert isinstance(report, dict)
        rows.append(
            "<tr>"
            f"<td><strong>{label}</strong></td>"
            f"<td><code>{html.escape(str(report['caller_ref']))}</code></td>"
            f"<td>{report['records']}</td>"
            f"<td>{report['complete']}</td>"
            f"<td>{report['incomplete']}</td>"
            f"<td><span class='badge'>{html.escape(str(report['evidence']))}</span></td>"
            f"<td>{_timing(report.get('raw_t_ecd_seconds'))}</td>"
            f"<td>{_timing(report.get('raw_t_dba_seconds'))}</td>"
            "</tr>"
        )

    classification_html = "".join(
        f"<li><span>{html.escape(name)}</span><strong>{count}</strong></li>"
        for name, count in sorted(classification_counts.items())
    ) or "<li><span>No evidence items</span><strong>0</strong></li>"

    warning = html.escape(BUNDLE_WARNING)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ECSS CDR Evidence Report</title>
<style>
:root{{color-scheme:light dark;font-family:Segoe UI,Arial,sans-serif}}body{{margin:0;background:#f3f5f8;color:#18202b}}main{{max-width:1200px;margin:auto;padding:28px}}h1{{margin:0 0 6px}}.muted{{color:#687386}}.cards{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin:24px 0}}.card,.panel{{background:#fff;border:1px solid #dfe5ec;border-radius:14px;padding:18px}}.value{{font-size:28px;font-weight:700}}table{{width:100%;border-collapse:collapse;background:#fff}}th,td{{padding:12px;border-bottom:1px solid #e5e9ef;text-align:left;vertical-align:top}}th{{font-size:12px;text-transform:uppercase;color:#687386}}.panel{{overflow-x:auto}}.badge{{display:inline-block;padding:4px 8px;background:#edf2f7;border-radius:999px;font-size:12px}}.warning{{border-left:4px solid #a56a10;background:#fff7e6;padding:14px 16px;margin:18px 0;border-radius:8px}}ul{{list-style:none;padding:0;margin:0}}li{{display:flex;justify-content:space-between;gap:20px;padding:7px 0}}code{{font-family:Consolas,monospace}}@media(max-width:760px){{.cards{{grid-template-columns:repeat(2,1fr)}}main{{padding:16px}}}}@media(prefers-color-scheme:dark){{body{{background:#11161d;color:#edf2f7}}.card,.panel,table{{background:#1b222c;border-color:#303a47}}th,td{{border-color:#303a47}}.muted,th{{color:#aeb8c6}}.badge{{background:#2a3441}}.warning{{background:#342a17}}}}
</style>
</head>
<body><main>
<h1>ECSS CDR Evidence Report</h1>
<div class="muted">Schema: {HTML_SCHEMA} · sanitized offline evidence only</div>
<div class="warning"><strong>Semantic boundary:</strong> {warning}. Raw T_ECD/T_DBA values below are displayed only as evidence and are not labelled as queue wait or final call duration.</div>
<section class="cards">
<div class="card"><div class="muted">Evidence items</div><div class="value">{len(items)}</div></div>
<div class="card"><div class="muted">CDR records</div><div class="value">{total_records}</div></div>
<div class="card"><div class="muted">Complete timing rows</div><div class="value">{total_complete}</div></div>
<div class="card"><div class="muted">Incomplete timing rows</div><div class="value">{total_incomplete}</div></div>
</section>
<section class="panel"><h2>Evidence classifications</h2><ul>{classification_html}</ul></section>
<section class="panel" style="margin-top:16px"><h2>Caller-reference evidence</h2><table><thead><tr><th>Label</th><th>Caller ref</th><th>Records</th><th>Complete</th><th>Incomplete</th><th>Evidence</th><th>Raw T_ECD (s)</th><th>Raw T_DBA (s)</th></tr></thead><tbody>{''.join(rows)}</tbody></table></section>
</main></body></html>"""


def run(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render a standalone human-readable HTML report from a sanitized ECSS evidence bundle.")
    parser.add_argument("bundle", help="Path to cdr_evidence_bundle JSON")
    parser.add_argument("output", help="Destination HTML path")
    args = parser.parse_args(argv)
    try:
        payload = json.loads(Path(args.bundle).read_text(encoding="utf-8"))
        rendered = build_html_report(payload)
        Path(args.output).write_text(rendered, encoding="utf-8", newline="\n")
    except (OSError, TypeError, ValueError, json.JSONDecodeError, KeyError) as exc:
        print(f"cdr_evidence_html_report: {exc}", file=sys.stderr)
        return 2
    print(args.output)
    return 0


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
