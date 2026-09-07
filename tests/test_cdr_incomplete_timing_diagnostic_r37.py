import unittest

from tools.cdr_caller_timing_evidence import caller_has_incomplete_timing_records


class CallerIncompleteTimingDiagnosticTests(unittest.TestCase):
    def test_reports_incomplete_evidence_without_semantic_inference(self):
        self.assertFalse(caller_has_incomplete_timing_records(0, 0))
        self.assertFalse(caller_has_incomplete_timing_records(1, 0))
        self.assertTrue(caller_has_incomplete_timing_records(0, 1))
        self.assertTrue(caller_has_incomplete_timing_records(2, 1))

    def test_rejects_non_exact_or_negative_counts(self):
        for complete, incomplete in ((True, 0), (0, False), (1.0, 0), (0, "1")):
            with self.subTest(complete=complete, incomplete=incomplete):
                with self.assertRaises(TypeError):
                    caller_has_incomplete_timing_records(complete, incomplete)  # type: ignore[arg-type]
        for complete, incomplete in ((-1, 0), (0, -1)):
            with self.subTest(complete=complete, incomplete=incomplete):
                with self.assertRaises(ValueError):
                    caller_has_incomplete_timing_records(complete, incomplete)


if __name__ == "__main__":
    unittest.main()
