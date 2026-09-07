import unittest

from tools.cdr_caller_timing_evidence import caller_has_competing_timing_records


class CallerCompetingTimingEvidenceTests(unittest.TestCase):
    def test_no_or_single_record_is_not_competing(self) -> None:
        for complete_count, incomplete_count in ((0, 0), (1, 0), (0, 1)):
            self.assertFalse(
                caller_has_competing_timing_records(complete_count, incomplete_count)
            )

    def test_multiple_or_mixed_records_are_competing(self) -> None:
        for complete_count, incomplete_count in ((2, 0), (0, 2), (1, 1), (2, 1)):
            self.assertTrue(
                caller_has_competing_timing_records(complete_count, incomplete_count)
            )

    def test_rejects_invalid_counts_fail_closed(self) -> None:
        for complete_count, incomplete_count in ((-1, 0), (0, -1)):
            with self.assertRaises(ValueError):
                caller_has_competing_timing_records(complete_count, incomplete_count)
        for complete_count, incomplete_count in ((True, 0), (0, None), (1.0, 0)):
            with self.assertRaises(TypeError):
                caller_has_competing_timing_records(complete_count, incomplete_count)


if __name__ == "__main__":
    unittest.main()
