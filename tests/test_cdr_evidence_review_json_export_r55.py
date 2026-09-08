from tools.cdr_evidence_bundle import BUNDLE_SCHEMA, BUNDLE_WARNING
from tools.cdr_evidence_review_report import VISIBLE_JSON_SCHEMA, build_review_report


def _bundle() -> dict[str, object]:
    warning = BUNDLE_WARNING.replace("evidence-only bundle; ", "raw timing fields only; ")
    return {
        "schema": BUNDLE_SCHEMA,
        "warning": BUNDLE_WARNING,
        "items": [
            {
                "label": "call-a",
                "report": {
                    "warning": warning,
                    "caller_ref": "ref-a",
                    "evidence": "unique-complete-caller-row",
                    "records": 1,
                    "complete": 1,
                    "incomplete": 0,
                    "raw_t_ecd_seconds": 10,
                    "raw_t_dba_seconds": 20,
                },
            }
        ],
    }


def test_review_report_exports_only_visible_rows_as_local_evidence_json() -> None:
    rendered = build_review_report(_bundle())
    assert VISIBLE_JSON_SCHEMA in rendered
    assert "Export visible JSON" in rendered
    assert "review-export-json" in rendered
    assert "visibleRows()" in rendered
    assert "Array.from(row.cells).slice(0, -1)" in rendered
    assert "classification: row.dataset.classification" in rendered
    assert "bookmarked: row.dataset.bookmarked === '1'" in rendered
    assert "evidence_semantics: 'raw-visible-values-only'" in rendered
    assert "ecss-cdr-visible-evidence.json" in rendered
    assert "URL.revokeObjectURL(url)" in rendered
    assert "fetch(" not in rendered
    assert "localStorage" not in rendered
    assert "queue_wait" not in rendered
    assert "final_duration" not in rendered
