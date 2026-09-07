from __future__ import annotations

from collections.abc import Iterable

from tools.cdr_caller_timing_evidence import summarize_caller_timing
from tools.cdr_queue_analyzer import CdrRecord


SEMANTIC_WARNING = (
    "raw timing fields only; queue membership, queue wait, logical call identity "
    "and final duration are not inferred"
)


def _render_raw_seconds(value: object) -> str:
    if value is None:
        return "n/a"
    if type(value) not in (int, float):
        raise TypeError("timing values must be exact int/float or None")
    return str(value)


def build_caller_timing_report(
    records: Iterable[CdrRecord],
    *,
    caller_call_ref: str,
) -> str:
    """Render an evidence-only offline report for one exact caller call reference.

    The report intentionally preserves the narrow semantics of
    ``summarize_caller_timing``. Raw T_ECD/T_DBA values are exposed only when the
    exact reference resolves to one complete, uncontested row. No queue or final
    call-duration meaning is inferred from those fields.
    """

    summary = summarize_caller_timing(records, caller_call_ref=caller_call_ref)
    lines = (
        f"caller_ref={summary['caller_call_ref']}",
        f"records={summary['caller_record_count']}",
        f"complete={summary['caller_complete_timing_record_count']}",
        f"incomplete={summary['caller_incomplete_timing_record_count']}",
        f"evidence={summary['caller_timing_evidence']}",
        f"raw_t_ecd_seconds={_render_raw_seconds(summary['caller_t_ecd_seconds'])}",
        f"raw_t_dba_seconds={_render_raw_seconds(summary['caller_t_dba_seconds'])}",
        f"warning={SEMANTIC_WARNING}",
    )
    return "\n".join(lines)
