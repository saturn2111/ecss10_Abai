import unittest

from tools.cdr_queue_analyzer import CdrRecord
from tools.cdr_timing_report import SEMANTIC_WARNING, build_caller_timing_report


class CallerTimingReportTests(unittest.TestCase):
    def test_no_evidence_report_is_explicit_and_ambiguous_values_are_absent(self) -> None:
        report = build_caller_timing_report((), caller_call_ref="caller-a")

        self.assertIn("records=0", report)
        self.assertIn("evidence=no_caller_timing_evidence", report)
        self.assertIn("raw_t_ecd_seconds=n/a", report)
        self.assertIn("raw_t_dba_seconds=n/a", report)
        self.assertIn(f"warning={SEMANTIC_WARNING}", report)

    def test_unique_complete_row_surfaces_raw_values_without_semantic_inference(self) -> None:
        report = build_caller_timing_report(
            (CdrRecord("caller-a", 17, 5, {}),),
            caller_call_ref="caller-a",
        )

        self.assertIn("evidence=single_complete_caller_timing_record", report)
        self.assertIn("raw_t_ecd_seconds=17", report)
        self.assertIn("raw_t_dba_seconds=5", report)
        self.assertIn("queue wait", report)
        self.assertIn("final duration", report)
        self.assertIn("not inferred", report)

    def test_competing_rows_never_surface_ambiguous_raw_values(self) -> None:
        report = build_caller_timing_report(
            (
                CdrRecord("caller-a", 17, 5, {}),
                CdrRecord("caller-a", 18, 6, {}),
            ),
            caller_call_ref="caller-a",
        )

        self.assertIn("records=2", report)
        self.assertIn("evidence=multiple_complete_caller_timing_records", report)
        self.assertIn("raw_t_ecd_seconds=n/a", report)
        self.assertIn("raw_t_dba_seconds=n/a", report)

    def test_mixed_rows_never_surface_partial_timing_values(self) -> None:
        report = build_caller_timing_report(
            (
                CdrRecord("caller-a", 17, 5, {}),
                CdrRecord("caller-a", None, 6, {}),
            ),
            caller_call_ref="caller-a",
        )

        self.assertIn("evidence=mixed_complete_and_incomplete_caller_timing_records", report)
        self.assertIn("raw_t_ecd_seconds=n/a", report)
        self.assertIn("raw_t_dba_seconds=n/a", report)


if __name__ == "__main__":
    unittest.main()
