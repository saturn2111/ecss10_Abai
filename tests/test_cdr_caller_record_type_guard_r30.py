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


@pytest.mark.parametrize("bad_record", [None, object(), {"conn_id": "caller-ref"}, "caller-ref"])
def test_caller_timing_requires_exact_cdr_record_values(bad_record) -> None:
    with pytest.raises(TypeError, match="exact CdrRecord"):
        summarize_caller_timing((_record(), bad_record), caller_call_ref="caller-ref")


def test_exact_cdr_record_is_preserved() -> None:
    summary = summarize_caller_timing((_record(),), caller_call_ref="caller-ref")

    assert summary["caller_timing_evidence"] == "single_complete_caller_timing_record"
    assert summary["caller_t_ecd_seconds"] == 12
    assert summary["caller_t_dba_seconds"] == 3
