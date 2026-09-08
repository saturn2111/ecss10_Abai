from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path

from tools.cdr_evidence_review_report import build_review_report

MARKDOWN_FILENAME = "ecss-cdr-visible-evidence.md"

_MARKDOWN_BUTTON = '<button id="review-export-markdown" type="button">Export visible Markdown</button>'

_MARKDOWN_SCRIPT = r"""
<script>
(() => {
  'use strict';
  const button = document.getElementById('review-export-markdown');
  const rows = Array.from(document.querySelectorAll('#evidence-rows tr'));
  const table = document.querySelector('#evidence-rows')?.closest('table');
  const head = table?.querySelector('thead tr');
  const search = document.getElementById('evidence-search');
  const classification = document.getElementById('evidence-classification');
  const bookmarkedOnly = document.getElementById('review-bookmarked-only');

  const markdownCell = (value) => String(value || '')
    .replaceAll('\\', '\\\\')
    .replaceAll('|', '\\|')
    .replace(/\r?\n/g, '<br>')
    .trim();

  const visibleRows = () => rows.filter((row) => !row.hidden);

  const exportVisibleMarkdown = () => {
    const visible = visibleRows();
    if (!visible.length || !head) return;
    const headers = Array.from(head.cells).slice(0, -1).map((cell) => markdownCell(cell.textContent));
    const lines = [
      '# ECSS CDR Evidence Review',
      '',
      '> Raw visible evidence only. T_ECD/T_DBA are not labeled as queue wait or final Duration.',
      '',
      `- Visible evidence items: ${visible.length}`,
      `- Search: ${markdownCell(search?.value || '(none)')}`,
      `- Classification: ${markdownCell(classification?.value || '(all)')}`,
      `- Bookmarked only: ${bookmarkedOnly?.getAttribute('aria-pressed') === 'true' ? 'yes' : 'no'}`,
      '',
      `| ${headers.join(' | ')} | Bookmarked |`,
      `| ${headers.map(() => '---').join(' | ')} | --- |`,
    ];
    for (const row of visible) {
      const values = Array.from(row.cells).slice(0, -1).map((cell) => markdownCell(cell.textContent));
      lines.push(`| ${values.join(' | ')} | ${row.dataset.bookmarked === '1' ? 'yes' : 'no'} |`);
    }
    lines.push('');
    const blob = new Blob([lines.join('\n')], {type: 'text/markdown;charset=utf-8'});
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = 'ecss-cdr-visible-evidence.md';
    document.body.appendChild(anchor);
    try { anchor.click(); } finally { anchor.remove(); URL.revokeObjectURL(url); }
  };

  if (button) {
    const refresh = () => { button.disabled = visibleRows().length === 0; };
    button.addEventListener('click', exportVisibleMarkdown);
    document.getElementById('evidence-search')?.addEventListener('input', () => queueMicrotask(refresh));
    document.getElementById('evidence-classification')?.addEventListener('change', () => queueMicrotask(refresh));
    document.getElementById('evidence-reset')?.addEventListener('click', () => queueMicrotask(refresh));
    document.getElementById('review-bookmarked-only')?.addEventListener('click', () => queueMicrotask(refresh));
    document.getElementById('review-bookmark-visible')?.addEventListener('click', () => queueMicrotask(refresh));
    document.getElementById('review-clear')?.addEventListener('click', () => queueMicrotask(refresh));
    refresh();
  }
})();
</script>
"""


def build_handoff_report(payload: Mapping[str, object]) -> str:
    """Render the verified review report plus a local Markdown handoff of the visible subset."""
    rendered = build_review_report(payload)
    json_button = '<button id="review-export-json" type="button">Export visible JSON</button>'
    if json_button not in rendered or "</body>" not in rendered:
        raise ValueError("base review report has an unsupported layout")
    rendered = rendered.replace(json_button, json_button + "\n" + _MARKDOWN_BUTTON, 1)
    return rendered.replace("</body>", _MARKDOWN_SCRIPT + "\n</body>", 1)


def run(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Render standalone ECSS evidence review with JSON and Markdown visible-subset handoff."
    )
    parser.add_argument("bundle", help="Path to sanitized cdr_evidence_bundle JSON")
    parser.add_argument("output", help="Destination HTML path")
    args = parser.parse_args(argv)
    try:
        payload = json.loads(Path(args.bundle).read_text(encoding="utf-8"))
        if type(payload) is not dict:
            raise ValueError("bundle must be a JSON object")
        rendered = build_handoff_report(payload)
        Path(args.output).write_text(rendered, encoding="utf-8", newline="\n")
    except (OSError, TypeError, ValueError, json.JSONDecodeError, KeyError) as exc:
        print(f"cdr_evidence_handoff_report: {exc}", file=sys.stderr)
        return 2
    print(args.output)
    return 0


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
