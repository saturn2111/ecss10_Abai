from __future__ import annotations

from tools.cdr_queue_analyzer import (
    CdrRecord,
    analyze_queue_call,
    correlation_evidence,
    operator_answer_delay_evidence,
    operator_duration_evidence,
    operator_timing_evidence,
)


def record(
    conn_id: str,
    duration: int | None = 10,
    answer_delay: int | None = 1,
) -> CdrRecord:
    return CdrRecord(
        conn_id=conn_id,
        conversation_seconds=duration,
        answer_delay_seconds=answer_delay,
        raw={},
    )


def test_exact_unique_refs_report_unique_evidence() -> None:
    result = analyze_queue_call(
        [record("caller", 0), record("operator", 12)],
        caller_call_ref="caller",
        operator_call_ref="operator",
    )

    assert result["correlation_evidence"] == "both_refs_unique"
    assert result["caller_ref_unique"] is True
    assert result["operator_ref_unique"] is True
    assert result["both_refs_unique"] is True
    assert result["operator_positive_duration_record_count"] == 1
    assert result["operator_zero_duration_record_count"] == 0
    assert result["operator_invalid_duration_record_count"] == 0
    assert result["operator_duration_evidence"] == "single_positive_duration_record"
    assert result["operator_positive_answer_delay_record_count"] == 1
    assert result["operator_zero_answer_delay_record_count"] == 0
    assert result["operator_invalid_answer_delay_record_count"] == 0
    assert result["operator_answer_delay_evidence"] == "single_positive_answer_delay_record"
    assert result["operator_complete_timing_record_count"] == 1
    assert result["operator_incomplete_timing_record_count"] == 0
    assert result["operator_timing_evidence"] == "single_complete_timing_record"


def test_duplicate_exact_ref_records_are_not_reported_as_unique() -> None:
    result = analyze_queue_call(
        [record("caller", 0), record("caller", 0), record("operator", 12)],
        caller_call_ref="caller",
        operator_call_ref="operator",
    )

    assert result["correlation_evidence"] == "both_refs_present_with_duplicates"
    assert result["caller_ref_unique"] is False
    assert result["operator_ref_unique"] is True
    assert result["both_refs_unique"] is False


def test_operator_duration_evidence_counts_are_explicit() -> None:
    result = analyze_queue_call(
        [
            record("caller", 0),
            record("operator", 12),
            record("operator", 0),
            record("operator", None),
        ],
        caller_call_ref="caller",
        operator_call_ref="operator",
    )

    assert result["operator_positive_duration_record_count"] == 1
    assert result["operator_zero_duration_record_count"] == 1
    assert result["operator_invalid_duration_record_count"] == 1
    assert result["operator_record_count"] == 3
    assert result["operator_duration_evidence"] == "mixed_or_ambiguous_duration_records"


def test_operator_answer_delay_evidence_counts_are_explicit() -> None:
    result = analyze_queue_call(
        [
            record("caller", 0),
            record("operator", 12, 5),
            record("operator", 0, 0),
            record("operator", None, None),
        ],
        caller_call_ref="caller",
        operator_call_ref="operator",
    )

    assert result["operator_positive_answer_delay_record_count"] == 1
    assert result["operator_zero_answer_delay_record_count"] == 1
    assert result["operator_invalid_answer_delay_record_count"] == 1
    assert result["operator_answer_delay_evidence"] == "mixed_or_ambiguous_answer_delay_records"


def test_operator_complete_timing_counts_are_same_record_evidence() -> None:
    result = analyze_queue_call(
        [
            record("caller", 0),
            record("operator", 12, 5),
            record("operator", 7, None),
            record("operator", None, 2),
        ],
        caller_call_ref="caller",
        operator_call_ref="operator",
    )

    assert result["operator_complete_timing_record_count"] == 1
    assert result["operator_incomplete_timing_record_count"] == 2
    assert result["operator_timing_evidence"] == "mixed_complete_and_incomplete_timing_records"


def test_duration_evidence_helper_is_deterministic() -> None:
    assert operator_duration_evidence(0, 0, 0) == "no_operator_duration_evidence"
    assert operator_duration_evidence(1, 0, 0) == "single_positive_duration_record"
    assert operator_duration_evidence(2, 0, 0) == "multiple_positive_duration_records"
    assert operator_duration_evidence(0, 1, 0) == "single_zero_duration_record"
    assert operator_duration_evidence(0, 0, 1) == "single_invalid_duration_record"
    assert operator_duration_evidence(1, 1, 0) == "mixed_or_ambiguous_duration_records"


def test_answer_delay_evidence_helper_is_deterministic() -> None:
    assert operator_answer_delay_evidence(0, 0, 0) == "no_operator_answer_delay_evidence"
    assert operator_answer_delay_evidence(1, 0, 0) == "single_positive_answer_delay_record"
    assert operator_answer_delay_evidence(2, 0, 0) == "multiple_positive_answer_delay_records"
    assert operator_answer_delay_evidence(0, 1, 0) == "single_zero_answer_delay_record"
    assert operator_answer_delay_evidence(0, 0, 1) == "single_invalid_answer_delay_record"
    assert operator_answer_delay_evidence(1, 1, 0) == "mixed_or_ambiguous_answer_delay_records"


def test_timing_evidence_helper_is_deterministic() -> None:
    assert operator_timing_evidence(0, 0) == "no_operator_timing_evidence"
    assert operator_timing_evidence(1, 0) == "single_complete_timing_record"
    assert operator_timing_evidence(2, 0) == "multiple_complete_timing_records"
    assert operator_timing_evidence(0, 1) == "single_incomplete_timing_record"
    assert operator_timing_evidence(0, 2) == "no_complete_timing_records"
    assert operator_timing_evidence(1, 2) == "mixed_complete_and_incomplete_timing_records"


def test_partial_match_is_explicit() -> None:
    result = analyze_queue_call(
        [record("caller", 0)],
        caller_call_ref="caller",
        operator_call_ref="operator",
    )

    assert result["correlation_evidence"] == "partial_ref_match"
    assert result["caller_ref_unique"] is True
    assert result["operator_ref_unique"] is False
    assert result["both_refs_unique"] is False
    assert result["operator_positive_duration_record_count"] == 0
    assert result["operator_zero_duration_record_count"] == 0
    assert result["operator_invalid_duration_record_count"] == 0
    assert result["operator_duration_evidence"] == "no_operator_duration_evidence"
    assert result["operator_positive_answer_delay_record_count"] == 0
    assert result["operator_zero_answer_delay_record_count"] == 0
    assert result["operator_invalid_answer_delay_record_count"] == 0
    assert result["operator_answer_delay_evidence"] == "no_operator_answer_delay_evidence"
    assert result["operator_complete_timing_record_count"] == 0
    assert result["operator_incomplete_timing_record_count"] == 0
    assert result["operator_timing_evidence"] == "no_operator_timing_evidence"


def test_invalid_ref_pair_is_not_evaluated() -> None:
    result = analyze_queue_call(
        [],
        caller_call_ref="same",
        operator_call_ref="same",
    )

    assert result["correlation_evidence"] == "not_evaluated"
    assert result["caller_ref_unique"] is False
    assert result["operator_ref_unique"] is False
    assert result["both_refs_unique"] is False
    assert result["operator_positive_duration_record_count"] == 0
    assert result["operator_zero_duration_record_count"] == 0
    assert result["operator_invalid_duration_record_count"] == 0
    assert result["operator_duration_evidence"] == "not_evaluated"
    assert result["operator_positive_answer_delay_record_count"] == 0
    assert result["operator_zero_answer_delay_record_count"] == 0
    assert result["operator_invalid_answer_delay_record_count"] == 0
    assert result["operator_answer_delay_evidence"] == "not_evaluated"
    assert result["operator_complete_timing_record_count"] == 0
    assert result["operator_incomplete_timing_record_count"] == 0
    assert result["operator_timing_evidence"] == "not_evaluated"


def test_evidence_helper_reports_no_match() -> None:
    assert correlation_evidence(0, 0) == "no_ref_match"
