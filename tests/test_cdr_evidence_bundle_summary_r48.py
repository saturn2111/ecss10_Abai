import json

import pytest

from tools.cdr_evidence_bundle import BUNDLE_SCHEMA, BUNDLE_WARNING
from tools.cdr_evidence_bundle_summary import build_summary_json, summarize_bundle


def _payload():
    return {
        "schema": BUNDLE_SCHEMA,
        "warning": BUNDLE_WARNING,
        "items": [
            {"label": "a", "report": {"records": 1, "complete": 1, "incomplete": 0, "evidence": "unique_complete"}},
            {"label": "b", "report": {"records": 2, "complete": 1, "incomplete": 1, "evidence": "competing"}},
            {"label": "c", "report": {"records": 0, "complete": 0, "incomplete": 0, "evidence": "none"}},
        ],
    }


def test_summary_counts_evidence_and_cardinality_deterministically():
    summary = json.loads(build_summary_json(_payload()))
    assert summary["items"] == 3
    assert summary["records"] == 3
    assert summary["complete"] == 2
    assert summary["incomplete"] == 1
    assert summary["evidence_counts"] == {"competing": 1, "none": 1, "unique_complete": 1}
    assert summary["warning"] == BUNDLE_WARNING


def test_summary_rejects_inconsistent_cardinality():
    payload = _payload()
    payload["items"][0]["report"]["records"] = 2
    with pytest.raises(ValueError, match="cardinality"):
        summarize_bundle(payload)


def test_summary_rejects_unknown_schema_and_warning():
    payload = _payload()
    payload["schema"] = "future"
    with pytest.raises(ValueError, match="schema"):
        summarize_bundle(payload)

    payload = _payload()
    payload["warning"] = "semantic guess allowed"
    with pytest.raises(ValueError, match="warning"):
        summarize_bundle(payload)
