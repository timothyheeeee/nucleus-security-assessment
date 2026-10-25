# Follow-up Answers

Answers to the Nucleus Security Engineering Intern assessment Gist questions.  
AI records: [`AI_USAGE.md`](AI_USAGE.md), [`AI_PROMPT_TRANSCRIPT.md`](AI_PROMPT_TRANSCRIPT.md).  
Webhook review: [`CODE_REVIEW.md`](CODE_REVIEW.md).

Items marked `[PERSONAL CONFIRMATION]` need your own one-sentence confirmation before sending.

---

## Code Review

### 1. Share your prompts and the AI outputs.

I used **Cursor** for the Python webhook review and the calculator. Work proceeded in stages (initial build/review, audit, expression + rounding, parentheses, stale-server debugging, documentation, and a final precision fix pass). Recoverable summaries and annotations are in `AI_USAGE.md` and `AI_PROMPT_TRANSCRIPT.md`.

**Limitation:** Full verbatim Cursor chat exports are largely **NOT RECOVERABLE** in-repo; those files summarise goals/outcomes and point to artefacts (code, tests). I am not claiming a complete token-level transcript dump.

Cursor drafted `CODE_REVIEW.md` and most implementation; I treat that as material to verify against the Gist and tests, not as automatically correct.

### 2. For each prompt

**Hoped for**  
Code review: high-signal PR feedback on SQL, signatures, upsert, secrets, and roles—not style nits—while respecting `SHA256(secret + body)`.  
Calculator: a small Flask + HTML/CSS/JS app with validation and tests, without `eval`. Later: expression display, precedence, rounding, parentheses.

**Actually did**  
Review findings (line-referenced): f-string SQL injection, false upsert, vendor-controlled roles, `"dev-secret"` fallback, non-constant-time compare, weak error handling. HMAC noted only as a possible **vendor** change.  
Calculator: Decimal arithmetic with explicit working context (50 significant digits), display rounding separate from working `result`, restricted expression parser, pytest suite. Latest agent-run: **70 passed** (`python -m pytest -q`).

**Re-prompt?**  
Yes—for environment (`py -3`/venv), an audit that found Overflow / long-result issues, feature asks (expression/rounding/parens), diagnosing a **stale Flask process** on port 5000 (tests green, browser hitting old API), and a later precision bug where `format_result` reduced values to 16 significant digits before display rounding.

**Approach changes**  
Do not “fix” the vendor digest algorithm to HMAC. Prefer `hmac.compare_digest` for comparing the existing digest. For maths, keep a **working-precision** serialization for chaining and apply user decimal places only to `display`.

`[PERSONAL CONFIRMATION]` Did you personally re-run pytest or only review Cursor’s reported results?

`[PERSONAL CONFIRMATION]` Did you personally click the calculator in a browser after the precision fix?

---

## Coding Challenge

### 1. How far were you able to get?

Functional web calculator: expression display, `+ − × ÷`, decimals/negatives, parentheses, precedence, AC/backspace/±, division-by-zero handling, decimal-places control (default 2, `ROUND_HALF_UP` for **display**), Flask APIs `/api/calculate` and `/api/format`, pytest (**70**). Webhook review in `CODE_REVIEW.md`.

**Gist minimum** = FE + BE calculator. Expression UI, precedence, parentheses, and rounding are **enhancements**. No automated browser E2E. One-hour completion is **not** claimed.

### 2. What challenges did you encounter?

- Stale Flask process: browser ≠ code under test  
- Separating working Decimal precision from display rounding (including fixing destructive 16-digit reduction in `format_result`)  
- Safe expression evaluation without `eval`  
- Webhook review: SQLi impact without overstating SQLite multi-statement exploits; HMAC vs vendor contract  

`[PERSONAL CONFIRMATION]` Which challenge was hardest for you personally?

### 3. Unlimited time?

Browser E2E (e.g. Playwright), CI, and basic public-deploy hardening—not accounts/databases/scientific mode.

### 4. AI: prompts; well; poorly; how prompting changed

Prompts/outputs: `AI_USAGE.md`, `AI_PROMPT_TRANSCRIPT.md` (with NOT RECOVERABLE notes where verbatim text is missing).

**Well:** Fast structure from the Gist; line-referenced review; thin Flask over testable `calculator.py`; incremental features without `eval`.

**Poorly:** Happy-path bias (Overflow / precision reduction needed audits); environment blindness (stale server); early docs sounded like generic reports; incomplete in-repo transcript export.

**Changed approach:** Narrower prompts (audit vs feature vs docs); when equals failed, verify live HTTP instead of rewriting the app; fix precision by separating working serialization from display rounding; document attribution and evidence explicitly.

`[PERSONAL CONFIRMATION]` What will you do differently next AI-assisted take-home?

---

## Additional thoughts (optional for email)

This exercise combined reviewing untrusted input handling with building a small, testable service. AI accelerated drafts; judgement still matters for contracts, precision, and verifying the process you think is running.
