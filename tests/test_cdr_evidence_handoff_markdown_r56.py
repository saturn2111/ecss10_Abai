from pathlib import Path

from tools.cdr_evidence_handoff_report import build_handoff_report


def _payload() -> dict[str, object]:
    return {
        "schema": "ecss-cdr-evidence-bundle-v1",
        "items": [
            {
                "source": "sanitized.tsv",
                "caller_ref": "caller-a",
                "classification": "complete_unique_caller_row",
                "records": 1,
                "complete_records": 1,
                "incomplete_records": 0,
                "evidence": {"CONN_ID": "caller-a", "T_ECD": "123", "T_DBA": "45"},
            }
        ],
    }


def test_handoff_report_adds_local_visible_markdown_export() -> None:
    rendered = build_handoff_report(_payload())
    assert 'id="review-export-markdown"' in rendered
    assert "Export visible Markdown" in rendered
    assert "# ECSS CDR Evidence Review" in rendered
    assert "Raw visible evidence only. T_ECD/T_DBA are not labeled as queue wait or final Duration." in rendered
    assert "rows.filter((row) => !row.hidden)" in rendered
    assert "slice(0, -1)" in rendered
    assert "row.dataset.bookmarked === '1'" in rendered
    assert "ecss-cdr-visible-evidence.md" in rendered
    assert "text/markdown;charset=utf-8" in rendered
    assert "URL.createObjectURL(blob)" in rendered
    assert "URL.revokeObjectURL(url)" in rendered
    lowered = rendered.lower()
    assert "localstorage" not in lowered
    assert "fetch(" not in lowered


def test_handoff_module_is_offline_only() -> None:
    source = (Path(__file__).resolve().parents[1] / "tools/cdr_evidence_handoff_report.py").read_text(encoding="utf-8")
    lowered = source.lower()
    assert "requests." not in lowered
    assert "http://" not in lowered
    assert "https://" not in lowered
