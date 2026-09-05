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
        parsed = int(float(text.replace(",", ".")))
    except (ValueError, OverflowError):
        return None
    return parsed if parsed >= 0 else None


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


def correlation_evidence(caller_record_count: int, operator_record_count: int) -> str:
    """Describe exact-ref evidence without inferring a logical call relationship."""

    if caller_record_count == 1 and operator_record_count == 1:
        return "both_refs_unique"
    if caller_record_count > 0 and operator_record_count > 0:
        return "both_refs_present_with_duplicates"
    if caller_record_count > 0 or operator_record_count > 0:
        return "partial_ref_match"
    return "no_ref_match"


def operator_duration_evidence(
    positive_count: int,
    zero_count: int,
    invalid_count: int,
) -> str:
    """Describe operator-side T_ECD evidence without selecting or inferring a record."""

    total = positive_count + zero_count + invalid_count
    if total == 0:
        return "no_operator_duration_evidence"
    if positive_count == 1 and zero_count == 0 and invalid_count == 0:
        return "single_positive_duration_record"
    if positive_count > 1:
        return "multiple_positive_duration_records"
    if positive_count == 0 and zero_count == 1 and invalid_count == 0:
        return "single_zero_duration_record"
    if positive_count == 0 and zero_count == 0 and invalid_count == 1:
        return "single_invalid_duration_record"
    return "mixed_or_ambiguous_duration_records"


def operator_answer_delay_evidence(
    positive_count: int,
    zero_count: int,
    invalid_count: int,
) -> str:
    """Describe exact operator-side T_DBA evidence without inferring queue timing."""

    total = positive_count + zero_count + invalid_count
    if total == 0:
        return "no_operator_answer_delay_evidence"
    if positive_count == 1 and zero_count == 0 and invalid_count == 0:
        return "single_positive_answer_delay_record"
    if positive_count > 1:
        return "multiple_positive_answer_delay_records"
    if positive_count == 0 and zero_count == 1 and invalid_count == 0:
        return "single_zero_answer_delay_record"
    if positive_count == 0 and zero_count == 0 and invalid_count == 1:
        return "single_invalid_answer_delay_record"
    return "mixed_or_ambiguous_answer_delay_records"


def operator_timing_evidence(complete_count: int, incomplete_count: int) -> str:
    """Describe whether exact operator records carry both parsed timing metrics."""

    total = complete_count + incomplete_count
    if total == 0:
        return "no_operator_timing_evidence"
    if complete_count == 1 and incomplete_count == 0:
        return "single_complete_timing_record"
    if complete_count > 1:
        return "multiple_complete_timing_records"
    if complete_count == 0 and incomplete_count == 1:
        return "single_incomplete_timing_record"
    if complete_count == 0:
        return "no_complete_timing_records"
    return "mixed_complete_and_incomplete_timing_records"


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
    operator_zero = [
        item for item in operator_records if item.conversation_seconds == 0
    ]
    operator_invalid = [
        item for item in operator_records if item.conversation_seconds is None
    ]
    operator_answer_delay_positive = [
        item for item in operator_records if (item.answer_delay_seconds or 0) > 0
    ]
    operator_answer_delay_zero = [
        item for item in operator_records if item.answer_delay_seconds == 0
    ]
    operator_answer_delay_invalid = [
        item for item in operator_records if item.answer_delay_seconds is None
    ]
    operator_complete_timing = [
        item
        for item in operator_records
        if item.conversation_seconds is not None
        and item.answer_delay_seconds is not None
    ]
    operator_incomplete_timing = [
        item
        for item in operator_records
        if item.conversation_seconds is None
        or item.answer_delay_seconds is None
    ]

    selected_operator: CdrRecord | None = None
    selection_reason = "no_operator_record"
    if len(operator_positive) == 1:
        selected_operator = operator_positive[0]
        selection_reason = "single_positive_t_ecd_operator_record"
    elif len(operator_positive) > 1:
        selection_reason = "ambiguous_multiple_positive_operator_records"
    elif len(operator_records) == 1:
        if operator_records[0].conversation_seconds is None:
            selection_reason = "invalid_operator_t_ecd"
        else:
            selected_operator = operator_records[0]
            selection_reason = "single_operator_record"
    elif len(operator_records) > 1:
        selection_reason = "ambiguous_multiple_operator_records"

    caller_ref_matched = bool(caller_records)
    operator_ref_matched = bool(operator_records)
    caller_ref_unique = len(caller_records) == 1
    operator_ref_unique = len(operator_records) == 1
    selected_operator_has_complete_timing = bool(
        selected_operator
        and selected_operator.conversation_seconds is not None
        and selected_operator.answer_delay_seconds is not None
    )

    return {
        "caller_call_ref": caller_call_ref,
        "operator_call_ref": operator_call_ref,
        "caller_record_count": len(caller_records),
        "operator_record_count": len(operator_records),
        "matched_record_count": len(matches),
        "caller_ref_matched": caller_ref_matched,
        "operator_ref_matched": operator_ref_matched,
        "both_refs_matched": caller_ref_matched and operator_ref_matched,
        "caller_ref_unique": caller_ref_unique,
        "operator_ref_unique": operator_ref_unique,
        "both_refs_unique": caller_ref_unique and operator_ref_unique,
        "operator_positive_duration_record_count": len(operator_positive),
        "operator_zero_duration_record_count": len(operator_zero),
        "operator_invalid_duration_record_count": len(operator_invalid),
        "operator_duration_evidence": operator_duration_evidence(
            len(operator_positive), len(operator_zero), len(operator_invalid)
        ),
        "operator_positive_answer_delay_record_count": len(operator_answer_delay_positive),
        "operator_zero_answer_delay_record_count": len(operator_answer_delay_zero),
        "operator_invalid_answer_delay_record_count": len(operator_answer_delay_invalid),
        "operator_answer_delay_evidence": operator_answer_delay_evidence(
            len(operator_answer_delay_positive),
            len(operator_answer_delay_zero),
            len(operator_answer_delay_invalid),
        ),
        "operator_complete_timing_record_count": len(operator_complete_timing),
        "operator_incomplete_timing_record_count": len(operator_incomplete_timing),
        "operator_timing_evidence": operator_timing_evidence(
            len(operator_complete_timing), len(operator_incomplete_timing)
        ),
        "correlation_evidence": correlation_evidence(
            len(caller_records), len(operator_records)
        ),
        "selected_operator_conn_id": selected_operator.conn_id if selected_operator else None,
        "selected_operator_has_complete_timing": selected_operator_has_complete_timing,
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
        "caller_ref_matched": False,
        "operator_ref_matched": False,
        "both_refs_matched": False,
        "caller_ref_unique": False,
        "operator_ref_unique": False,
        "both_refs_unique": False,
        "operator_positive_duration_record_count": 0,
        "operator_zero_duration_record_count": 0,
        "operator_invalid_duration_record_count": 0,
        "operator_duration_evidence": "not_evaluated",
        "operator_positive_answer_delay_record_count": 0,
        "operator_zero_answer_delay_record_count": 0,
        "operator_invalid_answer_delay_record_count": 0,
        "operator_answer_delay_evidence": "not_evaluated",
        "operator_complete_timing_record_count": 0,
        "operator_incomplete_timing_record_count": 0,
        "operator_timing_evidence": "not_evaluated",
        "correlation_evidence": "not_evaluated",
        "selected_operator_conn_id": None,
        "selected_operator_has_complete_timing": False,
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