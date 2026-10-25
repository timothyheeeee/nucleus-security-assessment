"""Pure arithmetic helpers for the calculator (no HTTP concerns)."""

from __future__ import annotations

import re
from decimal import (
    Context,
    Decimal,
    DivisionByZero,
    InvalidOperation,
    Overflow,
    ROUND_HALF_UP,
    Underflow,
    getcontext,
)
from typing import List, Union

# Working precision for intermediate arithmetic (not display rounding).
getcontext().prec = 50

MAX_INPUT_LENGTH = 32
MAX_EXPRESSION_LENGTH = 200
# Bound exact normalised results so they remain re-enterable as operands.
DISPLAY_PRECISION = 16
MIN_DECIMAL_PLACES = 0
MAX_DECIMAL_PLACES = 8
DEFAULT_DECIMAL_PLACES = 2
SUPPORTED_OPERATORS = frozenset({"+", "-", "*", "/"})
_DISPLAY_CONTEXT = Context(prec=DISPLAY_PRECISION, rounding=ROUND_HALF_UP)

# Numbers: optional leading minus, digits, optional fraction.
_NUMBER_RE = re.compile(r"-?\d+(?:\.\d*)?|-?\.\d+")

NumberLike = Union[str, int, float, Decimal]


class CalculationError(ValueError):
    """Raised when a calculation cannot be completed safely."""


def _reject_bool(value: object, field: str) -> None:
    # bool is a subclass of int in Python; treat it as invalid input.
    if isinstance(value, bool):
        raise CalculationError(f"Invalid operand for '{field}': booleans are not allowed")


def parse_decimal_places(value: object) -> int:
    """Validate and return an allowed decimal-places setting."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise CalculationError("decimal_places must be an integer")
    if value < MIN_DECIMAL_PLACES or value > MAX_DECIMAL_PLACES:
        raise CalculationError(
            f"decimal_places must be between {MIN_DECIMAL_PLACES} and {MAX_DECIMAL_PLACES}"
        )
    return value


def parse_number(value: object, field: str = "operand") -> Decimal:
    """Parse a user-facing numeric value into Decimal."""
    _reject_bool(value, field)

    if value is None:
        raise CalculationError(f"Missing operand '{field}'")

    if isinstance(value, Decimal):
        number = value
    elif isinstance(value, int):
        number = Decimal(value)
    elif isinstance(value, float):
        if value != value or value in (float("inf"), float("-inf")):
            raise CalculationError(f"Invalid operand for '{field}': non-finite number")
        # Convert via str to avoid binary float artifacts where possible.
        number = Decimal(str(value))
    elif isinstance(value, str):
        text = value.strip()
        if not text:
            raise CalculationError(f"Invalid operand for '{field}': empty value")
        if len(text) > MAX_INPUT_LENGTH:
            raise CalculationError(
                f"Invalid operand for '{field}': exceeds maximum length of {MAX_INPUT_LENGTH}"
            )
        lowered = text.lower()
        if lowered in {"nan", "inf", "+inf", "-inf", "infinity", "+infinity", "-infinity"}:
            raise CalculationError(f"Invalid operand for '{field}': non-finite number")
        try:
            number = Decimal(text)
        except InvalidOperation as exc:
            raise CalculationError(f"Invalid operand for '{field}': not a number") from exc
    else:
        raise CalculationError(f"Invalid operand for '{field}': unsupported type")

    if not number.is_finite():
        raise CalculationError(f"Invalid operand for '{field}': non-finite number")

    return number


def format_result(value: Decimal) -> str:
    """Normalise Decimal to an exact-ish display string (trim zeros, avoid -0)."""
    if not value.is_finite():
        raise CalculationError("Result is not a finite number")

    display_value = _DISPLAY_CONTEXT.create_decimal(value)
    if not display_value.is_finite():
        raise CalculationError("Result is not a finite number")

    normalised = display_value.normalize()
    text = format(normalised, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    if text in {"-0", "-0.0"}:
        return "0"
    if text == "":
        return "0"
    if len(text) > MAX_INPUT_LENGTH:
        raise CalculationError("Result exceeds display limits")
    return text


def format_rounded(value: Decimal, decimal_places: int) -> str:
    """
    Round for final display only using ROUND_HALF_UP.

    Trailing zeros after the decimal point are stripped so whole numbers
    and terminating decimals stay readable (e.g. 2.50 → 2.5, 5.00 → 5).
    """
    places = parse_decimal_places(decimal_places)
    if not value.is_finite():
        raise CalculationError("Result is not a finite number")

    quantum = Decimal(1).scaleb(-places)
    try:
        rounded = value.quantize(quantum, rounding=ROUND_HALF_UP)
    except (InvalidOperation, Overflow, Underflow) as exc:
        raise CalculationError("Calculation failed") from exc

    if not rounded.is_finite():
        raise CalculationError("Result is not a finite number")

    text = format(rounded, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    if text in {"-0", "-0.0"}:
        return "0"
    if text == "":
        return "0"
    return text


def _apply_operator(left: Decimal, right: Decimal, operator: str) -> Decimal:
    try:
        if operator == "+":
            return left + right
        if operator == "-":
            return left - right
        if operator == "*":
            return left * right
        if operator == "/":
            if right == 0:
                raise CalculationError("Division by zero")
            return left / right
    except DivisionByZero as exc:
        raise CalculationError("Division by zero") from exc
    except (InvalidOperation, Overflow, Underflow) as exc:
        raise CalculationError("Calculation failed") from exc
    raise CalculationError("Unsupported operator")


def calculate(a: NumberLike, b: NumberLike, operator: str) -> str:
    """
    Perform a single binary arithmetic operation.

    Returns a normalised exact result string (not decimal-place rounded).
    """
    if not isinstance(operator, str) or operator not in SUPPORTED_OPERATORS:
        raise CalculationError("Unsupported operator")

    left = parse_number(a, "a")
    right = parse_number(b, "b")
    result = _apply_operator(left, right, operator)

    if not result.is_finite():
        raise CalculationError("Result is not a finite number")

    return format_result(result)


def _normalise_expression_text(expression: str) -> str:
    return (
        expression.replace("−", "-")
        .replace("×", "*")
        .replace("÷", "/")
        .replace(" ", "")
    )


def _append_number_token(tokens: List[str], number: str) -> None:
    if number in {"-", ".", "-."}:
        raise CalculationError("Malformed expression")
    if len(number) > MAX_INPUT_LENGTH:
        raise CalculationError(
            f"Invalid operand: exceeds maximum length of {MAX_INPUT_LENGTH}"
        )
    parse_number(number, "operand")
    tokens.append(number)


def tokenize_expression(expression: str) -> List[str]:
    """
    Tokenise a restricted arithmetic expression into numbers, operators,
    and parentheses.

    Supports digits, one decimal point per number, optional leading minus
    on a number, the four operators + - * /, and ( ).
    """
    if not isinstance(expression, str):
        raise CalculationError("Expression must be a string")

    raw = expression.strip()
    if not raw:
        raise CalculationError("Expression is empty")
    if len(raw) > MAX_EXPRESSION_LENGTH:
        raise CalculationError("Expression is too long")

    text = _normalise_expression_text(raw)
    if not text:
        raise CalculationError("Expression is empty")

    tokens: List[str] = []
    i = 0
    # True when the next token should start a value (number or '(').
    expect_value = True
    depth = 0

    while i < len(text):
        ch = text[i]

        if expect_value:
            if ch == "(":
                tokens.append("(")
                depth += 1
                i += 1
                continue

            # Unary minus only when a value is expected.
            if ch == "-" and (i + 1) < len(text) and (
                text[i + 1].isdigit() or text[i + 1] == "."
            ):
                match = _NUMBER_RE.match(text, i)
                if not match:
                    raise CalculationError("Malformed expression")
                _append_number_token(tokens, match.group(0))
                i = match.end()
                expect_value = False
                continue

            if ch.isdigit() or ch == ".":
                match = _NUMBER_RE.match(text, i)
                if not match:
                    raise CalculationError("Malformed expression")
                _append_number_token(tokens, match.group(0))
                i = match.end()
                expect_value = False
                continue

            raise CalculationError("Malformed expression")

        # A value was just completed (number or ')').
        if ch == ")":
            if depth == 0:
                raise CalculationError("Mismatched parentheses")
            tokens.append(")")
            depth -= 1
            i += 1
            expect_value = False
            continue

        if ch in SUPPORTED_OPERATORS:
            tokens.append(ch)
            i += 1
            expect_value = True
            continue

        # Implicit multiplication: 2(3+1) or (1+2)(3+4)
        if ch == "(":
            tokens.append("*")
            tokens.append("(")
            depth += 1
            i += 1
            expect_value = True
            continue

        raise CalculationError("Malformed expression")

    if expect_value or not tokens or depth != 0:
        raise CalculationError("Malformed expression")

    return tokens


def evaluate_expression(expression: str) -> Decimal:
    """
    Evaluate a restricted expression with conventional precedence
    (* / before + -) and parentheses. No eval.
    """
    tokens = tokenize_expression(expression)

    # Shunting-yard → RPN
    output: List[str] = []
    ops: List[str] = []
    precedence = {"+": 1, "-": 1, "*": 2, "/": 2}

    for token in tokens:
        if token in SUPPORTED_OPERATORS:
            while (
                ops
                and ops[-1] in SUPPORTED_OPERATORS
                and precedence[ops[-1]] >= precedence[token]
            ):
                output.append(ops.pop())
            ops.append(token)
        elif token == "(":
            ops.append(token)
        elif token == ")":
            while ops and ops[-1] != "(":
                output.append(ops.pop())
            if not ops or ops[-1] != "(":
                raise CalculationError("Mismatched parentheses")
            ops.pop()
        else:
            output.append(token)

    while ops:
        if ops[-1] in {"(", ")"}:
            raise CalculationError("Mismatched parentheses")
        output.append(ops.pop())

    stack: List[Decimal] = []
    for token in output:
        if token in SUPPORTED_OPERATORS:
            if len(stack) < 2:
                raise CalculationError("Malformed expression")
            right = stack.pop()
            left = stack.pop()
            stack.append(_apply_operator(left, right, token))
        else:
            stack.append(parse_number(token, "operand"))

    if len(stack) != 1:
        raise CalculationError("Malformed expression")

    result = stack[0]
    if not result.is_finite():
        raise CalculationError("Result is not a finite number")
    return result


def evaluate_expression_formatted(expression: str) -> str:
    """Evaluate an expression and return a normalised exact result string."""
    return format_result(evaluate_expression(expression))
