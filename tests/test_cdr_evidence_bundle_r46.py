import json

import pytest

from tools.cdr_evidence_bundle import (
    BUNDLE_SCHEMA,
    BUNDLE_WARNING,
    build_evidence_bundle_json,
    build_evidence_bundle_payload,
)


def _report(ref: str, *, evidence: str, t_ecd: int | None, t_dba: int | None) -> dict[str, object]:
    return {
        "caller_ref": ref,
        "records": 1,
        "complete": 1 if t_ecd is not None and t_dba is not None else 0,
        "incomplete": 0 if t_ecd is not None and t_dba is not None else 1,
        "evidence": evidence,
        "raw_t_ecd_seconds": t_ecd,
        "raw_t_dba_seconds": t_dba,
        "warning": "raw timing fields only",
    }


def test_bundle_preserves_item_order_and_evidence_only_payloads() -> None:
    first = _report("caller-a", evidence="unique_complete", t_ecd=12, t_dba=3)
    second = _report("caller-b", evidence="ambiguous", t_ecd=None, t_dba=None)

    payload = build_evidence_bundle_payload((("first", first), ("second", second)))

    assert payload["schema"] == BUNDLE_SCHEMA
    assert payload["warning"] == BUNDLE_WARNING
    assert payload["items"] == [
        {"label": "first", "report": first},
        {"label": "second", "report": second},
    ]


def test_bundle_json_is_deterministic_and_keeps_ambiguous_timing_null() -> None:
    ambiguous = _report("caller-b", evidence="ambiguous", t_ecd=None, t_dba=None)

    rendered = build_evidence_bundle_json((("ambiguous", ambiguous),))
    decoded = json.loads(rendered)

    assert rendered == build_evidence_bundle_json((("ambiguous", ambiguous),))
    assert decoded["items"][0]["report"]["raw_t_ecd_seconds"] is None
    assert decoded["items"][0]["report"]["raw_t_dba_seconds"] is None
    assert "final duration" in decoded["warning"]


def test_bundle_rejects_duplicate_labels() -> None:
    report = _report("caller-a", evidence="unique_complete", t_ecd=12, t_dba=3)

    with pytest.raises(ValueError, match="duplicate bundle label"):
        build_evidence_bundle_payload((("same", report), ("same", report)))
