from __future__ import annotations

from collections.abc import Iterable

from tools.cdr_queue_analyzer import CdrRecord


def caller_timing_evidence(complete_count: int, incomplete_count: int) -> str:
    """Classify exact caller-ref timing rows without inferring queue semantics."""

    if type(complete_count) is not int or type(incomplete_count) is not int:
        raise TypeError("caller timing counts must be exact integers")
    if complete_count < 0 or incomplete_count < 0:
        raise ValueError("caller timing counts must be non-negative")

    total = complete_count + incomplete_count
    if total == 0:
        return "no_caller_timing_evidence"
    if complete_count == 1 and incomplete_count == 0:
        return "single_complete_caller_timing_record"
    if complete_count > 1 and incomplete_count == 0:
        return "multiple_complete_caller_timing_records"
    if complete_count == 0 and incomplete_count == 1:
        return "single_incomplete_caller_timing_record"
    if complete_count == 0:
        return "no_complete_caller_timing_records"
    return "mixed_complete_and_incomplete_caller_timing_records"


def summarize_caller_timing(
    records: Iterable[CdrRecord],
    *,
    caller_call_ref: str,
) -> dict[str, object]:
    """Summarize timing completeness for exact CONN_ID == caller_call_ref rows only.

    Exact T_ECD/T_DBA values are surfaced only when the caller ref resolves to one
    complete row and no competing incomplete row. They remain raw field evidence:
    this helper does not infer queue membership, queue wait, logical call identity,
    or final duration semantics.
    """

    caller_call_ref = caller_call_ref.strip()
    if not caller_call_ref:
        return {
            "caller_call_ref": caller_call_ref,
            "caller_record_count": 0,
            "caller_complete_timing_record_count": 0,
            "caller_incomplete_timing_record_count": 0,
            "caller_timing_evidence": "not_evaluated",
            "caller_t_ecd_seconds": None,
            "caller_t_dba_seconds": None,
        }

    caller_records = tuple(
        record for record in records if record.conn_id == caller_call_ref
    )
    complete = tuple(
        record
        for record in caller_records
        if record.conversation_seconds is not None
        and record.answer_delay_seconds is not None
    )
    incomplete_count = len(caller_records) - len(complete)
    unique_complete = complete[0] if len(complete) == 1 and incomplete_count == 0 else None

    return {
        "caller_call_ref": caller_call_ref,
        "caller_record_count": len(caller_records),
        "caller_complete_timing_record_count": len(complete),
        "caller_incomplete_timing_record_count": incomplete_count,
        "caller_timing_evidence": caller_timing_evidence(
            len(complete), incomplete_count
        ),
        "caller_t_ecd_seconds": (
            unique_complete.conversation_seconds if unique_complete is not None else None
        ),
        "caller_t_dba_seconds": (
            unique_complete.answer_delay_seconds if unique_complete is not None else None
        ),
    }
