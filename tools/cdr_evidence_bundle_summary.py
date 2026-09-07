from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from collections.abc import Mapping, Sequence

from tools.cdr_evidence_bundle import BUNDLE_SCHEMA, BUNDLE_WARNING

SUMMARY_SCHEMA = "ecss-cdr-timing-evidence-bundle-summary-v1"


def summarize_bundle(payload: Mapping[str, object]) -> dict[str, object]:
    """Summarize evidence classifications without inventing call semantics."""

    if type(payload) is not dict:
        raise TypeError("evidence bundle must be an exact object")
    if payload.get("schema") != BUNDLE_SCHEMA:
        raise ValueError("unsupported evidence bundle schema")
    if payload.get("warning") != BUNDLE_WARNING:
        raise ValueError("evidence bundle warning mismatch")

    items = payload.get("items")
    if type(items) is not list:
        raise TypeError("evidence bundle items must be an exact list")

    counts: Counter[str] = Counter()
    total_records = 0
    total_complete = 0
    total_incomplete = 0
    for item in items:
        if type(item) is not dict:
            raise TypeError("bundle item must be an exact object")
        report = item.get("report")
        if type(report) is not dict:
            raise TypeError("bundle report must be an exact object")
        evidence = report.get("evidence")
        if type(evidence) is not str or not evidence:
            raise ValueError("bundle report evidence must be a non-empty exact string")
        values: list[int] = []
        for key in ("records", "complete", "incomplete"):
            value = report.get(key)
            if type(value) is not int or value < 0:
                raise ValueError(f"bundle report {key} must be an exact non-negative integer")
            values.append(value)
        records, complete, incomplete = values
        if complete + incomplete != records:
            raise ValueError("bundle report cardinality is inconsistent")
        counts[evidence] += 1
        total_records += records
        total_complete += complete
        total_incomplete += incomplete

    return {
        "schema": SUMMARY_SCHEMA,
        "items": len(items),
        "records": total_records,
        "complete": total_complete,
        "incomplete": total_incomplete,
        "evidence_counts": dict(sorted(counts.items())),
        "warning": BUNDLE_WARNING,
    }


def build_summary_json(payload: Mapping[str, object]) -> str:
    return json.dumps(
        summarize_bundle(payload),
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Summarize a sanitized ECSS CDR evidence bundle without inferring queue semantics."
    )
    parser.add_argument("bundle", help="Path to an evidence-bundle JSON artifact")
    return parser


def run(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        with open(args.bundle, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
        print(build_summary_json(payload))
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(f"cdr_evidence_bundle_summary: {exc}", file=sys.stderr)
        return 2
    return 0


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
