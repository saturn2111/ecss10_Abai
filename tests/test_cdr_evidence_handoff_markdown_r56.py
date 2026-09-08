from pathlib import Path

from tools.cdr_evidence_bundle import BUNDLE_SCHEMA, BUNDLE_WARNING
from tools.cdr_evidence_handoff_report import build_handoff_report


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


def test_handoff_report_adds_local_visible_markdown_export() -> None:
    rendered = build_handoff_report(_bundle())
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
