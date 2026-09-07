import json
import unittest

from tools.cdr_queue_analyzer import CdrRecord
from tools.cdr_timing_report import SEMANTIC_WARNING, build_caller_timing_report_json


class CallerTimingJsonArtifactTests(unittest.TestCase):
    def test_unique_complete_row_exports_raw_values_without_semantic_guess(self) -> None:
        raw = build_caller_timing_report_json(
            (CdrRecord("caller-a", 17, 5, {}),),
            caller_call_ref="caller-a",
        )
        payload = json.loads(raw)

        self.assertEqual(payload["caller_ref"], "caller-a")
        self.assertEqual(payload["records"], 1)
        self.assertEqual(payload["complete"], 1)
        self.assertEqual(payload["incomplete"], 0)
        self.assertEqual(payload["evidence"], "single_complete_caller_timing_record")
        self.assertEqual(payload["raw_t_ecd_seconds"], 17)
        self.assertEqual(payload["raw_t_dba_seconds"], 5)
        self.assertEqual(payload["warning"], SEMANTIC_WARNING)

    def test_competing_rows_export_null_timing_values(self) -> None:
        raw = build_caller_timing_report_json(
            (
                CdrRecord("caller-a", 17, 5, {}),
                CdrRecord("caller-a", 18, 6, {}),
            ),
            caller_call_ref="caller-a",
        )
        payload = json.loads(raw)

        self.assertEqual(payload["records"], 2)
        self.assertEqual(payload["evidence"], "multiple_complete_caller_timing_records")
        self.assertIsNone(payload["raw_t_ecd_seconds"])
        self.assertIsNone(payload["raw_t_dba_seconds"])

    def test_json_artifact_is_deterministic(self) -> None:
        records = (CdrRecord("caller-a", 17, 5, {}),)
        first = build_caller_timing_report_json(records, caller_call_ref="caller-a")
        second = build_caller_timing_report_json(records, caller_call_ref="caller-a")

        self.assertEqual(first, second)
        self.assertIn('"warning":"raw timing fields only;', first)


if __name__ == "__main__":
    unittest.main()
