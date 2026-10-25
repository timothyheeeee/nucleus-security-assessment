# AI Prompt / Output Transcript (Recoverable Record)

This file supports the Nucleus assessment requirement to share AI prompts and outputs.

## Honesty constraints

- **Verbatim status:** Most historical Cursor prompts/outputs are **NOT RECOVERABLE** as full text in this repository (chat was not exported byte-for-byte). Entries below are annotated summaries tied to artefacts—not labelled “verbatim” unless quoted.
- ChatGPT also helped draft some editorial / assessment instruction text for the candidate; that is AI assistance and is disclosed here rather than hidden.
- No secrets/tokens from `gh` login are recorded in these markdown files.

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

## Prompt 8 — Evidence-first final engineering pass (this session)

**Prompt text status:** NOT RECOVERABLE as a full paste here without dumping the entire user message; the instruction lived in the Cursor chat titled along the lines of “Nucleus Security assessment — evidence-first final engineering pass”. Goal excerpt: fix destructive 16-digit `format_result` reduction; use `localcontext`; add regression tests; refine webhook review accuracy; honest AI provenance; no commit/push/email.

**Outcome (verified artefacts):**

- Reproduced: `format_rounded(100000000000000.005, 2)` via old `format_result` path → `100000000000000` (wrong).  
- Fixed: working serialization preserves fraction; display rounding → `100000000000000.01`.  
- `localcontext(WORKING_CONTEXT)` for parse/arithmetic/format; thread consistency test.  
- pytest: **70 passed**.  
- `CODE_REVIEW.md` impact wording tightened (SQLite execute / connection close / HMAC).  
- Docs/email draft updated; `FINAL_AUDIT_REPORT.md` added.

**Re-prompt?** N/A (single engineering gate).  
**Classification:** Defect fix + compliance documentation (not a new calculator feature).

---

## How to give Nucleus the “full” prompts

1. Point reviewers to this file + `AI_USAGE.md`.  
2. If they need unabridged chats, export from Cursor (candidate action)—this repo does **not** currently contain a complete verbatim dump.  
3. Do not claim full compliance with “all prompts and outputs” beyond what is recoverable above.
