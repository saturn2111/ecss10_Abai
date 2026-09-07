from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Mapping, Sequence

from tools.cdr_evidence_bundle import BUNDLE_WARNING
from tools.cdr_evidence_bundle_summary import SUMMARY_SCHEMA

DIFF_SCHEMA = "ecss-cdr-timing-evidence-bundle-summary-diff-v1"


def _validated_summary(payload: Mapping[str, object], name: str) -> dict[str, object]:
    if type(payload) is not dict:
        raise TypeError(f"{name} summary must be an exact object")
    if payload.get("schema") != SUMMARY_SCHEMA:
        raise ValueError(f"unsupported {name} summary schema")
    if payload.get("warning") != BUNDLE_WARNING:
        raise ValueError(f"{name} summary warning mismatch")

    values: dict[str, int] = {}
    for key in ("items", "records", "complete", "incomplete"):
        value = payload.get(key)
        if type(value) is not int or value < 0:
            raise ValueError(f"{name} summary {key} must be an exact non-negative integer")
        values[key] = value
    if values["complete"] + values["incomplete"] != values["records"]:
        raise ValueError(f"{name} summary record cardinality is inconsistent")

    evidence_counts = payload.get("evidence_counts")
    if type(evidence_counts) is not dict:
        raise TypeError(f"{name} evidence_counts must be an exact object")
    normalized_counts: dict[str, int] = {}
    for key, value in evidence_counts.items():
        if type(key) is not str or not key:
            raise ValueError(f"{name} evidence classification must be a non-empty exact string")
        if type(value) is not int or value < 0:
            raise ValueError(f"{name} evidence count must be an exact non-negative integer")
        normalized_counts[key] = value
    if sum(normalized_counts.values()) != values["items"]:
        raise ValueError(f"{name} evidence counts do not match item count")

    return {**values, "evidence_counts": normalized_counts}


def diff_summaries(before: Mapping[str, object], after: Mapping[str, object]) -> dict[str, object]:
    """Compare two evidence-only summaries without assigning call semantics."""

    left = _validated_summary(before, "before")
    right = _validated_summary(after, "after")
    evidence_names = sorted(set(left["evidence_counts"]) | set(right["evidence_counts"]))

    return {
        "schema": DIFF_SCHEMA,
        "delta": {
            key: int(right[key]) - int(left[key])
            for key in ("items", "records", "complete", "incomplete")
        },
        "evidence_count_delta": {
            name: int(right["evidence_counts"].get(name, 0))
            - int(left["evidence_counts"].get(name, 0))
            for name in evidence_names
        },
        "warning": BUNDLE_WARNING,
    }


def build_diff_json(before: Mapping[str, object], after: Mapping[str, object]) -> str:
    return json.dumps(
        diff_summaries(before, after),
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compare two sanitized ECSS evidence-bundle summaries without inferring queue semantics."
    )
    parser.add_argument("before", help="Earlier evidence-bundle summary JSON")
    parser.add_argument("after", help="Later evidence-bundle summary JSON")
    return parser


def run(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        with open(args.before, "r", encoding="utf-8") as handle:
            before = json.load(handle)
        with open(args.after, "r", encoding="utf-8") as handle:
            after = json.load(handle)
        print(build_diff_json(before, after))
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(f"cdr_evidence_bundle_summary_diff: {exc}", file=sys.stderr)
        return 2
    return 0


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
