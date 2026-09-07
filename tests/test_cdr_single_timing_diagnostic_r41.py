import pytest

from tools.cdr_caller_timing_evidence import caller_has_single_timing_record


@pytest.mark.parametrize(
    ("complete_count", "incomplete_count", "expected"),
    [
        (0, 0, False),
        (1, 0, True),
        (0, 1, True),
        (2, 0, False),
        (0, 2, False),
        (1, 1, False),
    ],
)
def test_single_timing_record_is_exact_cardinality_diagnostic(
    complete_count: int,
    incomplete_count: int,
    expected: bool,
) -> None:
    assert caller_has_single_timing_record(complete_count, incomplete_count) is expected


@pytest.mark.parametrize("value", [True, False, 1.0, "1", None])
def test_single_timing_record_rejects_non_exact_integer_counts(value: object) -> None:
    with pytest.raises(TypeError):
        caller_has_single_timing_record(value, 0)  # type: ignore[arg-type]


@pytest.mark.parametrize("counts", [(-1, 0), (0, -1)])
def test_single_timing_record_rejects_negative_counts(counts: tuple[int, int]) -> None:
    with pytest.raises(ValueError):
        caller_has_single_timing_record(*counts)
