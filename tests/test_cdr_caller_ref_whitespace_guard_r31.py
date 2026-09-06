import unittest

from tools.cdr_caller_timing_evidence import summarize_caller_timing
from tools.cdr_queue_analyzer import CdrRecord


def _record(conn_id: str = "caller-ref") -> CdrRecord:
    return CdrRecord(
        conn_id=conn_id,
        conversation_seconds=12,
        answer_delay_seconds=3,
        raw={"CONN_ID": conn_id, "T_ECD": "12", "T_DBA": "3"},
    )


class CallerRefWhitespaceGuardTests(unittest.TestCase):
    def test_padded_nonblank_caller_ref_fails_closed(self) -> None:
        for caller_ref in (" caller-ref", "caller-ref ", "\tcaller-ref\n"):
            with self.subTest(caller_ref=caller_ref):
                with self.assertRaisesRegex(ValueError, "surrounding whitespace"):
                    summarize_caller_timing((_record(),), caller_call_ref=caller_ref)

    def test_whitespace_only_ref_remains_not_evaluated(self) -> None:
        summary = summarize_caller_timing((_record(),), caller_call_ref="   ")

        self.assertEqual(summary["caller_call_ref"], "")
        self.assertEqual(summary["caller_record_count"], 0)
        self.assertEqual(summary["caller_timing_evidence"], "not_evaluated")
        self.assertIsNone(summary["caller_t_ecd_seconds"])
        self.assertIsNone(summary["caller_t_dba_seconds"])

    def test_exact_nonblank_ref_is_preserved(self) -> None:
        summary = summarize_caller_timing((_record(),), caller_call_ref="caller-ref")

        self.assertEqual(summary["caller_call_ref"], "caller-ref")
        self.assertEqual(
            summary["caller_timing_evidence"], "single_complete_caller_timing_record"
        )


if __name__ == "__main__":
    unittest.main()
