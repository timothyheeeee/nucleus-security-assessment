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
    localcontext,
)
from typing import List, Union

# Working arithmetic precision (significant digits). Finite — not mathematical exactness.
WORKING_PREC = 50
MIN_DECIMAL_PLACES = 0
MAX_DECIMAL_PLACES = 8
DEFAULT_DECIMAL_PLACES = 2
# Cap magnitude so integer digits + max display places fit in WORKING_PREC.
# quantize(n, 10^-p) needs roughly adjusted()+1+p significant digits when |n| >= 1.
MAX_ABS_ADJUSTED_EXPONENT = WORKING_PREC - MAX_DECIMAL_PLACES - 1  # 41
# Max characters for a numeric token or serialized working result (DoS bound).
MAX_NUMERIC_LENGTH = 64
MAX_EXPRESSION_LENGTH = 200
# Backwards-compatible alias used by older tests/docs.
MAX_INPUT_LENGTH = MAX_NUMERIC_LENGTH

SUPPORTED_OPERATORS = frozenset({"+", "-", "*", "/"})

# Explicit context used for arithmetic and working serialization (not process-global).
WORKING_CONTEXT = Context(
    prec=WORKING_PREC,
    rounding=ROUND_HALF_UP,
    Emax=999999,
    Emin=-999999,
)

# Numbers: optional leading minus, digits, optional fraction.
_NUMBER_RE = re.compile(r"-?\d+(?:\.\d*)?|-?\.\d+")

NumberLike = Union[str, int, float, Decimal]


class CalculationError(ValueError):
    """Raised when a calculation cannot be completed safely."""


def _reject_bool(value: object, field: str) -> None:
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


def _check_magnitude(number: Decimal, field: str = "value") -> None:
    if not number.is_finite():
        raise CalculationError(f"Invalid {field}: non-finite number")
    if abs(number.adjusted()) > MAX_ABS_ADJUSTED_EXPONENT:
        raise CalculationError(f"{field} magnitude exceeds supported limits")


def parse_number(value: object, field: str = "operand") -> Decimal:
    """Parse a user-facing numeric value into Decimal under WORKING_CONTEXT."""
    _reject_bool(value, field)

    if value is None:
        raise CalculationError(f"Missing operand '{field}'")

    with localcontext(WORKING_CONTEXT.copy()):
        if isinstance(value, Decimal):
            number = +value
        elif isinstance(value, int):
            number = Decimal(value)
        elif isinstance(value, float):
            if value != value or value in (float("inf"), float("-inf")):
                raise CalculationError(f"Invalid operand for '{field}': non-finite number")
            number = Decimal(str(value))
        elif isinstance(value, str):
            text = value.strip()
            if not text:
                raise CalculationError(f"Invalid operand for '{field}': empty value")
            if len(text) > MAX_NUMERIC_LENGTH:
                raise CalculationError(
                    f"Invalid operand for '{field}': exceeds maximum length of {MAX_NUMERIC_LENGTH}"
                )
            lowered = text.lower()
            if lowered in {
                "nan",
                "inf",
                "+inf",
                "-inf",
                "infinity",
                "+infinity",
                "-infinity",
            }:
                raise CalculationError(f"Invalid operand for '{field}': non-finite number")
            try:
                number = Decimal(text)
            except InvalidOperation as exc:
                raise CalculationError(
                    f"Invalid operand for '{field}': not a number"
                ) from exc
        else:
            raise CalculationError(f"Invalid operand for '{field}': unsupported type")

        number = +number
        _check_magnitude(number, field)
        return number


def format_result(value: Decimal) -> str:
    """
    Serialize a working-precision Decimal for chaining / API `result`.

    Does **not** apply user decimal-place display rounding, and does **not**
    reduce significant digits to a separate 16-digit display context.
    """
    with localcontext(WORKING_CONTEXT.copy()):
        number = +value
        _check_magnitude(number, "result")

        normalised = number.normalize()
        text = format(normalised, "f")
        if "." in text:
            text = text.rstrip("0").rstrip(".")
        if text in {"-0", "-0.0", ""}:
            return "0"
        if len(text) > MAX_NUMERIC_LENGTH:
            raise CalculationError("Result exceeds supported serialization length")
        return text


def format_rounded(value: Decimal, decimal_places: int) -> str:
    """
    Round for final **display** only using ROUND_HALF_UP.

    Operates on the full working-precision value, not a previously shortened
    serialization. Trailing zeros after the decimal point are stripped.
    """
    places = parse_decimal_places(decimal_places)

    with localcontext(WORKING_CONTEXT.copy()) as ctx:
        number = +value
        _check_magnitude(number, "result")

        # Reject values that cannot be quantized to `places` within WORKING_PREC.
        if number.copy_abs() >= 1:
            digits_needed = number.adjusted() + 1 + places
            if digits_needed > WORKING_PREC:
                raise CalculationError(
                    "Result cannot be rounded to the requested decimal places "
                    "within supported precision limits"
                )

        quantum = Decimal(1).scaleb(-places)
        # Extra headroom for the quantize step only (still bounded by check above).
        ctx.prec = WORKING_PREC + places + 2
        try:
            rounded = number.quantize(quantum, rounding=ROUND_HALF_UP)
        except (InvalidOperation, Overflow, Underflow) as exc:
            raise CalculationError("Calculation failed") from exc

        if not rounded.is_finite():
            raise CalculationError("Result is not a finite number")

        text = format(rounded, "f")
        if "." in text:
            text = text.rstrip("0").rstrip(".")
        if text in {"-0", "-0.0", ""}:
            return "0"
        if len(text) > MAX_NUMERIC_LENGTH:
            raise CalculationError("Result exceeds supported serialization length")
        return text


def _apply_operator(left: Decimal, right: Decimal, operator: str) -> Decimal:
    with localcontext(WORKING_CONTEXT.copy()):
        try:
            if operator == "+":
                result = left + right
            elif operator == "-":
                result = left - right
            elif operator == "*":
                result = left * right
            elif operator == "/":
                if right == 0:
                    raise CalculationError("Division by zero")
                result = left / right
            else:
                raise CalculationError("Unsupported operator")
        except DivisionByZero as exc:
            raise CalculationError("Division by zero") from exc
        except (InvalidOperation, Overflow, Underflow) as exc:
            raise CalculationError("Calculation failed") from exc

        result = +result
        _check_magnitude(result, "result")
        return result


def calculate_decimal(a: NumberLike, b: NumberLike, operator: str) -> Decimal:
    """Perform a single binary operation; return a working-precision Decimal."""
    if not isinstance(operator, str) or operator not in SUPPORTED_OPERATORS:
        raise CalculationError("Unsupported operator")

    left = parse_number(a, "a")
    right = parse_number(b, "b")
    return _apply_operator(left, right, operator)


def calculate(a: NumberLike, b: NumberLike, operator: str) -> str:
    """Binary operation returning a working-precision serialized result."""
    return format_result(calculate_decimal(a, b, operator))


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
    if len(number) > MAX_NUMERIC_LENGTH:
        raise CalculationError(
            f"Invalid operand: exceeds maximum length of {MAX_NUMERIC_LENGTH}"
        )
    parse_number(number, "operand")
    tokens.append(number)


def tokenize_expression(expression: str) -> List[str]:
    """Tokenise numbers, + - * /, and parentheses. No eval."""
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
    """Evaluate a restricted expression with precedence and parentheses."""
    tokens = tokenize_expression(expression)

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

    return stack[0]


def evaluate_expression_formatted(expression: str) -> str:
    """Evaluate an expression and return a working-precision serialized result."""
    return format_result(evaluate_expression(expression))
