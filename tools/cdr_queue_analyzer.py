from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Iterable


REQUIRED_COLUMNS = ("CONN_ID", "T_ECD", "T_DBA")


@dataclass(frozen=True, slots=True)
class CdrRecord:
    conn_id: str
    conversation_seconds: int | None
    answer_delay_seconds: int | None
    raw: dict[str, str]


def _to_int(value: str | None) -> int | None:
    text = (value or "").strip()
    if not text:
        return None
    try:
        return int(float(text.replace(",", ".")))
    except ValueError:
        return None


def _detect_dialect(sample: str) -> csv.Dialect:
    try:
        return csv.Sniffer().sniff(sample, delimiters=",;\t|")
    except csv.Error:
        return csv.excel


def load_cdr(path: str | Path) -> list[CdrRecord]:
    cdr_path = Path(path)
    sample = cdr_path.read_text(encoding="utf-8-sig")
    dialect = _detect_dialect(sample[:8192])

    rows: list[CdrRecord] = []
    reader = csv.DictReader(sample.splitlines(), dialect=dialect)
    fieldnames = tuple(name.strip() for name in (reader.fieldnames or ()))
    missing = [name for name in REQUIRED_COLUMNS if name not in fieldnames]
    if missing:
        raise ValueError(f"CDR is missing required columns: {', '.join(missing)}")

    duplicate_required = [
        name for name in REQUIRED_COLUMNS if fieldnames.count(name) > 1
    ]
    if duplicate_required:
        raise ValueError(
            "CDR has duplicate required columns: " + ", ".join(duplicate_required)
        )

    for raw_row in reader:
        normalized = {
            (key or "").strip(): (value or "").strip()
            for key, value in raw_row.items()
        }
        conn_id = normalized.get("CONN_ID", "")
        if not conn_id:
            continue
        rows.append(
            CdrRecord(
                conn_id=conn_id,
                conversation_seconds=_to_int(normalized.get("T_ECD")),
                answer_delay_seconds=_to_int(normalized.get("T_DBA")),
                raw=normalized,
            )
        )
    return rows


def matching_records(
    records: Iterable[CdrRecord],
    call_refs: Iterable[str],
) -> tuple[CdrRecord, ...]:
    wanted = {value.strip() for value in call_refs if value.strip()}
    return tuple(record for record in records if record.conn_id in wanted)


def analyze_queue_call(
    records: Iterable[CdrRecord],
    *,
    caller_call_ref: str,
    operator_call_ref: str,
) -> dict[str, object]:
    caller_call_ref = caller_call_ref.strip()
    operator_call_ref = operator_call_ref.strip()

    if not caller_call_ref or not operator_call_ref:
        return _empty_result(caller_call_ref, operator_call_ref, "missing_call_ref")

    if caller_call_ref == operator_call_ref:
        return _empty_result(caller_call_ref, operator_call_ref, "ambiguous_same_call_ref")

    record_list = tuple(records)
    matches = matching_records(record_list, (caller_call_ref, operator_call_ref))

    by_ref: dict[str, list[CdrRecord]] = {}
    for record in matches:
        by_ref.setdefault(record.conn_id, []).append(record)

    caller_records = by_ref.get(caller_call_ref, [])
    operator_records = by_ref.get(operator_call_ref, [])
    operator_positive = [
        item for item in operator_records if (item.conversation_seconds or 0) > 0
    ]

    selected_operator: CdrRecord | None = None
    selection_reason = "no_operator_record"
    if len(operator_positive) == 1:
        selected_operator = operator_positive[0]
        selection_reason = "single_positive_t_ecd_operator_record"
    elif len(operator_positive) > 1:
        # Multiple positive rows for the same operator call_ref are ambiguous.
        # Do not guess by selecting the largest T_ECD; the actual live CDR must
        # establish the semantics before Duration can be considered confirmed.
        selection_reason = "ambiguous_multiple_positive_operator_records"
    elif len(operator_records) == 1:
        selected_operator = operator_records[0]
        selection_reason = "single_operator_record"
    elif len(operator_records) > 1:
        selection_reason = "ambiguous_multiple_operator_records"

    return {
        "caller_call_ref": caller_call_ref,
        "operator_call_ref": operator_call_ref,
        "caller_record_count": len(caller_records),
        "operator_record_count": len(operator_records),
        "matched_record_count": len(matches),
        "selected_operator_conn_id": selected_operator.conn_id if selected_operator else None,
        "duration_seconds": selected_operator.conversation_seconds if selected_operator else None,
        "answer_delay_seconds": selected_operator.answer_delay_seconds if selected_operator else None,
        "selection_reason": selection_reason,
        "operator_duration_confirmed": bool(
            selected_operator
            and selected_operator.conversation_seconds is not None
            and selected_operator.conversation_seconds > 0
        ),
    }


def _empty_result(caller_call_ref: str, operator_call_ref: str, reason: str) -> dict[str, object]:
    return {
        "caller_call_ref": caller_call_ref,
        "operator_call_ref": operator_call_ref,
        "caller_record_count": 0,
        "operator_record_count": 0,
        "matched_record_count": 0,
        "selected_operator_conn_id": None,
        "duration_seconds": None,
        "answer_delay_seconds": None,
        "selection_reason": reason,
        "operator_duration_confirmed": False,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Correlate ECSS queue-call CDR records with live Call API call_ref values. "
            "The tool does not infer a logical call id; caller/operator refs must be "
            "supplied from the captured conversations_event data."
        )
    )
    parser.add_argument("csv", type=Path, help="ECSS CDR CSV file")
    parser.add_argument("--caller-ref", required=True, help="caller/IVR call_ref")
    parser.add_argument("--operator-ref", required=True, help="answered operator call_ref")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    records = load_cdr(args.csv)
    result = analyze_queue_call(
        records,
        caller_call_ref=args.caller_ref,
        operator_call_ref=args.operator_ref,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["operator_duration_confirmed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
