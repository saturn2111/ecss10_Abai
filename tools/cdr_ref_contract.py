from __future__ import annotations


def normalize_cdr_call_ref(value: object) -> str | None:
    """Return a bounded exact-string call_ref or None without coercing arbitrary objects.

    This helper is evidence-only. It does not infer a logical queue-call identity or
    relate caller/operator legs; it only normalizes a captured ref supplied by the
    operator or conversations_event evidence.
    """

    if type(value) is not str:
        return None
    normalized = value.strip()
    if not normalized or len(normalized) > 512:
        return None
    if any(ord(ch) < 32 or ord(ch) == 127 for ch in normalized):
        return None
    return normalized
