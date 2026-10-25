"""Tests for expression evaluation, precedence, and decimal rounding."""

import pytest

from calculator import (
    CalculationError,
    evaluate_expression_formatted,
    format_rounded,
    parse_number,
)


class TestExpressionPrecedence:
    def test_simple_addition_expression(self):
        assert evaluate_expression_formatted("1 + 2") == "3"

    def test_multi_digit(self):
        assert evaluate_expression_formatted("12 + 34") == "46"

    def test_division(self):
        assert evaluate_expression_formatted("10 / 4") == "2.5"

    def test_precedence_multiply_before_add(self):
        # 10 + 5 × 2 = 20, not left-to-right 30
        assert evaluate_expression_formatted("10 + 5 * 2") == "20"

    def test_precedence_divide_before_subtract(self):
        assert evaluate_expression_formatted("10 - 8 / 2") == "6"

    def test_left_associative_same_precedence(self):
        assert evaluate_expression_formatted("8 / 2 / 2") == "2"

    def test_unicode_operators(self):
        assert evaluate_expression_formatted("10 ÷ 4") == "2.5"
        assert evaluate_expression_formatted("3 × 4") == "12"

    def test_negative_operand(self):
        assert evaluate_expression_formatted("-5 + 2") == "-3"

    def test_division_by_zero(self):
        with pytest.raises(CalculationError, match="Division by zero"):
            evaluate_expression_formatted("8 / 0")

    def test_malformed_trailing_operator(self):
        with pytest.raises(CalculationError, match="Malformed"):
            evaluate_expression_formatted("1 +")

    def test_rejected_letters(self):
        with pytest.raises(CalculationError):
            evaluate_expression_formatted("1 + abc")

    def test_parentheses_override_precedence(self):
        assert evaluate_expression_formatted("(10 + 5) * 2") == "30"
        assert evaluate_expression_formatted("10 + 5 * 2") == "20"

    def test_nested_parentheses(self):
        assert evaluate_expression_formatted("((2 + 3) * (4 - 1))") == "15"

    def test_implicit_multiplication_before_paren(self):
        assert evaluate_expression_formatted("2(3 + 1)") == "8"

    def test_mismatched_parentheses(self):
        with pytest.raises(CalculationError):
            evaluate_expression_formatted("(1 + 2")
        with pytest.raises(CalculationError):
            evaluate_expression_formatted("1 + 2)")


class TestRounding:
    def test_default_style_two_places(self):
        value = parse_number(evaluate_expression_formatted("10 / 3"))
        assert format_rounded(value, 2) == "3.33"

    def test_zero_places(self):
        value = parse_number(evaluate_expression_formatted("10 / 3"))
        assert format_rounded(value, 0) == "3"
        value2 = parse_number(evaluate_expression_formatted("8 / 3"))
        assert format_rounded(value2, 0) == "3"

    def test_four_places(self):
        value = parse_number(evaluate_expression_formatted("10 / 3"))
        assert format_rounded(value, 4) == "3.3333"

    def test_one_eighth(self):
        value = parse_number(evaluate_expression_formatted("1 / 8"))
        assert format_rounded(value, 2) == "0.13"
        assert format_rounded(value, 4) == "0.125"

    def test_whole_number_no_trailing_zeros(self):
        value = parse_number(evaluate_expression_formatted("2 + 3"))
        assert format_rounded(value, 2) == "5"

    def test_terminating_decimal_strips_zeros(self):
        value = parse_number(evaluate_expression_formatted("10 / 4"))
        assert format_rounded(value, 2) == "2.5"

    def test_negative_rounding(self):
        value = parse_number(evaluate_expression_formatted("-10 / 3"))
        assert format_rounded(value, 2) == "-3.33"

    def test_half_up(self):
        # 0.125 to 2 places → 0.13 (ROUND_HALF_UP)
        assert format_rounded(parse_number("0.125"), 2) == "0.13"

    def test_invalid_places(self):
        with pytest.raises(CalculationError):
            format_rounded(parse_number("1"), 9)
