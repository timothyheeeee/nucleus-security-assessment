(() => {
  "use strict";

  const displayEl = document.getElementById("display");
  const errorEl = document.getElementById("error");
  const keysEl = document.querySelector(".keys");
  const decimalPlacesEl = document.getElementById("decimal-places");

  const MAX_DIGITS = 32;
  const OPERATOR_SYMBOLS = { "+": "+", "-": "−", "*": "×", "/": "÷" };
  const OPERATORS = new Set(["+", "-", "*", "/"]);

  const state = {
    // Tokens: numbers, operators, "(" and ")"
    tokens: [],
    // Number currently being typed (null when waiting after operator / "(" )
    current: "0",
    justEvaluated: false,
    exactResult: null,
    pendingRequest: false,
    decimalPlaces: 2,
  };

  function setError(message) {
    if (!message) {
      errorEl.hidden = true;
      errorEl.textContent = "";
      return;
    }
    errorEl.hidden = false;
    errorEl.textContent = message;
  }

  function fitDisplay() {
    const maxPx = 37.6;
    const minPx = 18;
    displayEl.style.fontSize = `${maxPx}px`;
    let size = maxPx;
    while (size > minPx && displayEl.scrollWidth > displayEl.clientWidth + 1) {
      size -= 1;
      displayEl.style.fontSize = `${size}px`;
    }
    displayEl.scrollLeft = displayEl.scrollWidth;
  }

  function setDisplayText(text) {
    displayEl.textContent = text;
    fitDisplay();
  }

  function displayToken(token) {
    if (OPERATORS.has(token)) return OPERATOR_SYMBOLS[token];
    return token;
  }

  function expressionParts() {
    const parts = state.tokens.map(displayToken);
    if (state.current !== null) {
      parts.push(state.current);
    }
    return parts;
  }

  function renderExpression() {
    if (state.justEvaluated && state.exactResult !== null) {
      return;
    }
    const parts = expressionParts();
    setDisplayText(parts.length ? parts.join(" ") : "0");
  }

  function openParenCount() {
    let depth = 0;
    for (const token of state.tokens) {
      if (token === "(") depth += 1;
      if (token === ")") depth -= 1;
    }
    return depth;
  }

  function lastToken() {
    return state.tokens.length ? state.tokens[state.tokens.length - 1] : null;
  }

  function updateOperatorHighlight() {
    const last = lastToken();
    const active = state.current === null && OPERATORS.has(last) ? last : null;
    keysEl.querySelectorAll("[data-operator]").forEach((btn) => {
      btn.classList.toggle("is-active", btn.dataset.operator === active);
    });
  }

  function setBusy(busy) {
    state.pendingRequest = busy;
    keysEl.querySelectorAll("button").forEach((btn) => {
      btn.disabled = busy;
    });
    decimalPlacesEl.disabled = busy;
  }

  function clearAll() {
    state.tokens = [];
    state.current = "0";
    state.justEvaluated = false;
    state.exactResult = null;
    setError("");
    setDisplayText("0");
    updateOperatorHighlight();
  }

  function beginNewExpressionWith(digitOrDot) {
    state.tokens = [];
    state.justEvaluated = false;
    state.exactResult = null;
    state.current = digitOrDot === "." ? "0." : digitOrDot;
    renderExpression();
  }

  function digitCount(numberText) {
    return numberText.replace("-", "").replace(".", "").length;
  }

  function inputDigit(digit) {
    if (state.pendingRequest) return;
    setError("");

    if (state.justEvaluated) {
      beginNewExpressionWith(digit);
      updateOperatorHighlight();
      return;
    }

    // After a closing ')', inserting a digit implies multiplication.
    if (state.current === null && lastToken() === ")") {
      state.tokens.push("*");
      state.current = digit === "." ? "0." : digit;
      renderExpression();
      updateOperatorHighlight();
      return;
    }

    if (state.current === null) {
      state.current = digit === "." ? "0." : digit;
      renderExpression();
      updateOperatorHighlight();
      return;
    }

    if (digit === ".") {
      if (state.current.includes(".")) return;
      state.current += ".";
      renderExpression();
      return;
    }

    if (state.current === "0") {
      state.current = digit;
      renderExpression();
      return;
    }
    if (state.current === "-0") {
      state.current = `-${digit}`;
      renderExpression();
      return;
    }

    if (digitCount(state.current) >= MAX_DIGITS) {
      setError("Maximum input length reached");
      return;
    }

    state.current += digit;
    renderExpression();
  }

  function chooseOperator(op) {
    if (state.pendingRequest) return;
    setError("");

    if (state.justEvaluated) {
      state.tokens = [state.exactResult];
      state.current = null;
      state.justEvaluated = false;
      state.tokens.push(op);
      renderExpression();
      updateOperatorHighlight();
      return;
    }

    // Replace pending operator (but not after '(').
    if (state.current === null) {
      const last = lastToken();
      if (OPERATORS.has(last)) {
        state.tokens[state.tokens.length - 1] = op;
        renderExpression();
        updateOperatorHighlight();
        return;
      }
      // Allow ")*" style: operator after ')'
      if (last === ")") {
        state.tokens.push(op);
        renderExpression();
        updateOperatorHighlight();
        return;
      }
      return;
    }

    state.tokens.push(state.current);
    state.tokens.push(op);
    state.current = null;
    renderExpression();
    updateOperatorHighlight();
  }

  function inputOpenParen() {
    if (state.pendingRequest) return;
    setError("");

    if (state.justEvaluated) {
      state.tokens = ["("];
      state.current = null;
      state.justEvaluated = false;
      state.exactResult = null;
      renderExpression();
      updateOperatorHighlight();
      return;
    }

    // Fresh calculator showing only 0 → start with "("
    if (
      state.tokens.length === 0 &&
      state.current !== null &&
      (state.current === "0" || state.current === "-0")
    ) {
      state.tokens = ["("];
      state.current = null;
      renderExpression();
      updateOperatorHighlight();
      return;
    }

    if (state.current !== null) {
      // Implicit multiply: 2( → 2 × (
      state.tokens.push(state.current);
      state.tokens.push("*");
      state.tokens.push("(");
      state.current = null;
      renderExpression();
      updateOperatorHighlight();
      return;
    }

    const last = lastToken();
    if (last === ")") {
      state.tokens.push("*");
    }
    state.tokens.push("(");
    renderExpression();
    updateOperatorHighlight();
  }

  function inputCloseParen() {
    if (state.pendingRequest) return;
    setError("");

    if (state.justEvaluated) return;
    if (openParenCount() <= 0) return;

    if (state.current !== null) {
      state.tokens.push(state.current);
      state.current = null;
    } else {
      const last = lastToken();
      // Cannot close after operator or bare '('
      if (last === null || OPERATORS.has(last) || last === "(") {
        return;
      }
    }

    state.tokens.push(")");
    renderExpression();
    updateOperatorHighlight();
  }

  function toggleSign() {
    if (state.pendingRequest) return;
    setError("");

    if (state.justEvaluated) {
      const exact = state.exactResult || "0";
      let next;
      if (exact === "0") {
        next = "0";
      } else if (exact.startsWith("-")) {
        next = exact.slice(1);
      } else {
        next = `-${exact}`;
      }
      state.tokens = [];
      state.current = next;
      state.justEvaluated = false;
      state.exactResult = null;
      renderExpression();
      updateOperatorHighlight();
      return;
    }

    if (state.current === null) {
      // After '(' or operator, start a negative number.
      state.current = "-0";
      renderExpression();
      updateOperatorHighlight();
      return;
    }

    if (state.current.startsWith("-")) {
      state.current = state.current.slice(1) || "0";
    } else {
      state.current = `-${state.current}`;
    }
    renderExpression();
  }

  function backspace() {
    if (state.pendingRequest) return;
    setError("");

    if (state.justEvaluated) {
      clearAll();
      return;
    }

    if (state.current !== null) {
      if (
        state.current.length <= 1 ||
        (state.current.length === 2 && state.current.startsWith("-"))
      ) {
        if (state.tokens.length > 0) {
          state.current = null;
        } else {
          state.current = "0";
        }
      } else {
        state.current = state.current.slice(0, -1);
      }
      renderExpression();
      updateOperatorHighlight();
      return;
    }

    if (state.tokens.length === 0) {
      state.current = "0";
      renderExpression();
      updateOperatorHighlight();
      return;
    }

    const last = state.tokens.pop();
    if (OPERATORS.has(last) || last === "(") {
      const prev = lastToken();
      if (prev !== null && prev !== "(" && prev !== ")" && !OPERATORS.has(prev)) {
        state.current = state.tokens.pop();
      } else {
        state.current = null;
      }
    } else if (last === ")") {
      state.current = null;
    } else {
      // Removed a number token
      state.current = last;
    }
    renderExpression();
    updateOperatorHighlight();
  }

  function buildExpressionString() {
    const parts = state.tokens.slice();
    if (state.current !== null) {
      parts.push(state.current);
    }
    return parts.join(" ");
  }

  function expressionIsComplete() {
    if (openParenCount() !== 0) return false;

    const parts = state.tokens.slice();
    if (state.current !== null) {
      parts.push(state.current);
    }
    if (parts.length < 2) return false;

    const last = parts[parts.length - 1];
    // Must end with a number or ')'
    if (OPERATORS.has(last) || last === "(") return false;
    // Must contain at least one operator or a parenthesised expression
    return parts.some((t) => OPERATORS.has(t) || t === "(");
  }

  async function showRounded(exact) {
    const response = await fetch("/api/format", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        value: exact,
        decimal_places: state.decimalPlaces,
      }),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "Formatting failed");
    }
    setDisplayText(String(data.display));
  }

  async function evaluate() {
    if (state.pendingRequest) return;
    setError("");

    if (state.justEvaluated) return;

    if (openParenCount() !== 0) {
      setError("Close all parentheses before calculating");
      return;
    }

    if (!expressionIsComplete()) {
      setError("Enter a complete expression before pressing =");
      return;
    }

    const expression = buildExpressionString();
    setBusy(true);

    try {
      const response = await fetch("/api/calculate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          expression,
          decimal_places: state.decimalPlaces,
        }),
      });

      let data;
      try {
        data = await response.json();
      } catch {
        setError("Unexpected server response");
        return;
      }

      if (!response.ok) {
        setError(data.error || "Calculation failed");
        return;
      }

      const exact = data.result;
      const shown = data.display != null ? data.display : data.result;
      if (exact == null || shown == null) {
        setError("Unexpected server response");
        return;
      }

      state.exactResult = String(exact);
      state.justEvaluated = true;
      state.tokens = [];
      state.current = null;
      setDisplayText(String(shown));
      updateOperatorHighlight();
    } catch {
      setError("Unable to reach calculator service — is the app running?");
    } finally {
      setBusy(false);
    }
  }

  async function onDecimalPlacesChange() {
    const value = Number(decimalPlacesEl.value);
    if (!Number.isInteger(value) || value < 0 || value > 8) {
      decimalPlacesEl.value = String(state.decimalPlaces);
      return;
    }
    state.decimalPlaces = value;

    if (state.justEvaluated && state.exactResult !== null) {
      setBusy(true);
      setError("");
      try {
        await showRounded(state.exactResult);
      } catch (err) {
        setError(err.message || "Unable to update rounding");
      } finally {
        setBusy(false);
      }
    }
  }

  keysEl.addEventListener("click", (event) => {
    const button = event.target.closest("button");
    if (!button || !keysEl.contains(button)) return;

    if (button.dataset.digit !== undefined) {
      inputDigit(button.dataset.digit);
      return;
    }
    if (button.dataset.operator) {
      chooseOperator(button.dataset.operator);
      return;
    }
    if (button.dataset.paren === "(") {
      inputOpenParen();
      return;
    }
    if (button.dataset.paren === ")") {
      inputCloseParen();
      return;
    }

    switch (button.dataset.action) {
      case "clear":
        clearAll();
        break;
      case "backspace":
        backspace();
        break;
      case "sign":
        toggleSign();
        break;
      case "equals":
        evaluate();
        break;
      default:
        break;
    }
  });

  decimalPlacesEl.addEventListener("change", () => {
    onDecimalPlacesChange();
  });

  document.addEventListener("keydown", (event) => {
    if (event.ctrlKey || event.metaKey || event.altKey) return;
    if (event.target === decimalPlacesEl) return;

    const key = event.key;

    if (/^[0-9]$/.test(key)) {
      event.preventDefault();
      inputDigit(key);
      return;
    }
    if (key === ".") {
      event.preventDefault();
      inputDigit(".");
      return;
    }
    if (key === "+" || key === "-" || key === "*" || key === "/") {
      event.preventDefault();
      chooseOperator(key);
      return;
    }
    if (key === "(") {
      event.preventDefault();
      inputOpenParen();
      return;
    }
    if (key === ")") {
      event.preventDefault();
      inputCloseParen();
      return;
    }
    if (key === "Enter" || key === "=") {
      event.preventDefault();
      evaluate();
      return;
    }
    if (key === "Escape") {
      event.preventDefault();
      clearAll();
      return;
    }
    if (key === "Backspace") {
      event.preventDefault();
      backspace();
    }
  });

  window.addEventListener("resize", () => {
    fitDisplay();
  });

  state.decimalPlaces = Number(decimalPlacesEl.value) || 2;
  clearAll();
})();
