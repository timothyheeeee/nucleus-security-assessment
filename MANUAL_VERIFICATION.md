# Manual verification checklist (candidate)

Automated tests (`pytest`) do **not** prove the browser UI works. Complete this once before emailing Nucleus.

## Setup

```powershell
cd c:\Users\Timothy\Desktop\security\nucleus-security-assessment
.\.venv\Scripts\Activate.ps1
python app.py
```

Open http://127.0.0.1:5000/ (hard-refresh with Ctrl+F5 if the page was already open).

## Calculator checks

| # | Action | Expected |
|---|--------|----------|
| 1 | `1` `+` `2` then `=` | Display shows `1 + 2` before equals; then `3` |
| 2 | `1` `0` `+` `5` `×` `2` then `=` | `20` (not 30) |
| 3 | `(` `1` `0` `+` `5` `)` `×` `2` then `=` | `30` |
| 4 | Decimal places = 2; `1` `0` `÷` `3` then `=` | `3.33` |
| 5 | Change decimal places to 4 (without re-entering) | Becomes `3.3333` |
| 6 | `8` `÷` `0` then `=` | Error shown; app does not crash |
| 7 | `AC` | Display `0` |
| 8 | After a result, press a digit | Starts a new expression |
| 9 | After a result, press `+` then a number then `=` | Continues from prior high-precision result |

Tick when done: [ ]

## Docs / AI disclosure

| # | Check | Done |
|---|--------|------|
| 1 | Replace every `[CANDIDATE TO CONFIRM …]` in `FOLLOW_UP_ANSWERS.md` with your own sentence | [ ] |
| 2 | Skim `CODE_REVIEW.md` so you can defend SQL injection / upsert / secret / role findings | [ ] |
| 3 | Confirm `AI_USAGE.md` / `AI_PROMPT_TRANSCRIPT.md` match how you actually used Cursor | [ ] |
| 4 | Paste public GitHub URL into `SUBMISSION_EMAIL_DRAFT.md` | [ ] |

## Do not claim

- That Cursor-run pytest equals “I personally tested everything”
- That the work took ≤1 hour unless that is true for you
- That Decimal results are infinitely exact
