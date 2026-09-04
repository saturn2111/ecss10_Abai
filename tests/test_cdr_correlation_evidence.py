from __future__ import annotations

from tools.cdr_queue_analyzer import CdrRecord, analyze_queue_call, correlation_evidence


def record(conn_id: str, duration: int | None = 10) -> CdrRecord:
    return CdrRecord(
        conn_id=conn_id,
        conversation_seconds=duration,
        answer_delay_seconds=1,
        raw={},
    )


def test_exact_unique_refs_report_unique_evidence() -> None:
    result = analyze_queue_call(
        [record("caller", 0), record("operator", 12)],
        caller_call_ref="caller",
        operator_call_ref="operator",
    )

    assert result["correlation_evidence"] == "both_refs_unique"


def test_duplicate_exact_ref_records_are_not_reported_as_unique() -> None:
    result = analyze_queue_call(
        [record("caller", 0), record("caller", 0), record("operator", 12)],
        caller_call_ref="caller",
        operator_call_ref="operator",
    )

    assert result["correlation_evidence"] == "both_refs_present_with_duplicates"


def test_partial_match_is_explicit() -> None:
    result = analyze_queue_call(
        [record("caller", 0)],
        caller_call_ref="caller",
        operator_call_ref="operator",
    )

    assert result["correlation_evidence"] == "partial_ref_match"


def test_invalid_ref_pair_is_not_evaluated() -> None:
    result = analyze_queue_call(
        [],
        caller_call_ref="same",
        operator_call_ref="same",
    )

    assert result["correlation_evidence"] == "not_evaluated"


def test_evidence_helper_reports_no_match() -> None:
    assert correlation_evidence(0, 0) == "no_ref_match"
