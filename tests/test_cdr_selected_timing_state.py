from __future__ import annotations

from tools.cdr_queue_analyzer import CdrRecord, analyze_queue_call, selected_operator_timing_state


def _record(conn_id: str, duration: int | None, delay: int | None) -> CdrRecord:
    return CdrRecord(
        conn_id=conn_id,
        conversation_seconds=duration,
        answer_delay_seconds=delay,
        raw={},
    )


def test_selected_operator_timing_state_is_deterministic() -> None:
    assert selected_operator_timing_state(None) == "no_selected_operator_record"
    assert selected_operator_timing_state(_record("op", 12, 3)) == "complete_timing"
    assert selected_operator_timing_state(_record("op", 12, None)) == "missing_answer_delay"
    assert selected_operator_timing_state(_record("op", None, 3)) == "missing_duration"
    assert selected_operator_timing_state(_record("op", None, None)) == "missing_duration_and_answer_delay"


def test_zero_values_are_present_timing_evidence_not_missing_fields() -> None:
    record = _record("operator", 0, 0)

    assert selected_operator_timing_state(record) == "complete_timing"

    result = analyze_queue_call(
        (_record("caller", 0, 0), record),
        caller_call_ref="caller",
        operator_call_ref="operator",
    )
    assert result["selected_operator_conn_id"] == "operator"
    assert result["selected_operator_timing_state"] == "complete_timing"
    assert result["selected_operator_has_complete_timing"] is True
    assert result["duration_seconds"] == 0
    assert result["answer_delay_seconds"] == 0
    assert result["operator_duration_confirmed"] is False


def test_analyzer_reports_state_only_for_already_selected_exact_operator_record() -> None:
    result = analyze_queue_call(
        (_record("caller", 0, 0), _record("operator", 12, None)),
        caller_call_ref="caller",
        operator_call_ref="operator",
    )

    assert result["selected_operator_conn_id"] == "operator"
    assert result["selected_operator_timing_state"] == "missing_answer_delay"
    assert result["selected_operator_has_complete_timing"] is False


def test_ambiguous_operator_selection_does_not_infer_timing_state() -> None:
    result = analyze_queue_call(
        (
            _record("caller", 0, 0),
            _record("operator", 12, 1),
            _record("operator", 15, 2),
        ),
        caller_call_ref="caller",
        operator_call_ref="operator",
    )

    assert result["selected_operator_conn_id"] is None
    assert result["selected_operator_timing_state"] == "no_selected_operator_record"
    assert result["selection_reason"] == "ambiguous_multiple_positive_operator_records"
