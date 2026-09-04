from __future__ import annotations

import tempfile
from pathlib import Path
import unittest

from tools.cdr_queue_analyzer import analyze_queue_call, load_cdr


class NegativeCdrMetricTests(unittest.TestCase):
    def _write(self, text: str) -> Path:
        handle = tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", suffix=".csv", delete=False)
        with handle:
            handle.write(text)
        return Path(handle.name)

    def test_negative_duration_is_not_confirmed(self) -> None:
        path = self._write("CONN_ID,T_ECD,T_DBA\ncaller-ref,0,0\noperator-ref,-7,3\n")
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
        self.assertFalse(result["operator_duration_confirmed"])

    def test_negative_answer_delay_is_not_exposed(self) -> None:
        path = self._write("CONN_ID,T_ECD,T_DBA\ncaller-ref,0,0\noperator-ref,12,-4\n")
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
        self.assertTrue(result["operator_duration_confirmed"])


if __name__ == "__main__":
    unittest.main()
