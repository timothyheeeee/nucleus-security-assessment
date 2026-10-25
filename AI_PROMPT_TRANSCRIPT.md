# AI Prompt / Output Transcript (Recoverable Record)

This file supports the Nucleus assessment requirement to share AI prompts and outputs.

## Honesty constraints

- **Export status:** Most historical Cursor prompts/outputs are **not checked into this repository as full verbatim dumps**. The original text for many interactions still exists in Cursor chat history for this project; absence from git is an **export gap**, not proof the text was destroyed.
- Entries below are annotated: paraphrase, summary, quoted fragment, or verified artefact. Nothing here invents verbatim text that was not recovered.
- **ChatGPT** also helped review and draft some editorial / assessment-instruction / submission wording for the candidate. That is AI assistance and is disclosed here rather than hidden. ChatGPT did not replace the Cursor-implemented calculator runtime.
- No secrets/tokens from `gh` login are recorded in these markdown files.

Tool: **Cursor** (agent labelled Auto / Composer-family in-product), plus **ChatGPT** for some submission drafting.  
Assessment Gist: https://gist.github.com/zlee-nucleussec/642cf8247c11e7a34bb03e318af549b4

---

## Prompt 1 — Master assessment brief

**When:** Start of the assessment session  

**Objective:** Complete the internship take-home: read Gist, Python webhook review, Flask calculator, tests, docs; no push/email without approval.

**Prompt text status:**  
The candidate pasted a long “MASTER CURSOR AGENT PROMPT / Nucleus Security…” message into Cursor.  
**Full verbatim text:** still present in Cursor chat history; **not** duplicated unabridged in this file (length / export choice).

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

**Prompt text status:** Present in Cursor chat as the “Prompt 2 / final engineering and security audit” message (full text in chat; not unabridged here).

**AI output (verified):**

- Confirmed Overflow → HTTP 500 and long `1/7` results breaking chaining  
- Patched `calculator.py`; added regression tests  
- Suite moved to **33 passed** at that time  

**Classification:** **Verification / corrective** (defects found by probing, then fixed)—not a new product feature.

---

## Prompt 3 — Expression display + decimal rounding

**Objective:** Show full expression until `=`; precedence for chains; decimal-places dropdown (default 2); round display only; keep exact value for further maths / re-rounding.

**Prompt text status:** Full enhancement brief in Cursor chat (not unabridged here).

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

**Prompt text status:** Short follow-up in Cursor chat. Recoverable quoted fragment: `need to add braket options too`.

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

## Prompt 7 — Advanced interview submission optimisation

**Objective:** Rewrite follow-ups for hiring-manager clarity, accurate AI attribution, evidence-based claims; re-verify tests; improve AI disclosure docs.

**Verification at that checkpoint:**

```text
.\.venv\Scripts\python.exe -m pytest -q
62 passed in 0.39s
```

Also confirmed in code/runtime: no `eval(`, precedence `10+5*2→20`, parentheses `(10+5)*2→30`, rounding `10/3` → `3.33` at 2 places.

**Classification:** Documentation / communication improvement.

---

## Prompt 8 — Evidence-first final engineering pass

**Prompt text status:** Long user message in Cursor chat (evidence-first final engineering pass). Goal excerpt (paraphrase): fix destructive 16-digit `format_result` reduction; use `localcontext`; add regression tests; refine webhook review accuracy; honest AI provenance; no commit/push/email.

**Outcome (verified artefacts):**

- Reproduced: `format_rounded(100000000000000.005, 2)` via old `format_result` path → `100000000000000` (wrong).  
- Fixed: working serialization preserves fraction; display rounding → `100000000000000.01`.  
- `localcontext(WORKING_CONTEXT)` for parse/arithmetic/format; thread consistency test.  
- pytest at that commit: **70 passed**.  
- `CODE_REVIEW.md` impact wording tightened (SQLite execute / connection close / HMAC).  

**Re-prompt?** N/A (single engineering gate).  
**Classification:** Defect fix + compliance documentation (not a new calculator feature).

---

## Prompt 9 — Final repository cleanup and consistency audit

**Prompt text status:** Long user message in Cursor chat (“FINAL REPOSITORY CLEANUP AND SUBMISSION CONSISTENCY AUDIT”). Not pasted unabridged here; constraints paraphrased accurately below.

**Recoverable constraints (paraphrase):**

- Keep employer-facing deliverables public; move private email/audit/checklist files outside the git tree  
- Synchronise AI disclosure across docs; expand follow-ups prompt-by-prompt  
- Investigate `1e50` parse-vs-quantize boundary; scoped fix + regression  
- Create private `SUBMISSION_EMAIL_FINAL.md`; no commit/push/email without approval  

**AI output (verified this pass):**

- Magnitude cap aligned with display quantize budget (`MAX_ABS_ADJUSTED_EXPONENT = 41`)  
- Regression: `1e50` rejected consistently; near-limit `1e40` still roundable  
- Private copies under sibling `nucleus-submission-private/`  
- Docs updated; agent-run pytest: **72 passed** (`py -3 -m pytest -q`, Python 3.14.3)  

**Classification:** Cleanup + boundary fix + documentation sync.

---

## Prompt 10 — Pre-submission technical review (genuine new conversation)

**When:** After the cleanup commit (`74810ec`) was already on GitHub; before email send.  

**Prompt text status:** Full user message present in Cursor chat. Recoverable structure and intent below; not every paragraph is duplicated here (length). This entry is **new** relative to prompts 1–9 and must not be backdated as an earlier project stage.

**Recoverable user intent (accurate paraphrase of the real prompt):**

1. Webhook: explain attacks actually possible with Python’s SQLite driver (not generic SQLi); check auth vs authz for `role`; confirm vendor `SHA256(secret + body)` should not be silently replaced with HMAC.  
2. Calculator precision: verify working (50 sig digits) vs display rounding on `0.1+0.2`, `1/7` then `×7`, `100000000000000.005` @ 2 places, large/small values, reuse of prior results; smallest fix only if genuine problem.  
3. Expression evaluation: check tokenizer, precedence, negatives, parentheses; remaining edge cases for a small calculator.  
4. Testing: explain unit vs integration vs manual browser coverage given the stale-Flask incident; run pytest and report actual output; do not claim tests as personally executed by the candidate.  
5. Code review prioritisation: which findings block merge; distinguish confirmed defects from assumptions.  
6. Final assessment: valid vs overstated concerns; what to change vs unnecessary complexity; trade-offs before rewriting.  
Constraints: no push/email without permission; keep a genuine record of this discussion; do not present it as something that happened earlier.

**AI output (summary of the actual response — full prose remains in Cursor chat):**

- SQLite `execute`: multi-statement `DROP TABLE` often overstated; single-statement injection still real (local demo: `ignored', 'admin');--` inserted admin; expression/subquery forms can shape values).  
- Auth ≠ authz for vendor `role` — approach confirmed.  
- Keep vendor digest; use `compare_digest` for comparison only — approach confirmed.  
- Precision design confirmed correct; frontend reuses API `result` (`exactResult`), not rounded `display`; `1/7*7` stays finite `0.999…`; no calculator rewrite recommended.  
- Parser appropriate; rejects `eval`-style input; sci-notation tokens not supported (acceptable for keypad calculator).  
- Tests cover calculator/API; browser/process drift still needs live checks.  
- Merge blockers: SQLi, secret default, fake upsert, uncontrolled roles.  
- Agent pytest: **72 passed** (`py -3 -m pytest -q`).  

**Code change from that review:** none to the calculator. Later submission-completeness pass added the concrete SQLite example into `CODE_REVIEW.md` and documented this prompt as Prompt 10.

**Classification:** Understanding / verification conversation (not a feature rebuild).

---

## Prompt 11 — Final submission-completeness pass (this update)

**Objective:** Reflect Prompt 10 in public docs; resolve former `[PERSONAL CONFIRMATION]` slots with evidence-limited statements only; refresh private email draft; no commit/push/email without approval.

**Classification:** Documentation / submission hygiene.

---

## ChatGPT (submission drafting)

**Role:** Secondary AI used to review/draft assessment instruction text and help polish submission wording.  
**Not claimed:** ChatGPT did not author the live calculator implementation in this repository.  
**Status:** Exact ChatGPT chat exports are **not** included in this repo unless the candidate pastes them later.

---

## How to give Nucleus the “full” prompts

1. Point reviewers to this file + `AI_USAGE.md` + `FOLLOW_UP_ANSWERS.md`.  
2. If they need unabridged Cursor chats, export from Cursor (candidate action)—this repo documents recoverable content and artefacts, not a complete dump.  
3. Do not claim full token-level compliance beyond what is recoverable above.
