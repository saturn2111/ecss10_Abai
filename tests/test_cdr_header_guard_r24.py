from __future__ import annotations

import unittest

from tools.cdr_header_guard import validate_cdr_header


class CdrHeaderGuardTests(unittest.TestCase):
    def test_normalizes_outer_whitespace_without_changing_order(self) -> None:
        self.assertEqual(
            validate_cdr_header([" CONN_ID ", "T_ECD", " T_DBA"]),
            ("CONN_ID", "T_ECD", "T_DBA"),
        )

    def test_rejects_duplicate_normalized_column(self) -> None:
        with self.assertRaisesRegex(ValueError, "duplicate column: EXTRA"):
            validate_cdr_header(("CONN_ID", "EXTRA", " EXTRA "))

    def test_rejects_blank_column(self) -> None:
        with self.assertRaisesRegex(ValueError, "blank column"):
            validate_cdr_header(("CONN_ID", " ", "T_ECD", "T_DBA"))

    def test_rejects_non_string_column(self) -> None:
        with self.assertRaisesRegex(ValueError, "exact strings"):
            validate_cdr_header(("CONN_ID", 7, "T_ECD", "T_DBA"))

    def test_rejects_arbitrary_iterables_and_empty_header(self) -> None:
        with self.assertRaisesRegex(ValueError, "exact list or tuple"):
            validate_cdr_header({"CONN_ID", "T_ECD", "T_DBA"})
        with self.assertRaisesRegex(ValueError, "header is empty"):
            validate_cdr_header(())


if __name__ == "__main__":
    unittest.main()
