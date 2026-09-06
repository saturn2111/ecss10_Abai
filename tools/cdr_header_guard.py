from __future__ import annotations

from collections.abc import Iterable


def validate_cdr_header(fieldnames: Iterable[object] | None) -> tuple[str, ...]:
    """Normalize and validate an offline CDR header without inferring call semantics.

    The helper accepts only an exact list/tuple of exact strings, trims outer
    whitespace, and rejects blank or duplicate normalized column names. It is a
    deterministic input-shape guard only; it does not correlate calls or infer
    queue wait, logical call identity, or finished-event duration.
    """

    if type(fieldnames) not in {list, tuple}:
        raise ValueError("CDR fieldnames must be an exact list or tuple")

    normalized: list[str] = []
    seen: set[str] = set()
    for value in fieldnames:
        if type(value) is not str:
            raise ValueError("CDR column names must be exact strings")
        name = value.strip()
        if not name:
            raise ValueError("CDR header contains a blank column name")
        if name in seen:
            raise ValueError(f"CDR header contains duplicate column: {name}")
        seen.add(name)
        normalized.append(name)

    if not normalized:
        raise ValueError("CDR header is empty")
    return tuple(normalized)
