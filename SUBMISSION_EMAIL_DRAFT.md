# Submission email draft — COPY MANUALLY (DO NOT AUTO-SEND)

**Status:** Local draft only. Fill placeholders, then copy into your email client yourself.  
**Do not** ask Cursor/agents to send this via Gmail, Outlook, SMTP, or any API.

Replace before sending:

- `[Your Name]`
- `[Your email]`
- `REPLACE_WITH_PUBLIC_REPO_URL`
- Every `[CANDIDATE TO CONFIRM …]` block with your own one-sentence answer (delete the marker text)

---

**Subject:** Nucleus Security Engineering Intern Assessment — [Your Name]

Hi,

Thank you for the opportunity to complete the Engineering Intern technical assessment.

Below are my answers to the follow-up questions from the assessment Gist. The full project—including the Python webhook code review, calculator application, tests, and AI prompt records—is in this public repository:

**GitHub:** `REPLACE_WITH_PUBLIC_REPO_URL`

I reviewed the **Python** webhook (not PHP).

---

## Code review follow-ups

### 1. Share your prompts and the AI outputs.

I used **Cursor** for the webhook review and the calculator. Work proceeded in several focused prompts (initial assessment brief; independent audit; expression display + decimal rounding; parentheses; debugging a stale Flask process; documentation polish). I asked Cursor to draft the review and implementation, then treated that output as something to verify against the official Gist and against tests—not as automatically correct.

Recoverable prompt/output records: `AI_USAGE.md` and `AI_PROMPT_TRANSCRIPT.md` in the repository. Long verbatim Cursor transcripts remain in the Cursor chat history; the markdown files summarise what can be recovered without inventing missing text. Code review comments: `CODE_REVIEW.md`.

### 2. For each prompt

**What I hoped AI would accomplish**  
For the code review: a PR-style critique of production risk (signatures, SQL, upsert, secrets, role writes)—not style nits. For the calculator: a small Flask + HTML/CSS/JS app I could run and test locally, without `eval` or a heavy framework. Later prompts requested expression display, precedence, rounding controls, and brackets.

**What it actually did**  
Produced `CODE_REVIEW.md` with line-referenced findings on the Gist Python snippet (copy under `review_subject/original_webhook.py`): SQL injection via f-strings, insert-only “upsert”, vendor-controlled `role`, default `"dev-secret"`, plus medium issues such as non-constant-time compare. It treated `SHA256(secret + body)` as the vendor contract and discussed HMAC only as a possible protocol change. For the calculator it built Decimal-based maths, validation, pytest coverage, then a restricted expression evaluator (precedence + parentheses) and display-only rounding. Latest automated run in the project environment: **62 passed**, 0 failed, 0 skipped (`python -m pytest -q`).

**Did I have to re-prompt?**  
Yes, but not always because the first answer was “wrong.” Windows needed `py -3`/venv because `python` hit the Store stub. An audit pass found uncaught `decimal.Overflow` (HTTP 500) and over-long division results that broke re-entry—fixed with regression tests. Expression UI, rounding, and parentheses were **feature follow-ups**. When `=` looked broken, an old Flask process on port 5000 was still serving the pre-expression API; restarting fixed it.

`[CANDIDATE TO CONFIRM — Q2 re-prompt]` Replace this line with one sentence: whether *you* personally ran pytest/browser/server restart, or only reviewed Cursor’s reports.

**If the approach changed, why?**  
I did not treat missing HMAC as an implementation bug—the Gist specifies `SHA256(secret + body)`. Unilaterally switching would break vendor compatibility. Safer comparison and no guessable default secret still matter. On the calculator, moving to a restricted expression model (not `eval`) was driven by needing visible expressions and precedence.

`[CANDIDATE TO CONFIRM — Q2 approach]` Replace this line with one sentence on which trade-off mattered most to you.

---

## Coding challenge follow-ups

### 1. How far were you able to get?

Working calculator: expression display until `=`, Flask APIs (`/api/calculate`, `/api/format`), four operations, decimals/negatives, AC/backspace/±, parentheses, precedence (`10 + 5 × 2` → 20; `(10 + 5) × 2` → 30), decimal-places control (default 2, `ROUND_HALF_UP` for display), pytest (**62**), plus `CODE_REVIEW.md`. The Gist only requires a calculator; expression/precedence/parens/rounding are enhancements. Not claimed: automated browser E2E, or one-hour completion.

`[CANDIDATE TO CONFIRM — browser]` Replace with what you personally clicked in the browser (or say you still need to).

### 2. What challenges did you encounter?

Matching a longer working prompt to the official Gist; separating Decimal working-precision results from rounded display; evaluating expressions without `eval`; diagnosing a stale Flask process when tests were green but the browser failed; prioritising SQLi/authz over cosmetics and not “upgrading” the vendor signature scheme incorrectly.

`[CANDIDATE TO CONFIRM — challenges]` Replace with what felt hardest for you personally.

### 3. If you had unlimited time?

Browser smoke tests (Playwright/Cypress) and basic public-deployment hardening. I would not add accounts, databases, or a full scientific mode.

### 4. AI: what it did well / poorly / how prompts changed

**Well:** Fast structure from a clear Gist; line-referenced webhook defects (especially f-string SQL); thin Flask over testable `calculator.py`; incremental features without `eval`/heavy frameworks.

**Poorly (concrete):** (1) Green pytest while the browser hit a stale server; (2) happy-path bias until an audit probed Overflow / long results; (3) early follow-up drafts sounded like generated reports; (4) full agent transcripts are not fully inlined in-repo.

**How approach changed:** Narrower follow-up prompts (audit vs feature vs docs); when equals failed, verify the live API instead of rebuilding; document attribution and evidence explicitly.

`[CANDIDATE TO CONFIRM — AI reflection]` Replace with what you will do differently next take-home.

---

## Additional thoughts

`[CANDIDATE TO CONFIRM — optional thoughts]` One or two sentences, or delete this section.

---

Best regards,  
[Your Name]  
[Your email]

---

## Reminder (not part of the email)

1. Fill all confirm markers above.  
2. Complete `MANUAL_VERIFICATION.md`.  
3. Commit, push to a **public** repo, paste the URL.  
4. Copy this email yourself—do not ask an agent to send it.
