from __future__ import annotations

import tempfile
from pathlib import Path
import unittest

from tools.cdr_queue_analyzer import analyze_queue_call, load_cdr


class CdrQueueAnalyzerTests(unittest.TestCase):
    def _write(self, text: str) -> Path:
        handle = tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", suffix=".csv", delete=False)
        with handle:
            handle.write(text)
        return Path(handle.name)

    def test_loads_semicolon_cdr_and_preserves_required_metrics(self) -> None:
        path = self._write("CONN_ID;T_ECD;T_DBA;RESULT\ncaller-ref;0;0;answered\noperator-ref;42;5;normalClearing\n")
        try:
            records = load_cdr(path)
        finally:
            path.unlink(missing_ok=True)
        self.assertEqual(len(records), 2)
        self.assertEqual(records[1].conversation_seconds, 42)
        self.assertEqual(records[1].answer_delay_seconds, 5)

    def test_selects_single_positive_operator_record_for_duration(self) -> None:
        path = self._write("CONN_ID,T_ECD,T_DBA\ncaller-ref,0,0\noperator-ref,0,5\noperator-ref,38,5\n")
        try:
            result = analyze_queue_call(load_cdr(path), caller_call_ref="caller-ref", operator_call_ref="operator-ref")
        finally:
            path.unlink(missing_ok=True)
        self.assertEqual(result["duration_seconds"], 38)
        self.assertEqual(result["selection_reason"], "single_positive_t_ecd_operator_record")
        self.assertTrue(result["operator_duration_confirmed"])

    def test_multiple_positive_operator_records_are_ambiguous(self) -> None:
        path = self._write("CONN_ID,T_ECD,T_DBA\ncaller-ref,0,0\noperator-ref,38,5\noperator-ref,51,5\n")
        try:
            result = analyze_queue_call(load_cdr(path), caller_call_ref="caller-ref", operator_call_ref="operator-ref")
        finally:
            path.unlink(missing_ok=True)
        self.assertEqual(result["selection_reason"], "ambiguous_multiple_positive_operator_records")
        self.assertIsNone(result["selected_operator_conn_id"])
        self.assertIsNone(result["duration_seconds"])
        self.assertFalse(result["operator_duration_confirmed"])

    def test_multiple_zero_operator_records_are_ambiguous(self) -> None:
        path = self._write("CONN_ID,T_ECD,T_DBA\ncaller-ref,0,0\noperator-ref,0,5\noperator-ref,0,6\n")
        try:
            result = analyze_queue_call(load_cdr(path), caller_call_ref="caller-ref", operator_call_ref="operator-ref")
        finally:
            path.unlink(missing_ok=True)
        self.assertEqual(result["selection_reason"], "ambiguous_multiple_operator_records")
        self.assertFalse(result["operator_duration_confirmed"])

    def test_does_not_guess_when_operator_ref_is_missing(self) -> None:
        path = self._write("CONN_ID,T_ECD,T_DBA\ncaller-ref,0,0\nother-ref,50,3\n")
        try:
            result = analyze_queue_call(load_cdr(path), caller_call_ref="caller-ref", operator_call_ref="operator-ref")
        finally:
            path.unlink(missing_ok=True)
        self.assertIsNone(result["duration_seconds"])
        self.assertEqual(result["selection_reason"], "no_operator_record")
        self.assertFalse(result["operator_duration_confirmed"])

    def test_same_call_ref_is_rejected_as_ambiguous(self) -> None:
        path = self._write("CONN_ID,T_ECD,T_DBA\nsame-ref,51,4\n")
        try:
            result = analyze_queue_call(load_cdr(path), caller_call_ref=" same-ref ", operator_call_ref="same-ref")
        finally:
            path.unlink(missing_ok=True)
        self.assertEqual(result["selection_reason"], "ambiguous_same_call_ref")
        self.assertIsNone(result["duration_seconds"])
        self.assertFalse(result["operator_duration_confirmed"])

    def test_blank_call_ref_is_rejected(self) -> None:
        result = analyze_queue_call((), caller_call_ref=" ", operator_call_ref="operator-ref")
        self.assertEqual(result["selection_reason"], "missing_call_ref")
        self.assertFalse(result["operator_duration_confirmed"])

    def test_missing_required_column_fails_closed(self) -> None:
        path = self._write("CONN_ID,T_ECD\nref,10\n")
        try:
            with self.assertRaisesRegex(ValueError, "T_DBA"):
                load_cdr(path)
        finally:
            path.unlink(missing_ok=True)

    def test_duplicate_required_column_fails_closed(self) -> None:
        path = self._write("CONN_ID,T_ECD,T_ECD,T_DBA\nref,10,999,2\n")
        try:
            with self.assertRaisesRegex(ValueError, "duplicate required columns: T_ECD"):
                load_cdr(path)
        finally:
            path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
