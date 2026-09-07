from tools.cdr_evidence_bundle import BUNDLE_SCHEMA, BUNDLE_WARNING
from tools.cdr_evidence_visible_summary_report import build_visible_summary_report


def _payload() -> dict[str, object]:
    report_warning = BUNDLE_WARNING.replace("evidence-only bundle; ", "raw timing fields only; ")
    return {
        "schema": BUNDLE_SCHEMA,
        "warning": BUNDLE_WARNING,
        "items": [
            {
                "label": "call-a",
                "report": {
                    "warning": report_warning,
                    "caller_ref": "caller-a",
                    "evidence": "single_complete_timing_record",
                    "records": 1,
                    "complete": 1,
                    "incomplete": 0,
                    "raw_t_ecd_seconds": 42,
                    "raw_t_dba_seconds": 5,
                },
            },
            {
                "label": "call-b",
                "report": {
                    "warning": report_warning,
                    "caller_ref": "caller-b",
                    "evidence": "single_incomplete_timing_record",
                    "records": 2,
                    "complete": 0,
                    "incomplete": 2,
                    "raw_t_ecd_seconds": None,
                    "raw_t_dba_seconds": None,
                },
            },
        ],
    }


def test_visible_summary_is_wired_to_existing_filters() -> None:
    rendered = build_visible_summary_report(_payload())

    assert "ecss-cdr-evidence-visible-summary-v1" in rendered
    assert 'id="visible-summary-items"' in rendered
    assert 'id="visible-summary-records"' in rendered
    assert "rows.filter((row) => !row.hidden)" in rendered
    assert "records += toCount(row.cells[2])" in rendered
    assert "complete += toCount(row.cells[3])" in rendered
    assert "incomplete += toCount(row.cells[4])" in rendered
    assert "classification?.addEventListener('change'" in rendered
    assert "search?.addEventListener('input'" in rendered
    assert "queue wait" in rendered.lower()
    assert "final call duration" in rendered.lower()
