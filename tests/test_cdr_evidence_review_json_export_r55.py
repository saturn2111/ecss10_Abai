from tools.cdr_evidence_review_report import VISIBLE_JSON_SCHEMA, build_review_report
from tests.test_cdr_evidence_review_report_r54 import _bundle


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
