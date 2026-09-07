from tools.cdr_evidence_bundle import BUNDLE_SCHEMA, BUNDLE_WARNING
from tools.cdr_evidence_bundle_report import render_bundle_table


def _payload():
    return {
        "schema": BUNDLE_SCHEMA,
        "warning": BUNDLE_WARNING,
        "items": [
            {
                "label": "capture-a",
                "report": {
                    "caller_ref": "ref-a",
                    "records": 1,
                    "complete": 1,
                    "incomplete": 0,
                    "evidence": "unique_complete",
                    "raw_t_ecd_seconds": 12,
                    "raw_t_dba_seconds": 3,
                },
            },
            {
                "label": "capture-b",
                "report": {
                    "caller_ref": "ref-b",
                    "records": 2,
                    "complete": 1,
                    "incomplete": 1,
                    "evidence": "competing",
                    "raw_t_ecd_seconds": None,
                    "raw_t_dba_seconds": None,
                },
            },
        ],
    }


def test_render_bundle_table_is_deterministic_and_preserves_order():
    rendered = render_bundle_table(_payload())
    lines = rendered.splitlines()
    assert lines[1].startswith("capture-a\tref-a\t1\t1\t0\tunique_complete\t12\t3")
    assert lines[2].startswith("capture-b\tref-b\t2\t1\t1\tcompeting\tn/a\tn/a")
    assert lines[-1] == f"warning\t{BUNDLE_WARNING}"


def test_render_bundle_table_does_not_invent_ambiguous_timing():
    rendered = render_bundle_table(_payload())
    assert "capture-b\tref-b\t2\t1\t1\tcompeting\tn/a\tn/a" in rendered


def test_render_bundle_table_rejects_unknown_schema():
    payload = _payload()
    payload["schema"] = "future-schema"
    try:
        render_bundle_table(payload)
    except ValueError as exc:
        assert "unsupported evidence bundle schema" in str(exc)
    else:
        raise AssertionError("unknown schema must fail closed")
