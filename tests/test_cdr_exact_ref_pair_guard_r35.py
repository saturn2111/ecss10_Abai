import unittest

from tools.cdr_queue_analyzer import analyze_queue_call


class ExactQueueAnalyzerRefPairGuardTests(unittest.TestCase):
    def test_rejects_non_exact_ref_types(self) -> None:
        for caller_ref, operator_ref in ((1, "operator"), ("caller", None), (b"caller", "operator")):
            with self.subTest(caller_ref=caller_ref, operator_ref=operator_ref):
                with self.assertRaisesRegex(TypeError, "must be exact strings"):
                    analyze_queue_call(
                        [],
                        caller_call_ref=caller_ref,
                        operator_call_ref=operator_ref,
                    )

    def test_rejects_surrounding_whitespace_on_nonblank_refs(self) -> None:
        for caller_ref, operator_ref in (
            (" caller", "operator"),
            ("caller ", "operator"),
            ("caller", " operator"),
            ("caller", "operator "),
        ):
            with self.subTest(caller_ref=caller_ref, operator_ref=operator_ref):
                with self.assertRaisesRegex(ValueError, "surrounding whitespace"):
                    analyze_queue_call(
                        [],
                        caller_call_ref=caller_ref,
                        operator_call_ref=operator_ref,
                    )

    def test_whitespace_only_ref_remains_missing_evidence(self) -> None:
        result = analyze_queue_call(
            [],
            caller_call_ref="   ",
            operator_call_ref="operator",
        )
        self.assertEqual(result["selection_reason"], "missing_call_ref")
        self.assertEqual(result["caller_call_ref"], "")
        self.assertEqual(result["correlation_evidence"], "not_evaluated")


if __name__ == "__main__":
    unittest.main()
