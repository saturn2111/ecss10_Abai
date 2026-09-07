import pytest

from tools.cdr_caller_timing_evidence import caller_has_complete_timing_records


def test_complete_timing_diagnostic_reports_presence_only():
    assert caller_has_complete_timing_records(0, 0) is False
    assert caller_has_complete_timing_records(0, 2) is False
    assert caller_has_complete_timing_records(1, 0) is True
    assert caller_has_complete_timing_records(2, 3) is True


@pytest.mark.parametrize("complete_count,incomplete_count", [(True, 0), (1.0, 0), ("1", 0), (0, False)])
def test_complete_timing_diagnostic_rejects_non_exact_integer_counts(complete_count, incomplete_count):
    with pytest.raises(TypeError):
        caller_has_complete_timing_records(complete_count, incomplete_count)


@pytest.mark.parametrize("complete_count,incomplete_count", [(-1, 0), (0, -1)])
def test_complete_timing_diagnostic_rejects_negative_counts(complete_count, incomplete_count):
    with pytest.raises(ValueError):
        caller_has_complete_timing_records(complete_count, incomplete_count)
