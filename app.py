"""Flask app: serves the calculator UI and calculation API."""

from __future__ import annotations

from flask import Flask, jsonify, render_template, request

from calculator import (
    CalculationError,
    calculate,
    evaluate_expression,
    format_result,
    format_rounded,
    parse_decimal_places,
    parse_number,
)

app = Flask(__name__)


@app.get("/")
def index():
    return render_template("index.html")


def _optional_decimal_places(data: dict):
    if "decimal_places" not in data:
        return None
    return parse_decimal_places(data["decimal_places"])


@app.post("/api/calculate")
def api_calculate():
    """
    Calculate either:
    - binary: {a, b, operator}  (legacy / unit-test contract)
    - expression: {expression}  (chained ops with precedence)

    Optional decimal_places (0–8) adds a rounded `display` field.
    `result` is always the normalised exact value used for further maths.
    """
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Malformed JSON"}), 400
    if not isinstance(data, dict):
        return jsonify({"error": "JSON body must be an object"}), 400

    try:
        places = _optional_decimal_places(data)

        if "expression" in data:
            if not isinstance(data["expression"], str):
                return jsonify({"error": "Expression must be a string"}), 400
            exact_decimal = evaluate_expression(data["expression"])
            exact = format_result(exact_decimal)
        else:
            missing = [field for field in ("a", "b", "operator") if field not in data]
            if missing:
                return jsonify(
                    {"error": f"Missing required field(s): {', '.join(missing)}"}
                ), 400
            exact = calculate(data["a"], data["b"], data["operator"])
            exact_decimal = parse_number(exact, "result")

        payload = {"result": exact}
        if places is not None:
            payload["display"] = format_rounded(exact_decimal, places)
        return jsonify(payload), 200

    except CalculationError as exc:
        return jsonify({"error": str(exc)}), 400


@app.post("/api/format")
def api_format():
    """Re-round an exact result for display without recalculating an expression."""
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Malformed JSON"}), 400
    if not isinstance(data, dict):
        return jsonify({"error": "JSON body must be an object"}), 400

    if "value" not in data or "decimal_places" not in data:
        return jsonify({"error": "Missing required field(s): value, decimal_places"}), 400

    try:
        places = parse_decimal_places(data["decimal_places"])
        number = parse_number(data["value"], "value")
        return jsonify({"display": format_rounded(number, places)}), 200
    except CalculationError as exc:
        return jsonify({"error": str(exc)}), 400


if __name__ == "__main__":
    # Debug disabled by default — suitable for local demo without exposing the debugger.
    app.run(host="127.0.0.1", port=5000, debug=False)
