import unittest

from tools.cdr_caller_timing_evidence import summarize_caller_timing
from tools.cdr_queue_analyzer import CdrRecord


class CallerUniqueCompleteEvidenceTests(unittest.TestCase):
    def test_true_only_for_one_complete_exact_ref_row(self) -> None:
        result = summarize_caller_timing(
            (CdrRecord("caller-a", 17, 5, {}),),
            caller_call_ref="caller-a",
        )
        self.assertIs(result["caller_has_unique_complete_timing_record"], True)

    def test_false_for_duplicate_mixed_incomplete_absent_and_blank(self) -> None:
        cases = (
            summarize_caller_timing(
                (CdrRecord("caller-a", 17, 5, {}), CdrRecord("caller-a", 18, 6, {})),
                caller_call_ref="caller-a",
            ),
            summarize_caller_timing(
                (CdrRecord("caller-a", 17, 5, {}), CdrRecord("caller-a", None, 6, {})),
                caller_call_ref="caller-a",
            ),
            summarize_caller_timing(
                (CdrRecord("caller-a", None, 6, {}),),
                caller_call_ref="caller-a",
            ),
            summarize_caller_timing((), caller_call_ref="caller-a"),
            summarize_caller_timing((), caller_call_ref="   "),
        )
        for result in cases:
            self.assertIs(result["caller_has_unique_complete_timing_record"], False)


if __name__ == "__main__":
    unittest.main()
