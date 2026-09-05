from __future__ import annotations

from tools.cdr_queue_analyzer import CdrRecord
from tools.cdr_selected_timing_evidence import selected_operator_missing_timing_fields


def _record(duration: int | None, delay: int | None) -> CdrRecord:
    return CdrRecord(
        conn_id="operator-ref",
        conversation_seconds=duration,
        answer_delay_seconds=delay,
        raw={},
    )


def test_selected_operator_missing_timing_fields_are_deterministic() -> None:
    assert selected_operator_missing_timing_fields(None) == ()
    assert selected_operator_missing_timing_fields(_record(12, 3)) == ()
    assert selected_operator_missing_timing_fields(_record(None, 3)) == ("T_ECD",)
    assert selected_operator_missing_timing_fields(_record(12, None)) == ("T_DBA",)
    assert selected_operator_missing_timing_fields(_record(None, None)) == ("T_ECD", "T_DBA")


def test_zero_timing_values_are_present_not_missing() -> None:
    assert selected_operator_missing_timing_fields(_record(0, 0)) == ()
