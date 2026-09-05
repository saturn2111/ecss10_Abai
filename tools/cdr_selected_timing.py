from __future__ import annotations

from .cdr_queue_analyzer import CdrRecord


def selected_operator_timing_values(
    record: CdrRecord | None,
) -> tuple[int, int] | None:
    """Expose timing only when the already-selected exact operator row is complete.

    The tuple is ``(T_ECD, T_DBA)``. Zero is valid evidence. This helper never
    selects a CDR row, infers queue wait time, or constructs a logical call id.
    """

    if record is None:
        return None
    if record.conversation_seconds is None or record.answer_delay_seconds is None:
        return None
    return (record.conversation_seconds, record.answer_delay_seconds)
