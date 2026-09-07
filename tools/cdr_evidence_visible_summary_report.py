from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path

from tools.cdr_evidence_html_report import build_html_report

SUMMARY_SCHEMA = "ecss-cdr-evidence-visible-summary-v1"

_SUMMARY_PANEL = f"""
<section class="panel" id="visible-summary" style="margin-top:16px">
<h2>Visible evidence summary</h2>
<div class="muted">Schema: {SUMMARY_SCHEMA} · recalculated locally from the currently visible rows</div>
<div class="cards" style="margin:14px 0 0">
<div class="card"><div class="muted">Visible items</div><div class="value" id="visible-summary-items">0</div></div>
<div class="card"><div class="muted">CDR records</div><div class="value" id="visible-summary-records">0</div></div>
<div class="card"><div class="muted">Complete rows</div><div class="value" id="visible-summary-complete">0</div></div>
<div class="card"><div class="muted">Incomplete rows</div><div class="value" id="visible-summary-incomplete">0</div></div>
</div>
<ul id="visible-summary-classifications"></ul>
</section>
"""

_SUMMARY_SCRIPT = r"""
<script>
(() => {
  'use strict';
  const rows = Array.from(document.querySelectorAll('#evidence-rows tr'));
  const search = document.getElementById('evidence-search');
  const classification = document.getElementById('evidence-classification');
  const reset = document.getElementById('evidence-reset');
  const itemsNode = document.getElementById('visible-summary-items');
  const recordsNode = document.getElementById('visible-summary-records');
  const completeNode = document.getElementById('visible-summary-complete');
  const incompleteNode = document.getElementById('visible-summary-incomplete');
  const classesNode = document.getElementById('visible-summary-classifications');
  const toCount = (cell) => {
    const value = Number.parseInt(cell?.textContent || '', 10);
    return Number.isFinite(value) && value >= 0 ? value : 0;
  };
  const refresh = () => {
    const visible = rows.filter((row) => !row.hidden);
    let records = 0;
    let complete = 0;
    let incomplete = 0;
    const classes = new Map();
    for (const row of visible) {
      records += toCount(row.cells[2]);
      complete += toCount(row.cells[3]);
      incomplete += toCount(row.cells[4]);
      const name = row.dataset.classification || 'unknown';
      classes.set(name, (classes.get(name) || 0) + 1);
    }
    itemsNode.textContent = String(visible.length);
    recordsNode.textContent = String(records);
    completeNode.textContent = String(complete);
    incompleteNode.textContent = String(incomplete);
    classesNode.replaceChildren();
    if (!classes.size) {
      const li = document.createElement('li');
      li.textContent = 'No visible evidence';
      classesNode.appendChild(li);
      return;
    }
    for (const [name, count] of Array.from(classes.entries()).sort((a, b) => a[0].localeCompare(b[0]))) {
      const li = document.createElement('li');
      const label = document.createElement('span');
      const value = document.createElement('strong');
      label.textContent = name;
      value.textContent = String(count);
      li.append(label, value);
      classesNode.appendChild(li);
    }
  };
  const refreshAfterBaseFilter = () => queueMicrotask(refresh);
  search?.addEventListener('input', refreshAfterBaseFilter);
  classification?.addEventListener('change', refreshAfterBaseFilter);
  reset?.addEventListener('click', refreshAfterBaseFilter);
  refresh();
})();
</script>
"""


def build_visible_summary_report(payload: Mapping[str, object]) -> str:
    """Add a live selected-subset summary to the verified standalone evidence report."""
    rendered = build_html_report(payload)
    if "</main>" not in rendered or "</body>" not in rendered:
        raise ValueError("base HTML report has an unsupported layout")
    rendered = rendered.replace("</main>", _SUMMARY_PANEL + "\n</main>", 1)
    return rendered.replace("</body>", _SUMMARY_SCRIPT + "\n</body>", 1)


def run(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Render the standalone ECSS evidence report with a live visible-subset summary."
    )
    parser.add_argument("bundle", help="Path to sanitized cdr_evidence_bundle JSON")
    parser.add_argument("output", help="Destination HTML path")
    args = parser.parse_args(argv)
    try:
        payload = json.loads(Path(args.bundle).read_text(encoding="utf-8"))
        if type(payload) is not dict:
            raise ValueError("bundle must be a JSON object")
        rendered = build_visible_summary_report(payload)
        Path(args.output).write_text(rendered, encoding="utf-8", newline="\n")
    except (OSError, TypeError, ValueError, json.JSONDecodeError, KeyError) as exc:
        print(f"cdr_evidence_visible_summary_report: {exc}", file=sys.stderr)
        return 2
    print(args.output)
    return 0


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
