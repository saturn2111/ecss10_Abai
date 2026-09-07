from tools.cdr_evidence_bundle import BUNDLE_SCHEMA, BUNDLE_WARNING
from tools.cdr_evidence_html_report import HTML_SCHEMA, build_html_report
from tools.cdr_timing_report import SEMANTIC_WARNING


def _bundle() -> dict[str, object]:
    return {
        "schema": BUNDLE_SCHEMA,
        "warning": BUNDLE_WARNING,
        "items": [
            {
                "label": "queue-call-A",
                "report": {
                    "caller_ref": "caller-ref-A",
                    "records": 1,
                    "complete": 1,
                    "incomplete": 0,
                    "evidence": "unique_complete",
                    "raw_t_ecd_seconds": 14,
                    "raw_t_dba_seconds": 5,
                    "warning": SEMANTIC_WARNING,
                },
            },
            {
                "label": "ambiguous-B",
                "report": {
                    "caller_ref": "caller-ref-B",
                    "records": 2,
                    "complete": 1,
                    "incomplete": 1,
                    "evidence": "competing_incomplete",
                    "raw_t_ecd_seconds": None,
                    "raw_t_dba_seconds": None,
                    "warning": SEMANTIC_WARNING,
                },
            },
        ],
    }


def test_html_report_is_human_readable_and_keeps_raw_semantics() -> None:
    rendered = build_html_report(_bundle())

    assert "ECSS CDR Evidence Report" in rendered
    assert HTML_SCHEMA in rendered
    assert "queue-call-A" in rendered
    assert "caller-ref-A" in rendered
    assert "unique_complete" in rendered
    assert "competing_incomplete" in rendered
    assert "Raw T_ECD (s)" in rendered
    assert "Raw T_DBA (s)" in rendered
    assert "n/a" in rendered
    assert "queue wait" in rendered.lower()
    assert "not labelled as queue wait or final call duration" in rendered


def test_html_report_escapes_labels_and_refs() -> None:
    payload = _bundle()
    item = payload["items"][0]  # type: ignore[index]
    item["label"] = "<script>alert(1)</script>"  # type: ignore[index]
    item["report"]["caller_ref"] = "<b>ref</b>"  # type: ignore[index]

    rendered = build_html_report(payload)

    assert "<script>alert(1)</script>" not in rendered
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in rendered
    assert "<b>ref</b>" not in rendered
    assert "&lt;b&gt;ref&lt;/b&gt;" in rendered


def test_html_report_rejects_inconsistent_cardinality() -> None:
    payload = _bundle()
    payload["items"][0]["report"]["records"] = 2  # type: ignore[index]

    try:
        build_html_report(payload)
    except ValueError as exc:
        assert "cardinality" in str(exc)
    else:
        raise AssertionError("inconsistent evidence must fail closed")
