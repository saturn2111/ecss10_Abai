from __future__ import annotations

import unittest

from tools.cdr_ref_contract import normalize_cdr_call_ref


class CdrCallRefContractTests(unittest.TestCase):
    def test_trims_exact_string_ref(self) -> None:
        self.assertEqual(normalize_cdr_call_ref("  ref-123  "), "ref-123")

    def test_rejects_non_string_without_coercion(self) -> None:
        self.assertIsNone(normalize_cdr_call_ref(True))
        self.assertIsNone(normalize_cdr_call_ref(123))
        self.assertIsNone(normalize_cdr_call_ref(object()))

    def test_rejects_blank_oversized_and_control_character_refs(self) -> None:
        self.assertIsNone(normalize_cdr_call_ref("   "))
        self.assertIsNone(normalize_cdr_call_ref("x" * 513))
        self.assertIsNone(normalize_cdr_call_ref("ref\nspoof"))
        self.assertIsNone(normalize_cdr_call_ref("ref\x7fspoof"))

    def test_preserves_zero_like_text_as_evidence(self) -> None:
        self.assertEqual(normalize_cdr_call_ref("0"), "0")


if __name__ == "__main__":
    unittest.main()
