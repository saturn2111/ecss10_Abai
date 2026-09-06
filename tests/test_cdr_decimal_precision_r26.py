import unittest

from tools.cdr_queue_analyzer import _to_int


class CdrDecimalPrecisionGuardTests(unittest.TestCase):
    def test_preserves_large_integer_without_binary_float_rounding(self):
        self.assertEqual(_to_int("9007199254740993"), 9007199254740993)

    def test_integral_decimal_and_comma_forms_remain_supported(self):
        self.assertEqual(_to_int("12.0"), 12)
        self.assertEqual(_to_int("12,0"), 12)

    def test_fractional_and_non_finite_values_fail_closed(self):
        for value in ("12.5", "NaN", "Infinity", "-Infinity"):
            with self.subTest(value=value):
                self.assertIsNone(_to_int(value))

    def test_negative_value_fails_closed(self):
        self.assertIsNone(_to_int("-1"))


if __name__ == "__main__":
    unittest.main()
