from tools.cdr_evidence_bundle import BUNDLE_SCHEMA, BUNDLE_WARNING
from tools.cdr_evidence_html_report import HTML_SCHEMA, build_html_report


def _bundle():
    report_warning = BUNDLE_WARNING.replace("evidence-only bundle; ", "raw timing fields only; ")
    return {
        "schema": BUNDLE_SCHEMA,
        "warning": BUNDLE_WARNING,
        "items": [
            {
                "label": "capture-a",
                "report": {
                    "warning": report_warning,
                    "caller_ref": "ref-1",
                    "evidence": "unique-complete",
                    "records": 1,
                    "complete": 1,
                    "incomplete": 0,
                    "raw_t_ecd_seconds": 1.25,
                    "raw_t_dba_seconds": 2.5,
                },
            }
        ],
    }


def test_html_report_exports_only_visible_rows_and_keeps_semantic_boundary():
    rendered = build_html_report(_bundle())

    assert HTML_SCHEMA == "ecss-cdr-evidence-html-report-v3"
    assert "Export visible CSV" in rendered
    assert "rows.filter((row) => !row.hidden)" in rendered
    assert "ecss-cdr-visible-evidence.csv" in rendered
    assert "Raw T_ECD/T_DBA values" in rendered
    assert "queue wait" in rendered


def test_csv_export_hardens_spreadsheet_formula_prefixes():
    rendered = build_html_report(_bundle())

    assert "/^[=+\\-@]/" in rendered
    assert "safe = \"'\" + safe" in rendered
