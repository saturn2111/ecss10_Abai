from __future__ import annotations

import tempfile
from pathlib import Path
import unittest

from tools.cdr_queue_analyzer import analyze_queue_call, load_cdr


class FractionalCdrMetricTests(unittest.TestCase):
    def _write(self, text: str) -> Path:
        handle = tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", suffix=".csv", delete=False)
        with handle:
            handle.write(text)
        return Path(handle.name)

    def test_fractional_duration_is_not_truncated_or_confirmed(self) -> None:
        path = self._write("CONN_ID,T_ECD,T_DBA\ncaller-ref,0,0\noperator-ref,12.5,3\n")
        try:
            records = load_cdr(path)
            result = analyze_queue_call(
                records,
                caller_call_ref="caller-ref",
                operator_call_ref="operator-ref",
            )
        finally:
            path.unlink(missing_ok=True)

        self.assertIsNone(records[1].conversation_seconds)
        self.assertIsNone(result["duration_seconds"])
        self.assertEqual(result["selection_reason"], "invalid_operator_t_ecd")
        self.assertFalse(result["operator_duration_confirmed"])

    def test_fractional_answer_delay_is_not_truncated(self) -> None:
        path = self._write("CONN_ID,T_ECD,T_DBA\ncaller-ref,0,0\noperator-ref,12,3.75\n")
        try:
            records = load_cdr(path)
            result = analyze_queue_call(
                records,
                caller_call_ref="caller-ref",
                operator_call_ref="operator-ref",
            )
        finally:
            path.unlink(missing_ok=True)

        self.assertEqual(result["duration_seconds"], 12)
        self.assertIsNone(result["answer_delay_seconds"])
        self.assertFalse(result["selected_operator_has_complete_timing"])
        self.assertTrue(result["operator_duration_confirmed"])

    def test_integral_decimal_representation_remains_accepted(self) -> None:
        path = self._write("CONN_ID,T_ECD,T_DBA\ncaller-ref,0,0\noperator-ref,12.0,3.0\n")
        try:
            records = load_cdr(path)
        finally:
            path.unlink(missing_ok=True)

        self.assertEqual(records[1].conversation_seconds, 12)
        self.assertEqual(records[1].answer_delay_seconds, 3)


if __name__ == "__main__":
    unittest.main()
