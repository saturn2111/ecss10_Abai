from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path

from tools.cdr_evidence_bundle import BUNDLE_SCHEMA, BUNDLE_WARNING

COLUMNS = (
    "label",
    "caller_ref",
    "records",
    "complete",
    "incomplete",
    "evidence",
    "raw_t_ecd_seconds",
    "raw_t_dba_seconds",
)


def _cell(value: object) -> str:
    if value is None:
        return "n/a"
    return str(value)


def render_bundle_table(payload: Mapping[str, object]) -> str:
    """Render a deterministic evidence-only TSV summary from a verified bundle."""
    if payload.get("schema") != BUNDLE_SCHEMA:
        raise ValueError("unsupported evidence bundle schema")
    if payload.get("warning") != BUNDLE_WARNING:
        raise ValueError("evidence bundle warning contract is missing or changed")

    items = payload.get("items")
    if type(items) is not list:
        raise ValueError("evidence bundle items must be a list")

    lines = ["\t".join(COLUMNS)]
    for item in items:
        if type(item) is not dict or type(item.get("label")) is not str:
            raise ValueError("invalid evidence bundle item")
        report = item.get("report")
        if type(report) is not dict:
            raise ValueError("invalid evidence bundle report")
        row = (
            item["label"],
            report.get("caller_ref"),
            report.get("records"),
            report.get("complete"),
            report.get("incomplete"),
            report.get("evidence"),
            report.get("raw_t_ecd_seconds"),
            report.get("raw_t_dba_seconds"),
        )
        lines.append("\t".join(_cell(value) for value in row))

    lines.append(f"warning\t{BUNDLE_WARNING}")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Render a human-readable evidence-only table from a sanitized ECSS CDR bundle."
    )
    parser.add_argument("--bundle", required=True, help="Path to a JSON bundle from cdr_evidence_bundle.py")
    return parser


def run(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        payload = json.loads(Path(args.bundle).read_text(encoding="utf-8"))
        if type(payload) is not dict:
            raise ValueError("bundle JSON must contain an object")
        rendered = render_bundle_table(payload)
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(f"cdr_evidence_bundle_report: {exc}", file=sys.stderr)
        return 2
    print(rendered)
    return 0


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
