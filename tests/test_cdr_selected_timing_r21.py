from tools.cdr_queue_analyzer import CdrRecord
from tools.cdr_selected_timing import selected_operator_timing_values


def _record(duration, answer_delay):
    return CdrRecord(
        conn_id="operator-ref",
        conversation_seconds=duration,
        answer_delay_seconds=answer_delay,
        raw={},
    )


def test_complete_selected_operator_timing_is_exposed():
    assert selected_operator_timing_values(_record(37, 5)) == (37, 5)


def test_zero_values_are_real_complete_evidence():
    assert selected_operator_timing_values(_record(0, 0)) == (0, 0)


def test_incomplete_or_missing_selection_fails_closed():
    assert selected_operator_timing_values(None) is None
    assert selected_operator_timing_values(_record(None, 5)) is None
    assert selected_operator_timing_values(_record(37, None)) is None
