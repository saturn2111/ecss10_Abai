from __future__ import annotations

import json
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


def _build_report_payload(
    records: Iterable[CdrRecord],
    *,
    caller_call_ref: str,
) -> dict[str, object]:
    summary = summarize_caller_timing(records, caller_call_ref=caller_call_ref)
    return {
        "caller_ref": summary["caller_call_ref"],
        "records": summary["caller_record_count"],
        "complete": summary["caller_complete_timing_record_count"],
        "incomplete": summary["caller_incomplete_timing_record_count"],
        "evidence": summary["caller_timing_evidence"],
        "raw_t_ecd_seconds": summary["caller_t_ecd_seconds"],
        "raw_t_dba_seconds": summary["caller_t_dba_seconds"],
        "warning": SEMANTIC_WARNING,
    }


def build_caller_timing_report(
    records: Iterable[CdrRecord],
    *,
    caller_call_ref: str,
) -> str:
    """Render an evidence-only offline report for one exact caller call reference.

    Raw T_ECD/T_DBA values are exposed only when the exact reference resolves to
    one complete, uncontested row. No queue or final call-duration meaning is
    inferred from those fields.
    """

    payload = _build_report_payload(records, caller_call_ref=caller_call_ref)
    lines = (
        f"caller_ref={payload['caller_ref']}",
        f"records={payload['records']}",
        f"complete={payload['complete']}",
        f"incomplete={payload['incomplete']}",
        f"evidence={payload['evidence']}",
        f"raw_t_ecd_seconds={_render_raw_seconds(payload['raw_t_ecd_seconds'])}",
        f"raw_t_dba_seconds={_render_raw_seconds(payload['raw_t_dba_seconds'])}",
        f"warning={payload['warning']}",
    )
    return "\n".join(lines)


def build_caller_timing_report_json(
    records: Iterable[CdrRecord],
    *,
    caller_call_ref: str,
) -> str:
    """Return a deterministic evidence-only JSON artifact for offline analysis.

    Ambiguous or incomplete timing remains JSON ``null`` because the underlying
    verified summary fails closed. The artifact deliberately carries the same
    semantic warning as the human-readable report.
    """

    payload = _build_report_payload(records, caller_call_ref=caller_call_ref)
    return json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
