from __future__ import annotations

import argparse
import html
import json
import sys
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path

from tools.cdr_evidence_bundle import BUNDLE_SCHEMA, BUNDLE_WARNING

HTML_SCHEMA = "ecss-cdr-evidence-html-report-v3"


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
        label_raw = str(item["label"])
        label = html.escape(label_raw)
        report = item["report"]
        assert isinstance(report, dict)
        caller_ref_raw = str(report["caller_ref"])
        evidence_raw = str(report["evidence"])
        searchable = html.escape(f"{label_raw} {caller_ref_raw} {evidence_raw}".lower(), quote=True)
        classification = html.escape(evidence_raw, quote=True)
        rows.append(
            f"<tr data-search='{searchable}' data-classification='{classification}'>"
            f"<td><strong>{label}</strong></td>"
            f"<td><code>{html.escape(caller_ref_raw)}</code></td>"
            f"<td>{report['records']}</td>"
            f"<td>{report['complete']}</td>"
            f"<td>{report['incomplete']}</td>"
            f"<td><span class='badge'>{html.escape(evidence_raw)}</span></td>"
            f"<td>{_timing(report.get('raw_t_ecd_seconds'))}</td>"
            f"<td>{_timing(report.get('raw_t_dba_seconds'))}</td>"
            "</tr>"
        )

    classification_html = "".join(
        f"<li><span>{html.escape(name)}</span><strong>{count}</strong></li>"
        for name, count in sorted(classification_counts.items())
    ) or "<li><span>No evidence items</span><strong>0</strong></li>"
    classification_options = "".join(
        f"<option value='{html.escape(name, quote=True)}'>{html.escape(name)} ({count})</option>"
        for name, count in sorted(classification_counts.items())
    )

    warning = html.escape(BUNDLE_WARNING)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ECSS CDR Evidence Report</title>
<style>
:root{{color-scheme:light dark;font-family:Segoe UI,Arial,sans-serif}}body{{margin:0;background:#f3f5f8;color:#18202b}}main{{max-width:1200px;margin:auto;padding:28px}}h1{{margin:0 0 6px}}.muted{{color:#687386}}.cards{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin:24px 0}}.card,.panel{{background:#fff;border:1px solid #dfe5ec;border-radius:14px;padding:18px}}.value{{font-size:28px;font-weight:700}}table{{width:100%;border-collapse:collapse;background:#fff}}th,td{{padding:12px;border-bottom:1px solid #e5e9ef;text-align:left;vertical-align:top}}th{{font-size:12px;text-transform:uppercase;color:#687386}}.panel{{overflow-x:auto}}.badge{{display:inline-block;padding:4px 8px;background:#edf2f7;border-radius:999px;font-size:12px}}.warning{{border-left:4px solid #a56a10;background:#fff7e6;padding:14px 16px;margin:18px 0;border-radius:8px}}ul{{list-style:none;padding:0;margin:0}}li{{display:flex;justify-content:space-between;gap:20px;padding:7px 0}}code{{font-family:Consolas,monospace}}.filters{{display:grid;grid-template-columns:minmax(220px,2fr) minmax(180px,1fr) auto auto;gap:10px;margin:12px 0 16px}}.filters input,.filters select,.filters button{{font:inherit;padding:10px 12px;border:1px solid #ccd5e0;border-radius:9px;background:#fff;color:inherit}}.filters button{{cursor:pointer}}.result-count{{font-size:13px;margin-bottom:10px}}tr[hidden]{{display:none}}@media(max-width:900px){{.filters{{grid-template-columns:1fr 1fr}}}}@media(max-width:760px){{.cards{{grid-template-columns:repeat(2,1fr)}}.filters{{grid-template-columns:1fr}}main{{padding:16px}}}}@media(prefers-color-scheme:dark){{body{{background:#11161d;color:#edf2f7}}.card,.panel,table{{background:#1b222c;border-color:#303a47}}th,td{{border-color:#303a47}}.muted,th{{color:#aeb8c6}}.badge{{background:#2a3441}}.warning{{background:#342a17}}.filters input,.filters select,.filters button{{background:#151b23;border-color:#3a4655}}}}
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
<section class="panel" style="margin-top:16px"><h2>Caller-reference evidence</h2>
<div class="filters"><input id="evidence-search" type="search" placeholder="Search label, caller ref or classification" aria-label="Search evidence"><select id="evidence-classification" aria-label="Filter by classification"><option value="">All classifications</option>{classification_options}</select><button id="evidence-reset" type="button">Reset</button><button id="evidence-export" type="button">Export visible CSV</button></div>
<div id="evidence-result-count" class="muted result-count">Showing {len(items)} of {len(items)} evidence items</div>
<table><thead><tr><th>Label</th><th>Caller ref</th><th>Records</th><th>Complete</th><th>Incomplete</th><th>Evidence</th><th>Raw T_ECD (s)</th><th>Raw T_DBA (s)</th></tr></thead><tbody id="evidence-rows">{''.join(rows)}</tbody></table></section>
</main>
<script>
(() => {{
  'use strict';
  const search = document.getElementById('evidence-search');
  const classification = document.getElementById('evidence-classification');
  const reset = document.getElementById('evidence-reset');
  const exportButton = document.getElementById('evidence-export');
  const counter = document.getElementById('evidence-result-count');
  const rows = Array.from(document.querySelectorAll('#evidence-rows tr'));
  const apply = () => {{
    const needle = search.value.trim().toLowerCase();
    const selected = classification.value;
    let visible = 0;
    for (const row of rows) {{
      const matchesText = !needle || row.dataset.search.includes(needle);
      const matchesClass = !selected || row.dataset.classification === selected;
      row.hidden = !(matchesText && matchesClass);
      if (!row.hidden) visible += 1;
    }}
    counter.textContent = `Showing ${{visible}} of ${{rows.length}} evidence items`;
    exportButton.disabled = visible === 0;
  }};
  const csvCell = (value) => {{
    let safe = String(value).replace(/\r?\n/g, ' ').trim();
    if (/^[=+\-@]/.test(safe)) safe = "'" + safe;
    return '"' + safe.replace(/"/g, '""') + '"';
  }};
  const exportVisible = () => {{
    const visibleRows = rows.filter((row) => !row.hidden);
    if (!visibleRows.length) return;
    const header = Array.from(document.querySelectorAll('thead th')).map((cell) => csvCell(cell.textContent));
    const body = visibleRows.map((row) => Array.from(row.cells).map((cell) => csvCell(cell.textContent)));
    const csv = '\uFEFF' + [header, ...body].map((line) => line.join(',')).join('\r\n');
    const blob = new Blob([csv], {{ type: 'text/csv;charset=utf-8' }});
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'ecss-cdr-visible-evidence.csv';
    document.body.appendChild(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 0);
  }};
  search.addEventListener('input', apply);
  classification.addEventListener('change', apply);
  reset.addEventListener('click', () => {{ search.value = ''; classification.value = ''; apply(); search.focus(); }});
  exportButton.addEventListener('click', exportVisible);
  apply();
}})();
</script>
</body></html>"""


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
