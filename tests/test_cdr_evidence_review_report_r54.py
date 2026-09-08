from tools.cdr_evidence_bundle import BUNDLE_SCHEMA, BUNDLE_WARNING
from tools.cdr_evidence_review_report import REVIEW_SCHEMA, build_review_report


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
            },
            {
                "label": "call-b",
                "report": {
                    "warning": warning,
                    "caller_ref": "ref-b",
                    "evidence": "incomplete-or-competing-caller-evidence",
                    "records": 2,
                    "complete": 0,
                    "incomplete": 2,
                    "raw_t_ecd_seconds": None,
                    "raw_t_dba_seconds": None,
                },
            },
        ],
    }


def test_review_report_adds_session_only_bookmarks_without_changing_timing_semantics() -> None:
    rendered = build_review_report(_bundle())

    assert REVIEW_SCHEMA in rendered
    assert "bookmarks are session-only and never sent to ECSS" in rendered
    assert "Bookmarked only" in rendered
    assert "Bookmark visible" in rendered
    assert "Clear bookmarks" in rendered
    assert "Bookmark evidence row" in rendered
    assert "row.dataset.bookmarked" in rendered
    assert "if (!baseVisible(row)) continue;" in rendered
    assert "bookmarkVisibleButton.disabled = visible.length === 0" in rendered
    assert "refreshVisibleSummary(visible)" in rendered
    assert "queue wait" in rendered
    assert "final call duration" in rendered
    assert "localStorage" not in rendered
    assert "fetch(" not in rendered
