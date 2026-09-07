from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from tools.cdr_queue_analyzer import load_cdr
from tools.cdr_timing_report import (
    build_caller_timing_report,
    build_caller_timing_report_json,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Render evidence-only caller timing from a sanitized ECSS CDR export. "
            "No queue or final-duration semantics are inferred."
        )
    )
    parser.add_argument("cdr", help="Path to a sanitized CDR CSV/TSV export")
    parser.add_argument("--caller-ref", required=True, help="Exact caller CONN_ID/call_ref")
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Deterministic output format",
    )
    return parser


def run(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        records = load_cdr(args.cdr)
        if args.format == "json":
            rendered = build_caller_timing_report_json(
                records,
                caller_call_ref=args.caller_ref,
            )
        else:
            rendered = build_caller_timing_report(
                records,
                caller_call_ref=args.caller_ref,
            )
    except (OSError, TypeError, ValueError) as exc:
        print(f"cdr_timing_cli: {exc}", file=sys.stderr)
        return 2

    print(rendered)
    return 0


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
