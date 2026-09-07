from __future__ import annotations

import json
from pathlib import Path

from tools.cdr_timing_cli import run


def _write_cdr(path: Path, rows: str) -> None:
    path.write_text("CONN_ID,T_ECD,T_DBA\n" + rows, encoding="utf-8")


def test_text_cli_renders_exact_ref_without_semantic_guess(tmp_path: Path, capsys) -> None:
    cdr = tmp_path / "sanitized.csv"
    _write_cdr(cdr, "caller-ref,12,3\nother-ref,50,8\n")

    assert run((str(cdr), "--caller-ref", "caller-ref")) == 0
    output = capsys.readouterr().out

    assert "caller_ref=caller-ref" in output
    assert "raw_t_ecd_seconds=12" in output
    assert "raw_t_dba_seconds=3" in output
    assert "queue wait" in output
    assert "not inferred" in output


def test_json_cli_keeps_ambiguous_timing_null(tmp_path: Path, capsys) -> None:
    cdr = tmp_path / "sanitized.csv"
    _write_cdr(cdr, "caller-ref,12,3\ncaller-ref,13,4\n")

    assert run((str(cdr), "--caller-ref", "caller-ref", "--format", "json")) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["caller_ref"] == "caller-ref"
    assert payload["records"] == 2
    assert payload["raw_t_ecd_seconds"] is None
    assert payload["raw_t_dba_seconds"] is None


def test_cli_fails_closed_for_missing_cdr(tmp_path: Path, capsys) -> None:
    missing = tmp_path / "missing.csv"

    assert run((str(missing), "--caller-ref", "caller-ref")) == 2
    assert "cdr_timing_cli:" in capsys.readouterr().err
