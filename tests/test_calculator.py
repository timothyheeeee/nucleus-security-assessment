"""Unit tests for pure calculation logic."""

import pytest

from calculator import CalculationError, calculate, format_result, parse_number
from decimal import Decimal


class TestCalculate:
    def test_addition(self):
        assert calculate("8", "5", "+") == "13"

    def test_subtraction(self):
        assert calculate("3", "7", "-") == "-4"

    def test_multiplication(self):
        assert calculate("2.5", "4", "*") == "10"

    def test_division(self):
        assert calculate("10", "4", "/") == "2.5"

    def test_decimal_precision(self):
        assert calculate("0.1", "0.2", "+") == "0.3"

    def test_negative_operands(self):
        assert calculate("-5", "2", "+") == "-3"

    def test_zero_multiplication(self):
        assert calculate("0", "8", "*") == "0"

    def test_division_by_zero(self):
        with pytest.raises(CalculationError, match="Division by zero"):
            calculate("8", "0", "/")

    def test_invalid_operator(self):
        with pytest.raises(CalculationError, match="Unsupported operator"):
            calculate("8", "2", "^")

    def test_invalid_operand(self):
        with pytest.raises(CalculationError):
            calculate("hello", "2", "+")

    def test_boolean_rejected(self):
        with pytest.raises(CalculationError, match="booleans"):
            calculate(True, "2", "+")

    def test_nan_string_rejected(self):
        with pytest.raises(CalculationError, match="non-finite"):
            calculate("NaN", "1", "+")

    def test_infinity_rejected(self):
        with pytest.raises(CalculationError, match="non-finite"):
            calculate("Infinity", "1", "+")

    def test_input_too_long(self):
        with pytest.raises(CalculationError, match="maximum length"):
            calculate("1" * 65, "1", "+")

    def test_negative_zero_normalised(self):
        assert calculate("-0", "0", "+") == "0"

    def test_integer_inputs(self):
        assert calculate(12, 3, "/") == "4"

    def test_repeating_division_is_reenterable(self):
        # Results must stay within MAX_NUMERIC_LENGTH so chaining works.
        result = calculate("1", "7", "/")
        assert len(result) <= 64
        assert calculate(result, "0", "+") == result

    def test_overflow_rejected(self):
        with pytest.raises(CalculationError, match="exceeds supported limits|Calculation failed"):
            calculate("9e999999", "9e999999", "*")


class TestParseAndFormat:
    def test_parse_strips_whitespace(self):
        assert parse_number("  3.5  ") == Decimal("3.5")

    def test_format_trims_trailing_zeros(self):
        assert format_result(Decimal("5.0")) == "5"
        assert format_result(Decimal("0.3000")) == "0.3"
