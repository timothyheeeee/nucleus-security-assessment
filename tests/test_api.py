"""HTTP integration tests for the Flask calculation API."""

import json

import pytest

from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


class TestCalculateApi:
    def test_valid_calculation(self, client):
        response = client.post(
            "/api/calculate",
            data=json.dumps({"a": "12.5", "b": "2", "operator": "*"}),
            content_type="application/json",
        )
        assert response.status_code == 200
        assert response.get_json() == {"result": "25"}

    def test_addition_decimals(self, client):
        response = client.post(
            "/api/calculate",
            json={"a": "0.1", "b": "0.2", "operator": "+"},
        )
        assert response.status_code == 200
        assert response.get_json()["result"] == "0.3"

    def test_malformed_json(self, client):
        response = client.post(
            "/api/calculate",
            data="{not-json",
            content_type="application/json",
        )
        assert response.status_code == 400
        assert "error" in response.get_json()

    def test_missing_fields(self, client):
        response = client.post("/api/calculate", json={"a": "1"})
        assert response.status_code == 400
        body = response.get_json()
        assert "error" in body
        assert "Missing" in body["error"]

    def test_invalid_operator(self, client):
        response = client.post(
            "/api/calculate",
            json={"a": "8", "b": "2", "operator": "^"},
        )
        assert response.status_code == 400
        assert "Unsupported operator" in response.get_json()["error"]

    def test_invalid_operand_type_list(self, client):
        response = client.post(
            "/api/calculate",
            json={"a": [1], "b": "2", "operator": "+"},
        )
        assert response.status_code == 400
        assert "error" in response.get_json()

    def test_json_array_body_rejected(self, client):
        response = client.post("/api/calculate", json=[1, 2, 3])
        assert response.status_code == 400
        assert "object" in response.get_json()["error"].lower()

    def test_boolean_operand_rejected(self, client):
        response = client.post(
            "/api/calculate",
            json={"a": True, "b": "2", "operator": "+"},
        )
        assert response.status_code == 400

    def test_division_by_zero(self, client):
        response = client.post(
            "/api/calculate",
            json={"a": "8", "b": "0", "operator": "/"},
        )
        assert response.status_code == 400
        assert "Division by zero" in response.get_json()["error"]

    def test_overflow_returns_json_error_not_500(self, client):
        response = client.post(
            "/api/calculate",
            json={"a": "9e999999", "b": "9e999999", "operator": "*"},
        )
        assert response.status_code == 400
        body = response.get_json()
        assert body is not None
        assert "error" in body

    def test_non_finite_rejected(self, client):
        response = client.post(
            "/api/calculate",
            json={"a": "NaN", "b": "1", "operator": "+"},
        )
        assert response.status_code == 400

    def test_non_json_content_type(self, client):
        response = client.post(
            "/api/calculate",
            data="a=1&b=2&operator=%2B",
            content_type="application/x-www-form-urlencoded",
        )
        assert response.status_code == 400

    def test_index_page(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert b"Calculator" in response.data
        assert b"decimal-places" in response.data

    def test_expression_with_precedence(self, client):
        response = client.post(
            "/api/calculate",
            json={"expression": "10 + 5 * 2", "decimal_places": 2},
        )
        assert response.status_code == 200
        body = response.get_json()
        assert body["result"] == "20"
        assert body["display"] == "20"

    def test_expression_with_parentheses(self, client):
        response = client.post(
            "/api/calculate",
            json={"expression": "(10 + 5) * 2", "decimal_places": 2},
        )
        assert response.status_code == 200
        body = response.get_json()
        assert body["result"] == "30"
        assert body["display"] == "30"

    def test_expression_division_rounding(self, client):
        response = client.post(
            "/api/calculate",
            json={"expression": "10 / 3", "decimal_places": 2},
        )
        assert response.status_code == 200
        body = response.get_json()
        assert body["display"] == "3.33"
        # Exact result retains more precision than the rounded display.
        assert body["result"].startswith("3.333")

    def test_expression_division_by_zero(self, client):
        response = client.post(
            "/api/calculate",
            json={"expression": "8 / 0", "decimal_places": 2},
        )
        assert response.status_code == 400
        assert "Division by zero" in response.get_json()["error"]

    def test_format_reuses_exact_value(self, client):
        calc = client.post(
            "/api/calculate",
            json={"expression": "1 / 3", "decimal_places": 2},
        ).get_json()
        exact = calc["result"]
        assert calc["display"] == "0.33"

        rounded5 = client.post(
            "/api/format",
            json={"value": exact, "decimal_places": 5},
        )
        assert rounded5.status_code == 200
        assert rounded5.get_json()["display"] == "0.33333"

        rounded2 = client.post(
            "/api/format",
            json={"value": exact, "decimal_places": 2},
        )
        assert rounded2.get_json()["display"] == "0.33"
