# Follow-up Answers

Answers to the Nucleus Security Engineering Intern assessment Gist questions.  
AI records: [`AI_USAGE.md`](AI_USAGE.md), [`AI_PROMPT_TRANSCRIPT.md`](AI_PROMPT_TRANSCRIPT.md), [`AI_FULL_INTERACTIONS.md`](AI_FULL_INTERACTIONS.md).  
Webhook review: [`CODE_REVIEW.md`](CODE_REVIEW.md).

Personal verification notes below state only what the conversation record supports. Where a personal action was not established, that limitation is written plainly.

---

## Code Review

### 1. Share your prompts and the AI outputs.

I used **Cursor** for the webhook review and the calculator. ChatGPT also helped review and draft some submission/editorial wording (assessment instructions and polishing), which is disclosed in `AI_USAGE.md` / `AI_PROMPT_TRANSCRIPT.md` rather than hidden.

Work went through these stages (same order as the transcript):

1. Master brief — review + calculator + docs  
2. Independent audit — Overflow / long-result defects  
3. Expression display + decimal-places rounding  
4. Parentheses  
5. Equals debugging (stale Flask process)  
6. Follow-up answers currency check  
7. Interview-style docs polish  
8. Precision fix — destructive 16-digit `format_result`  
9. Public-repo cleanup — `1e50` magnitude/quantize consistency  
10. Pre-submission technical review — webhook SQLite realism, auth vs authz, precision cases, parser/tests, merge priorities (docs/understanding; no calculator rewrite)  
11. Submission-completeness documentation  
12. Final AI disclosure recovery into `AI_FULL_INTERACTIONS.md` (this packaging pass)

Original candidate prompts for this Cursor assessment session are recovered verbatim in `AI_FULL_INTERACTIONS.md` (31 interactions from the local agent JSONL). User-visible AI text is included with tool JSON omitted. `AI_PROMPT_TRANSCRIPT.md` is the short index. ChatGPT drafting chats were **not** found in accessible Cursor archives and are not reproduced as verbatim transcripts.

Cursor drafted `CODE_REVIEW.md` and most of the implementation. I treat that as material to verify against the Gist and tests, not as automatically correct.

### 2. For each prompt

#### Prompt 1 — Master assessment brief

- **Hoped:** End-to-end take-home against the official Gist: Python webhook review, Flask + HTML/CSS/JS calculator, pytest, AI disclosure docs; no fabricated personal claims; no auto push/email.  
- **Actually did:** Produced `CODE_REVIEW.md`, the calculator stack, initial README/follow-ups, and an early pytest suite (agent-reported ~30 passed at that stage).  
- **Re-prompt?** Not immediately for the same task — later prompts were audits, features, and docs.  
- **Approach change:** Kept the vendor digest as `SHA256(secret + body)` and treated HMAC as a vendor-side suggestion only.

#### Prompt 2 — Independent audit

- **Hoped:** Find real defects, not style nits; fix only MUST FIX items.  
- **Actually did:** Found Overflow → HTTP 500 and over-long `1/7` results that broke chaining; patched `calculator.py` and added regressions (suite moved to ~33 passed then).  
- **Re-prompt?** Yes — this was a corrective pass after the first happy-path build.  
- **Approach change:** Probe failure modes (magnitude, result length) instead of trusting green happy-path tests alone.

#### Prompt 3 — Expression display + decimal rounding

- **Hoped:** Show the full expression until `=`; conventional precedence; decimal-places control with display-only rounding.  
- **Actually did:** Restricted tokenizer + shunting-yard (no `eval`); `format_rounded` with `ROUND_HALF_UP`; `/api/format`; frontend expression state.  
- **Re-prompt?** No failure re-prompt — this was a new requirement.  
- **Approach change:** Separate **working** `result` from rounded `display` so chaining and re-rounding stay accurate.

#### Prompt 4 — Parentheses

- **Hoped:** Add `(` / `)` without rebuilding the app.  
- **Actually did:** Nested parentheses in parser/UI; mismatch cases tested; keypad + keyboard.  
- **Re-prompt?** Short follow-up only (“braket” typo in the original ask).  
- **Approach change:** Incremental feature on the existing parser, not a rewrite.

#### Prompt 5 — Equals not showing

- **Hoped:** Fix a broken equals path.  
- **Actually did:** Live HTTP still returned the old binary-only API error (`Missing a, b, operator`), proving a **stale Flask process** on port 5000. Restarting fixed it; frontend incomplete-expression feedback improved.  
- **Re-prompt?** Debugging, not a calculator rewrite.  
- **Approach change:** When UI and tests disagree, check the live process before rewriting logic.

#### Prompt 6 — Follow-up currency

- **Hoped:** Confirm follow-ups matched latest features.  
- **Actually did:** Updated factual sections for expression/rounding/parens.  
- **Re-prompt?** Docs-only.  
- **Approach change:** Treat follow-ups as living with the code.

#### Prompt 7 — Interview docs polish

- **Hoped:** Clearer hiring-manager writing and honest AI attribution.  
- **Actually did:** Tightened follow-ups and AI disclosure; agent-run pytest reported 62 passed at that checkpoint.  
- **Re-prompt?** Editorial.  
- **Approach change:** Separate evidence (tests, HTTP) from personal feelings; avoid inventing unverified personal claims.

#### Prompt 8 — Precision fix (16-digit reduction)

- **Hoped:** Stop display rounding from operating on a shortened working value.  
- **Actually did:** Reproduced `100000000000000.005` → wrong display via old `format_result`; fixed with explicit `localcontext` / `WORKING_PREC=50` working serialization; display-only `ROUND_HALF_UP`; regression tests (70 passed at that commit).  
- **Re-prompt?** Single engineering gate.  
- **Approach change:** Never serialize away precision that later maths or display rounding still need.

#### Prompt 9 — Cleanup / `1e50` boundary

- **Hoped:** Employer-facing repo hygiene + consistent numeric range.  
- **Actually did:** Tightened magnitude so values like `1e50` cannot parse while failing at quantize; added regression; moved private submission drafts out of the public tree; synced docs. Suite at **72 passed** (`py -3 -m pytest -q`, Python 3.14.3, Cursor agent environment).  
- **Re-prompt?** Continuation of the evidence-first cleanup brief.  
- **Approach change:** Prefer a consistent supported range over a parse that cannot display-round within `WORKING_PREC`.

#### Prompt 10 — Pre-submission technical review (this conversation)

- **Hoped:** Confirm I understand webhook SQLi under Python’s SQLite driver, auth vs authz for `role`, vendor SHA256 vs HMAC, working vs display precision, restricted parsing, test vs live-process coverage, and merge-blocker severity—without unnecessary rewrites.  
- **Actually did:** Agent re-ran pytest (**72 passed**); spot-checked precision/expression cases; confirmed frontend chains from API `result` not `display`; reproduced single-statement SQLite injection shaping (including forcing `admin`); concluded calculator needs **no** code change for submission; enriched `CODE_REVIEW.md` impact wording with that concrete SQLite behaviour.  
- **Re-prompt?** Understanding / verification, not a feature rebuild.  
- **Approach change:** Prefer realistic driver impact and “change only if wrong” over looking more advanced.

**Implementation facts (current code):** 50-significant-digit working precision; explicit local Decimal contexts; no destructive 16-digit working serialization; display-only `ROUND_HALF_UP`; precision regressions; restricted expression evaluation (no `eval`); magnitude capped for roundability (`MAX_ABS_ADJUSTED_EXPONENT = 41`).

**Pytest verification (conversation record):** Automated results cited here were produced in the **Cursor agent** environment (`py -3 -m pytest -q` → 72 passed). This record does **not** establish that I separately re-ran the suite myself outside that environment.

**Browser verification (conversation record):** This record does **not** establish a personal browser click-through of the calculator after the precision/cleanup fixes. Keypad/UX behaviour remains covered by design and API tests, not by a documented candidate E2E session.

---

## Coding Challenge

### 1. How far were you able to get?

Functional web calculator: expression display, `+ − × ÷`, decimals/negatives, parentheses, precedence, AC/backspace/±, division-by-zero handling, decimal-places control (default 2, `ROUND_HALF_UP` for **display**), Flask APIs `/api/calculate` and `/api/format`, pytest (**72** in Cursor agent runs). Webhook review in `CODE_REVIEW.md`.

**Gist minimum** = frontend + backend calculator. Expression UI, precedence, parentheses, and rounding are **enhancements**. No automated browser E2E. One-hour completion is **not** claimed.

### 2. What challenges did you encounter?

- Stale Flask process: browser ≠ code under test  
- Separating working Decimal precision from display rounding (including fixing destructive 16-digit reduction in `format_result`, then aligning magnitude limits with quantize)  
- Safe expression evaluation without `eval`  
- Webhook review: SQLi impact without overstating SQLite multi-statement exploits; HMAC vs vendor contract  

**Hardest challenge (evidence-limited):** The conversation record does not include a separate personal ranking of which challenge “felt” hardest. The issues that required the most corrective engineering attention in the project were (1) environment drift (stale Flask vs green tests) and (2) keeping working Decimal serialization honest for display rounding and chaining.

### 3. If you were given unlimited time, what additional functionality would you include?

Browser E2E (e.g. Playwright), CI, and basic public-deploy hardening—not accounts/databases/scientific mode.

### 4. If you used AI: prompts; what it did well; poorly; how prompting changed

Prompts/outputs: `AI_FULL_INTERACTIONS.md` (verbatim recovered Cursor prompts + user-visible AI text), indexed by `AI_PROMPT_TRANSCRIPT.md`, summarised in `AI_USAGE.md`. ChatGPT contributed to reviewing/drafting some submission material earlier; those ChatGPT chats are **not** in the recovered Cursor JSONL.

**Well:** Fast structure from the Gist; line-referenced review; thin Flask over testable `calculator.py`; incremental features without `eval`; useful when asked for realistic SQLite impact and “do not rewrite if correct.”

**Poorly:** Happy-path bias (Overflow / precision reduction / `1e50` quantize edge needed audits); environment blindness (stale server); early docs sounded like generic reports; incomplete in-repo transcript export even though chat history still exists in Cursor.

**Changed approach:** Narrower prompts (audit vs feature vs docs vs understanding); when equals failed, verify live HTTP instead of rewriting the app; fix precision by separating working serialization from display rounding and keeping the numeric range consistent with display quantize; document attribution and evidence explicitly.

**Next AI-assisted take-home (from evidenced approach, not invented feelings):** Start earlier with failure-mode and process checks; keep agent-run pytest clearly labelled as agent-run until I personally re-run or browser-check when I need to defend the work; ask for realistic severity (e.g. SQLite `execute` vs stacked-statement myths) before changing code.

---

## Additional thoughts (optional for email)

This exercise combined reviewing untrusted input handling with building a small, testable service. AI accelerated drafts; judgement still matters for contracts, precision, and verifying the process you think is running. The pre-submission review reinforced that multi-statement `DROP TABLE` claims are often overstated for Python’s SQLite `execute`, while single-statement injection and role trust remain real merge blockers—and that the calculator’s working-vs-display design did not need further complexity for this assessment.
