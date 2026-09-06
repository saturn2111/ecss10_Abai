import pytest

from tools.cdr_caller_timing_evidence import summarize_caller_timing
from tools.cdr_queue_analyzer import CdrRecord


def _record(conn_id: str = "caller-ref") -> CdrRecord:
    return CdrRecord(
        conn_id=conn_id,
        conversation_seconds=12,
        answer_delay_seconds=3,
        raw={"CONN_ID": conn_id, "T_ECD": "12", "T_DBA": "3"},
    )


@pytest.mark.parametrize("caller_ref", [" caller-ref", "caller-ref ", "\tcaller-ref\n"])
def test_padded_nonblank_caller_ref_fails_closed(caller_ref: str) -> None:
    with pytest.raises(ValueError, match="surrounding whitespace"):
        summarize_caller_timing((_record(),), caller_call_ref=caller_ref)


def test_whitespace_only_ref_remains_not_evaluated() -> None:
    summary = summarize_caller_timing((_record(),), caller_call_ref="   ")

    assert summary["caller_call_ref"] == ""
    assert summary["caller_record_count"] == 0
    assert summary["caller_timing_evidence"] == "not_evaluated"
    assert summary["caller_t_ecd_seconds"] is None
    assert summary["caller_t_dba_seconds"] is None


def test_exact_nonblank_ref_is_preserved() -> None:
    summary = summarize_caller_timing((_record(),), caller_call_ref="caller-ref")

    assert summary["caller_call_ref"] == "caller-ref"
    assert summary["caller_timing_evidence"] == "single_complete_caller_timing_record"
