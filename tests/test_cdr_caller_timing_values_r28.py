import unittest

from tools.cdr_caller_timing_evidence import summarize_caller_timing
from tools.cdr_queue_analyzer import CdrRecord


class CallerTimingValuesTests(unittest.TestCase):
    def test_surfaces_values_only_for_one_complete_exact_ref_row(self) -> None:
        result = summarize_caller_timing(
            (
                CdrRecord("caller-a", 17, 5, {}),
                CdrRecord("operator-b", 99, 1, {}),
            ),
            caller_call_ref="caller-a",
        )

        self.assertEqual(result["caller_timing_evidence"], "single_complete_caller_timing_record")
        self.assertEqual(result["caller_t_ecd_seconds"], 17)
        self.assertEqual(result["caller_t_dba_seconds"], 5)

    def test_duplicate_or_mixed_rows_do_not_select_timing_values(self) -> None:
        duplicate = summarize_caller_timing(
            (
                CdrRecord("caller-a", 17, 5, {}),
                CdrRecord("caller-a", 18, 6, {}),
            ),
            caller_call_ref="caller-a",
        )
        mixed = summarize_caller_timing(
            (
                CdrRecord("caller-a", 17, 5, {}),
                CdrRecord("caller-a", None, 6, {}),
            ),
            caller_call_ref="caller-a",
        )

        self.assertIsNone(duplicate["caller_t_ecd_seconds"])
        self.assertIsNone(duplicate["caller_t_dba_seconds"])
        self.assertIsNone(mixed["caller_t_ecd_seconds"])
        self.assertIsNone(mixed["caller_t_dba_seconds"])

    def test_blank_ref_has_no_selected_values(self) -> None:
        result = summarize_caller_timing((), caller_call_ref="   ")
        self.assertIsNone(result["caller_t_ecd_seconds"])
        self.assertIsNone(result["caller_t_dba_seconds"])


if __name__ == "__main__":
    unittest.main()
