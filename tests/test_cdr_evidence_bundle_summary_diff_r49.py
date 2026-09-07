from __future__ import annotations

import json
import unittest

from tools.cdr_evidence_bundle import BUNDLE_WARNING
from tools.cdr_evidence_bundle_summary import SUMMARY_SCHEMA
from tools.cdr_evidence_bundle_summary_diff import DIFF_SCHEMA, build_diff_json, diff_summaries


def summary(*, items: int, records: int, complete: int, incomplete: int, counts: dict[str, int]) -> dict[str, object]:
    return {
        "schema": SUMMARY_SCHEMA,
        "items": items,
        "records": records,
        "complete": complete,
        "incomplete": incomplete,
        "evidence_counts": counts,
        "warning": BUNDLE_WARNING,
    }


class EvidenceBundleSummaryDiffTests(unittest.TestCase):
    def test_reports_signed_cardinality_and_classification_deltas(self) -> None:
        before = summary(items=2, records=3, complete=2, incomplete=1, counts={"unique_complete": 1, "mixed": 1})
        after = summary(items=3, records=5, complete=4, incomplete=1, counts={"unique_complete": 2, "mixed": 1})

        result = diff_summaries(before, after)

        self.assertEqual(result["schema"], DIFF_SCHEMA)
        self.assertEqual(result["delta"], {"items": 1, "records": 2, "complete": 2, "incomplete": 0})
        self.assertEqual(result["evidence_count_delta"], {"mixed": 0, "unique_complete": 1})
        self.assertEqual(result["warning"], BUNDLE_WARNING)

    def test_missing_classification_is_treated_as_zero_for_delta_only(self) -> None:
        before = summary(items=1, records=1, complete=1, incomplete=0, counts={"unique_complete": 1})
        after = summary(items=1, records=1, complete=0, incomplete=1, counts={"incomplete_only": 1})

        result = diff_summaries(before, after)

        self.assertEqual(result["evidence_count_delta"], {"incomplete_only": 1, "unique_complete": -1})

    def test_rejects_inconsistent_summary(self) -> None:
        bad = summary(items=1, records=2, complete=2, incomplete=1, counts={"unique_complete": 1})
        good = summary(items=1, records=1, complete=1, incomplete=0, counts={"unique_complete": 1})
        with self.assertRaises(ValueError):
            diff_summaries(bad, good)

    def test_json_is_deterministic_and_semantics_remain_warning_only(self) -> None:
        before = summary(items=0, records=0, complete=0, incomplete=0, counts={})
        after = summary(items=0, records=0, complete=0, incomplete=0, counts={})
        rendered = build_diff_json(before, after)
        payload = json.loads(rendered)
        self.assertEqual(rendered, build_diff_json(before, after))
        self.assertEqual(payload["warning"], BUNDLE_WARNING)
        self.assertNotIn("queue_wait", rendered)
        self.assertNotIn("final_duration", rendered)
        self.assertNotIn("logical_call_id", rendered)


if __name__ == "__main__":
    unittest.main()
