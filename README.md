# Nucleus Security — Engineering Intern Assessment

Full-stack calculator web app and Python webhook code review for the Nucleus Security Software Engineering Intern (Australia) technical assessment.

## Summary

This repository contains:

1. **Code review** of the assessment’s Python webhook (`CODE_REVIEW.md`)
2. **Calculator application** — Flask backend + HTML/CSS/vanilla JS frontend
3. **Automated tests** (pytest)
4. **AI usage transparency** (`AI_USAGE.md`, `AI_PROMPT_TRANSCRIPT.md`)
5. **Follow-up answers** (`FOLLOW_UP_ANSWERS.md`)

Official assessment source: [Engineering Intern Interview Questions Gist](https://gist.github.com/zlee-nucleussec/642cf8247c11e7a34bb03e318af549b4)

## Technologies

- Python 3.11+ (developed/tested on Python 3.14)
- Flask
- HTML5 / CSS3 / vanilla JavaScript
- pytest
- `decimal.Decimal` for arithmetic (stdlib)

## Calculator features

**Implemented**

- Addition, subtraction, multiplication, division
- Full expression display in the main panel until `=` is pressed (e.g. `10 + 5 × 2`)
- Chained expressions with **conventional operator precedence** (`×`/`÷` before `+`/`−`)
- Parentheses `(` `)` including nested groups (e.g. `(10 + 5) × 2 = 30`)
- Integer and decimal operands
- Negative numbers and sign toggle (±)
- Clear (AC), backspace, equals
- **Decimal places** dropdown (0–8, default **2**) for final-result rounding only
- Server-side validation and division-by-zero handling
- Keyboard support (digits, operators, Enter, Escape, Backspace)
- Responsive layout suitable for mobile and desktop

**Interaction model**

- Digits and operators accumulate in the black display as a readable expression
- Equals evaluates the full expression on the Python backend (no `eval`)
- Changing an operator before entering the next number replaces the pending operator
- After a result, entering a digit starts a new expression; choosing an operator continues from the stored **working-precision** `result` (not the rounded `display` string)
- Changing decimal places after a result re-rounds that stored value via `/api/format` without recalculating the expression

**Precision policy (important)**

- Working arithmetic uses `decimal.localcontext` with **50 significant digits** (`WORKING_PREC`) — finite, not infinite exactness
- API `result` is a working-precision serialization (bounded length/magnitude)
- API `display` applies user decimal places with `ROUND_HALF_UP` on the full working value
- Numeric strings are capped (`MAX_NUMERIC_LENGTH = 64`); extreme exponents are rejected with JSON 400 errors

**Scope relative to the Gist**

- **Required by Gist:** a calculator with frontend + any needed backend  
- **Also in this repo (enhancements):** expression display, operator precedence, parentheses, decimal-places control, pytest suite, webhook code review + AI disclosure docs

## Setup

### Prerequisites

- Python 3.11 or newer
- On Windows, `py -3` is recommended if `python` opens the Store stub

### Installation

**Windows (PowerShell)**

```powershell
cd nucleus-security-assessment
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

**macOS / Linux**

```bash
cd nucleus-security-assessment
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Run the application

```powershell
python app.py
```

Then open: [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

The server binds to `127.0.0.1` with Flask debug mode **off** by default.

## Run tests

```powershell
python -m pytest -v
```

Latest agent-run suite: **70 passed**, 0 failed, 0 skipped (`python -m pytest -q`).

## API example

### Expression (preferred by the UI)

`POST /api/calculate`

```json
{
  "expression": "10 + 5 * 2",
  "decimal_places": 2
}
```

Success (`200`):

```json
{
  "result": "20",
  "display": "20"
}
```

`result` is the normalised high-precision value (used for further maths / re-rounding).  
`display` is rounded for the selected decimal places.

### Binary (still supported)

```json
{
  "a": "12.5",
  "b": "2",
  "operator": "*"
}
```

```json
{
  "result": "25"
}
```

### Re-round without recalculating

`POST /api/format`

```json
{
  "value": "0.3333333333333333",
  "decimal_places": 5
}
```

```json
{
  "display": "0.33333"
}
```

Error example (`400`):

```json
{
  "error": "Division by zero"
}
```

## Architecture

```
Browser (expression state + rounding preference)
    → POST /api/calculate { expression, decimal_places }
        → evaluate_expression() + format_rounded() in calculator.py
            → JSON { result, display }
    → POST /api/format { value, decimal_places }  (re-round stored high-precision result)
```

- **`calculator.py`** — binary ops, expression parser (shunting-yard), rounding
- **`app.py`** — HTTP validation only
- **Frontend** — builds the visible expression; never uses `eval`

## Security notes

- No `eval` / `exec` / shell for calculations
- Operands validated server-side (type, length, finiteness); booleans rejected
- Errors returned as JSON messages without Python tracebacks
- Display updates use `textContent` (not `innerHTML`)
- Minimal dependencies declared in `requirements.txt`

## Known limitations

- No browser end-to-end automation in CI — see [`MANUAL_VERIFICATION.md`](MANUAL_VERIFICATION.md)
- No scientific functions — only `+ − × ÷`, numbers, and parentheses
- `Decimal` precision is finite (configured working/display contexts); display rounding is separate
- Not a hardened production deployment (no TLS termination, rate limiting, or reverse proxy config)
- Frontend calculation always requires the backend (offline use not supported)
- Long expressions scroll horizontally inside the display; very long input is length-limited server-side
- Full verbatim Cursor chat transcripts are summarised in-repo; unabridged export is optional if reviewers request it

## Possible future improvements

- Playwright/Cypress smoke tests for keypad flows
- Optional history of the current session (in-memory only)
- Stronger HTTP hardening headers if deployed behind a public URL

## Related documents

| File | Purpose |
|------|---------|
| [`CODE_REVIEW.md`](CODE_REVIEW.md) | Python webhook PR review |
| [`AI_USAGE.md`](AI_USAGE.md) | AI assistance overview |
| [`AI_PROMPT_TRANSCRIPT.md`](AI_PROMPT_TRANSCRIPT.md) | Chronological recoverable prompt/output record |
| [`FOLLOW_UP_ANSWERS.md`](FOLLOW_UP_ANSWERS.md) | Answers to official follow-up questions |
| [`MANUAL_VERIFICATION.md`](MANUAL_VERIFICATION.md) | Browser checks for the candidate before submit |
| [`PERSONAL_CONFIRMATION_CHECKLIST.md`](PERSONAL_CONFIRMATION_CHECKLIST.md) | Private checklist (fill confirms; not required in email body) |
| [`SUBMISSION_EMAIL_DRAFT.md`](SUBMISSION_EMAIL_DRAFT.md) | Full email draft (copy/send manually) |
| [`FINAL_AUDIT_REPORT.md`](FINAL_AUDIT_REPORT.md) | Evidence-first audit report for this pass |
