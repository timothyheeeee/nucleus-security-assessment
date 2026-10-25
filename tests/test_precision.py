"""Regression tests for working vs display precision and thread context."""

import threading

import pytest

from calculator import (
    CalculationError,
    calculate,
    evaluate_expression_formatted,
    format_result,
    format_rounded,
    parse_number,
)
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


class TestWorkingVsDisplayPrecision:
    def test_large_fraction_not_destroyed_by_format_result(self):
        value = parse_number("100000000000000.005")
        assert format_rounded(value, 2) == "100000000000000.01"
        serialized = format_result(value)
        # Working serialization must retain enough precision for correct re-rounding.
        assert format_rounded(parse_number(serialized), 2) == "100000000000000.01"

    def test_api_calculate_format_round_trip(self, client):
        calc = client.post(
            "/api/calculate",
            json={
                "expression": "100000000000000.005 + 0",
                "decimal_places": 2,
            },
        )
        assert calc.status_code == 200
        body = calc.get_json()
        assert body["display"] == "100000000000000.01"

        fmt = client.post(
            "/api/format",
            json={"value": body["result"], "decimal_places": 2},
        )
        assert fmt.status_code == 200
        assert fmt.get_json()["display"] == "100000000000000.01"

    def test_binary_path_same_precision(self, client):
        response = client.post(
            "/api/calculate",
            json={
                "a": "100000000000000.005",
                "b": "0",
                "operator": "+",
                "decimal_places": 2,
            },
        )
        assert response.status_code == 200
        assert response.get_json()["display"] == "100000000000000.01"

    def test_chain_after_one_seventh(self):
        seventh = evaluate_expression_formatted("1 / 7")
        # Working result keeps ~50 significant digits (not collapsed to a 16-digit context).
        assert seventh.startswith("0.142857142857142857")
        assert len(seventh) > 20
        # Finite Decimal precision: 1/7*7 is extremely close to 1, not bit-identical "1".
        product = calculate(seventh, "7", "*")
        assert product.startswith("0.999999")

    def test_classic_cases(self):
        assert evaluate_expression_formatted("0.1 + 0.2") == "0.3"
        assert evaluate_expression_formatted("10 + 5 * 2") == "20"
        assert evaluate_expression_formatted("(10 + 5) * 2") == "30"
        assert format_rounded(parse_number(evaluate_expression_formatted("1 / 8")), 2) == "0.13"
        assert evaluate_expression_formatted("-5 + 2") == "-3"
        assert evaluate_expression_formatted("((2 + 3) * (4 - 1))") == "15"

    def test_thread_local_context_consistency(self):
        outcomes: list[str] = []

        def worker() -> None:
            outcomes.append(format_rounded(parse_number("100000000000000.005"), 2))

        threads = [threading.Thread(target=worker) for _ in range(4)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        assert outcomes == ["100000000000000.01"] * 4

    def test_giant_exponent_rejected(self):
        with pytest.raises(CalculationError):
            parse_number("1e999999")

    def test_overlong_rejected(self):
        with pytest.raises(CalculationError, match="maximum length"):
            parse_number("1" * 65)
