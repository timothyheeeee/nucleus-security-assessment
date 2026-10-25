# AI Prompt / Output Transcript (Recoverable Record)

This file supports the Nucleus assessment requirement to share AI prompts and outputs.

## Honesty constraints

- **Source of truth for long verbatim text:** the Cursor chat session that produced this repository.  
- **This file:** structured, chronological recovery of what actually happened.  
- **Not fabricated:** where full agent token streams were not exported into the repo, that limitation is stated. Summaries below describe verified artefacts (files, tests, HTTP behaviour), not invented dialogue.

Tool: **Cursor** (agent labelled Auto / Composer-family in-product).  
Assessment Gist: https://gist.github.com/zlee-nucleussec/642cf8247c11e7a34bb03e318af549b4

---

## Prompt 1 — Master assessment brief

**When:** Start of the assessment session  

**Objective:** Complete the internship take-home: read Gist, Python webhook review, Flask calculator, tests, docs; no push/email without approval.

**Prompt text status:**  
The candidate pasted a long “MASTER CURSOR AGENT PROMPT / Nucleus Security…” message into Cursor.  
**Full verbatim text:** available in the Cursor chat transcript (too long to duplicate here without lossy truncation).  

**Recoverable constraints from that prompt (accurate paraphrase):**

- Prefer the official Gist over conflicting instructions  
- Review Python webhook only  
- Flask + HTML/CSS/vanilla JS + pytest calculator  
- `CODE_REVIEW.md`, `AI_USAGE.md`, follow-up drafts  
- No fabricated test results or personal reflections  
- Do not push/email automatically  

**AI output (artefacts produced — verified in repo):**

- `CODE_REVIEW.md`  
- Calculator: `app.py`, `calculator.py`, `templates/`, `static/`, `tests/`  
- `README.md`, initial `FOLLOW_UP_ANSWERS.md`, `.gitignore`, `requirements.txt`  
- pytest initially reported **30 passed** in-session  

**Verification:** Automated tests and live HTTP smoke checks were run in Cursor’s environment (not assumed to be candidate-only).

**Classification:** Initial implementation + review generation (broad scope).

---

## Prompt 2 — Independent final audit

**Objective:** Staff-style audit; find real defects; fix MUST FIX only; no commit/push.

**Prompt text status:** Present in Cursor chat as the “Prompt 2 / final engineering and security audit” message (full text in chat).

**AI output (verified):**

- Confirmed Overflow → HTTP 500 and long `1/7` results breaking chaining  
- Patched `calculator.py`; added regression tests  
- Suite moved to **33 passed** at that time  

**Classification:** **Verification / corrective** (defects found by probing, then fixed)—not a new product feature.

---

## Prompt 3 — Expression display + decimal rounding

**Objective:** Show full expression until `=`; precedence for chains; decimal-places dropdown (default 2); round display only; keep exact value for further maths / re-rounding.

**Prompt text status:** Full enhancement brief in Cursor chat.

**AI output (verified in code):**

- Restricted tokenizer + shunting-yard in `calculator.py` (no `eval`)  
- `format_rounded` with `ROUND_HALF_UP`  
- API: expression body + `/api/format`  
- Frontend expression state + precision select  
- Tests expanded  

**Classification:** **Feature enhancement** (new requirements), not a failed first-build re-prompt.

---

## Prompt 4 — Parentheses

**Objective:** Add `(` / `)` without rebuilding the app.

**Prompt text status:** Short follow-up in Cursor chat (“need to add braket options too”).

**AI output (verified):**

- Parentheses in tokenizer / evaluator; nested and mismatch cases tested  
- Keypad + keyboard handlers  
- Implicit multiplication `2(3+1)` supported server-side  

**Classification:** **Feature enhancement**.

---

## Prompt 5 — Equals not showing answer

**Objective:** Diagnose UI equals failure.

**What happened (verified):**

- Live `POST /api/calculate` with `{expression, decimal_places}` returned  
  `400 {"error":"Missing required field(s): a, b, operator"}`  
- That response matches the **pre-expression** API, proving a **stale Flask process** still owned port 5000  
- Killing listeners and restarting with current `app.py` restored  
  `{"result":"3","display":"3"}` for `1 + 2`  

**Classification:** **Environment / process debugging**, not an AI logic rewrite of the calculator.

Frontend also improved incomplete-expression feedback so silent no-ops are less likely.

---

## Prompt 6 — Follow-up answers currency check

**Objective:** Confirm whether `FOLLOW_UP_ANSWERS.md` matched the latest features; then update factual sections (candidate requested).

**Classification:** Documentation sync (no calculator rebuild).

---

## Prompt 7 — Advanced interview submission optimisation (this pass)

**Objective:** Rewrite follow-ups for hiring-manager clarity, accurate AI attribution, evidence-based claims; re-verify tests; improve AI disclosure docs.

**Verification this pass:**

```text
.\.venv\Scripts\python.exe -m pytest -q
62 passed in 0.39s
```

Also confirmed in code/runtime: no `eval(`, precedence `10+5*2→20`, parentheses `(10+5)*2→30`, rounding `10/3` → `3.33` at 2 places.

**Classification:** Documentation / communication improvement.

---

## How to give Nucleus the “full” prompts

1. Attach or point to this file + `AI_USAGE.md` in the repo.  
2. If they want unabridged Cursor transcripts, export/share the chat from Cursor (candidate action).  
3. Do **not** claim this markdown file contains every agent token; it contains the recoverable engineering record.
