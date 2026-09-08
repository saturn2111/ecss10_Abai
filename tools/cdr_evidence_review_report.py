from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path

from tools.cdr_evidence_visible_summary_report import build_visible_summary_report

REVIEW_SCHEMA = "ecss-cdr-evidence-review-v1"

_REVIEW_PANEL = f"""
<section class="panel" id="evidence-review" style="margin-top:16px">
<h2>Operator review</h2>
<div class="muted">Schema: {REVIEW_SCHEMA} · bookmarks are session-only and never sent to ECSS</div>
<div class="filters" style="grid-template-columns:auto auto 1fr">
<button id="review-bookmarked-only" type="button" aria-pressed="false">Bookmarked only</button>
<button id="review-clear" type="button">Clear bookmarks</button>
<div id="review-count" class="muted" style="align-self:center">Bookmarked 0 of 0 evidence items</div>
</div>
</section>
"""

_REVIEW_SCRIPT = r"""
<script>
(() => {
  'use strict';
  const rows = Array.from(document.querySelectorAll('#evidence-rows tr'));
  const table = document.querySelector('#evidence-rows')?.closest('table');
  const tableHead = table?.querySelector('thead tr');
  const onlyButton = document.getElementById('review-bookmarked-only');
  const clearButton = document.getElementById('review-clear');
  const countNode = document.getElementById('review-count');
  const search = document.getElementById('evidence-search');
  const classification = document.getElementById('evidence-classification');
  const reset = document.getElementById('evidence-reset');
  const resultCount = document.getElementById('evidence-result-count');
  const exportButton = document.getElementById('evidence-export');
  const printButton = document.getElementById('evidence-print');
  const summaryItems = document.getElementById('visible-summary-items');
  const summaryRecords = document.getElementById('visible-summary-records');
  const summaryComplete = document.getElementById('visible-summary-complete');
  const summaryIncomplete = document.getElementById('visible-summary-incomplete');
  const summaryClasses = document.getElementById('visible-summary-classifications');
  let bookmarkedOnly = false;

  if (tableHead) {
    const th = document.createElement('th');
    th.textContent = 'Review';
    tableHead.appendChild(th);
  }

  for (const [index, row] of rows.entries()) {
    row.dataset.bookmarked = '0';
    const cell = document.createElement('td');
    const label = document.createElement('label');
    label.style.whiteSpace = 'nowrap';
    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.setAttribute('aria-label', `Bookmark evidence row ${index + 1}`);
    label.append(checkbox, document.createTextNode(' ★'));
    cell.appendChild(label);
    row.appendChild(cell);
    checkbox.addEventListener('change', () => {
      row.dataset.bookmarked = checkbox.checked ? '1' : '0';
      refreshReview();
    });
  }

  const baseVisible = (row) => {
    const needle = search?.value.trim().toLowerCase() || '';
    const selected = classification?.value || '';
    const matchesText = !needle || (row.dataset.search || '').includes(needle);
    const matchesClass = !selected || row.dataset.classification === selected;
    return matchesText && matchesClass;
  };

  const toCount = (cell) => {
    const value = Number.parseInt(cell?.textContent || '', 10);
    return Number.isFinite(value) && value >= 0 ? value : 0;
  };

  const refreshVisibleSummary = (visible) => {
    if (!summaryItems || !summaryRecords || !summaryComplete || !summaryIncomplete || !summaryClasses) return;
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
    summaryItems.textContent = String(visible.length);
    summaryRecords.textContent = String(records);
    summaryComplete.textContent = String(complete);
    summaryIncomplete.textContent = String(incomplete);
    summaryClasses.replaceChildren();
    if (!classes.size) {
      const li = document.createElement('li');
      li.textContent = 'No visible evidence';
      summaryClasses.appendChild(li);
      return;
    }
    for (const [name, count] of Array.from(classes.entries()).sort((a, b) => a[0].localeCompare(b[0]))) {
      const li = document.createElement('li');
      const label = document.createElement('span');
      const value = document.createElement('strong');
      label.textContent = name;
      value.textContent = String(count);
      li.append(label, value);
      summaryClasses.appendChild(li);
    }
  };

  const refreshReview = () => {
    let bookmarked = 0;
    const visible = [];
    for (const row of rows) {
      const isBookmarked = row.dataset.bookmarked === '1';
      if (isBookmarked) bookmarked += 1;
      row.hidden = !baseVisible(row) || (bookmarkedOnly && !isBookmarked);
      if (!row.hidden) visible.push(row);
    }
    countNode.textContent = `Bookmarked ${bookmarked} of ${rows.length} evidence items`;
    onlyButton.setAttribute('aria-pressed', String(bookmarkedOnly));
    if (resultCount) resultCount.textContent = `Showing ${visible.length} of ${rows.length} evidence items`;
    if (exportButton) exportButton.disabled = visible.length === 0;
    if (printButton) printButton.disabled = visible.length === 0;
    refreshVisibleSummary(visible);
  };

  onlyButton.addEventListener('click', () => {
    bookmarkedOnly = !bookmarkedOnly;
    refreshReview();
  });
  clearButton.addEventListener('click', () => {
    for (const row of rows) {
      row.dataset.bookmarked = '0';
      const checkbox = row.querySelector('input[type="checkbox"]');
      if (checkbox) checkbox.checked = false;
    }
    refreshReview();
  });
  search?.addEventListener('input', () => queueMicrotask(refreshReview));
  classification?.addEventListener('change', () => queueMicrotask(refreshReview));
  reset?.addEventListener('click', () => queueMicrotask(refreshReview));
  refreshReview();
})();
</script>
"""


def build_review_report(payload: Mapping[str, object]) -> str:
    """Add session-only operator bookmarks to the verified standalone summary report."""
    rendered = build_visible_summary_report(payload)
    if "</main>" not in rendered or "</body>" not in rendered:
        raise ValueError("base visible-summary report has an unsupported layout")
    rendered = rendered.replace("</main>", _REVIEW_PANEL + "\n</main>", 1)
    return rendered.replace("</body>", _REVIEW_SCRIPT + "\n</body>", 1)


def run(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Render the standalone ECSS evidence report with session-only operator bookmarks."
    )
    parser.add_argument("bundle", help="Path to sanitized cdr_evidence_bundle JSON")
    parser.add_argument("output", help="Destination HTML path")
    args = parser.parse_args(argv)
    try:
        payload = json.loads(Path(args.bundle).read_text(encoding="utf-8"))
        if type(payload) is not dict:
            raise ValueError("bundle must be a JSON object")
        rendered = build_review_report(payload)
        Path(args.output).write_text(rendered, encoding="utf-8", newline="\n")
    except (OSError, TypeError, ValueError, json.JSONDecodeError, KeyError) as exc:
        print(f"cdr_evidence_review_report: {exc}", file=sys.stderr)
        return 2
    print(args.output)
    return 0


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
