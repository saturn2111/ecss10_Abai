import unittest

from tools.cdr_caller_timing_evidence import (
    caller_timing_evidence,
    summarize_caller_timing,
)
from tools.cdr_queue_analyzer import CdrRecord


class CallerTimingEvidenceTests(unittest.TestCase):
    def test_classification_states(self) -> None:
        self.assertEqual(caller_timing_evidence(0, 0), "no_caller_timing_evidence")
        self.assertEqual(
            caller_timing_evidence(1, 0), "single_complete_caller_timing_record"
        )
        self.assertEqual(
            caller_timing_evidence(2, 0), "multiple_complete_caller_timing_records"
        )
        self.assertEqual(
            caller_timing_evidence(0, 1), "single_incomplete_caller_timing_record"
        )
        self.assertEqual(
            caller_timing_evidence(0, 2), "no_complete_caller_timing_records"
        )
        self.assertEqual(
            caller_timing_evidence(1, 1),
            "mixed_complete_and_incomplete_caller_timing_records",
        )

    def test_counts_fail_closed_on_invalid_types_or_values(self) -> None:
        with self.assertRaises(TypeError):
            caller_timing_evidence(True, 0)
        with self.assertRaises(TypeError):
            caller_timing_evidence(0, 1.0)  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            caller_timing_evidence(-1, 0)

    def test_summary_uses_exact_caller_ref_only(self) -> None:
        rows = (
            CdrRecord("caller-a", 15, 4, {}),
            CdrRecord("caller-a", None, 0, {}),
            CdrRecord("operator-b", 12, 2, {}),
        )

        result = summarize_caller_timing(rows, caller_call_ref=" caller-a ")

        self.assertEqual(result["caller_call_ref"], "caller-a")
        self.assertEqual(result["caller_record_count"], 2)
        self.assertEqual(result["caller_complete_timing_record_count"], 1)
        self.assertEqual(result["caller_incomplete_timing_record_count"], 1)
        self.assertEqual(
            result["caller_timing_evidence"],
            "mixed_complete_and_incomplete_caller_timing_records",
        )

    def test_blank_ref_is_not_evaluated(self) -> None:
        result = summarize_caller_timing((), caller_call_ref="   ")
        self.assertEqual(result["caller_record_count"], 0)
        self.assertEqual(result["caller_timing_evidence"], "not_evaluated")


if __name__ == "__main__":
    unittest.main()
