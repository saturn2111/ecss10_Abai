from __future__ import annotations

from tools.cdr_queue_analyzer import CdrRecord


def selected_operator_missing_timing_fields(record: CdrRecord | None) -> tuple[str, ...]:
    """Return missing raw timing fields for an already-selected exact operator row.

    This helper is descriptive only. It never selects a record, correlates call legs,
    infers queue membership, or reinterprets T_DBA as queue-wait time.
    """

    if record is None:
        return ()

    missing: list[str] = []
    if record.conversation_seconds is None:
        missing.append("T_ECD")
    if record.answer_delay_seconds is None:
        missing.append("T_DBA")
    return tuple(missing)
