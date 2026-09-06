import pytest

from tools.cdr_caller_timing_evidence import summarize_caller_timing


@pytest.mark.parametrize("bad_ref", [None, 123, True, b"ref"])
def test_caller_call_ref_requires_exact_string(bad_ref) -> None:
    with pytest.raises(TypeError, match="exact string"):
        summarize_caller_timing((), caller_call_ref=bad_ref)


def test_blank_string_still_fails_closed_without_evidence() -> None:
    summary = summarize_caller_timing((), caller_call_ref="  ")

    assert summary["caller_call_ref"] == ""
    assert summary["caller_timing_evidence"] == "not_evaluated"
    assert summary["caller_t_ecd_seconds"] is None
    assert summary["caller_t_dba_seconds"] is None
