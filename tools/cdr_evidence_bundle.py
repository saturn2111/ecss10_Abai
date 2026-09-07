from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence

from tools.cdr_queue_analyzer import load_cdr
from tools.cdr_timing_report import build_caller_timing_report_json

BUNDLE_SCHEMA = "ecss-cdr-timing-evidence-bundle-v1"
BUNDLE_WARNING = (
    "evidence-only bundle; queue membership, queue wait, logical call identity "
    "and final duration are not inferred"
)


def build_evidence_bundle_payload(
    items: Sequence[tuple[str, dict[str, object]]],
) -> dict[str, object]:
    """Build one deterministic bundle from already-derived evidence reports."""

    seen: set[str] = set()
    bundled: list[dict[str, object]] = []
    for label, report in items:
        if type(label) is not str or not label or label.strip() != label:
            raise ValueError("bundle labels must be exact non-empty strings without edge whitespace")
        if label in seen:
            raise ValueError(f"duplicate bundle label: {label}")
        if type(report) is not dict:
            raise TypeError("bundle report must be an exact dict")
        seen.add(label)
        bundled.append({"label": label, "report": report})

    return {
        "schema": BUNDLE_SCHEMA,
        "items": bundled,
        "warning": BUNDLE_WARNING,
    }


def build_evidence_bundle_json(
    items: Sequence[tuple[str, dict[str, object]]],
) -> str:
    return json.dumps(
        build_evidence_bundle_payload(items),
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Bundle multiple sanitized ECSS CDR caller-timing evidence artifacts. "
            "No queue or final-duration semantics are inferred."
        )
    )
    parser.add_argument(
        "--item",
        action="append",
        nargs=3,
        metavar=("LABEL", "CDR", "CALLER_REF"),
        required=True,
        help="Repeat for each sanitized CDR evidence item",
    )
    return parser


def run(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    items: list[tuple[str, dict[str, object]]] = []
    try:
        for label, cdr_path, caller_ref in args.item:
            records = load_cdr(cdr_path)
            report = json.loads(
                build_caller_timing_report_json(records, caller_call_ref=caller_ref)
            )
            if type(report) is not dict:
                raise ValueError("timing report JSON must decode to an object")
            items.append((label, report))
        rendered = build_evidence_bundle_json(items)
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(f"cdr_evidence_bundle: {exc}", file=sys.stderr)
        return 2

    print(rendered)
    return 0


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
