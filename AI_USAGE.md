# AI Usage Record

Nucleus encourages AI use and asks candidates to share prompts and reflect on them.  
This file is the **high-level map**. The chronological recoverable record is in [`AI_PROMPT_TRANSCRIPT.md`](AI_PROMPT_TRANSCRIPT.md).  
Long verbatim Cursor transcripts are **not** fully duplicated in-repo; they remain in the Cursor chat history.

## Tooling

| Item | Value |
|------|--------|
| Environment | Cursor IDE |
| Assistant | Cursor agent (in-product label: Auto / Composer-family) |
| Model ID | Not independently confirmed beyond the product UI — do not invent a vendor model name |
| Official assessment | [Gist `642cf8247c11e7a34bb03e318af549b4`](https://gist.github.com/zlee-nucleussec/642cf8247c11e7a34bb03e318af549b4) |

## How AI was used (accurate attribution)

| Work | Who did what |
|------|----------------|
| Official Gist retrieval & parsing | Cursor tools |
| Webhook `CODE_REVIEW.md` draft | Cursor-generated; findings map to Gist line numbers in `review_subject/original_webhook.py` |
| Calculator implementation | Cursor-generated under candidate-specified constraints (Flask, no `eval`, pytest, later expression/rounding/parens) |
| Automated tests execution | Run in Cursor’s shell against the project venv — **not** automatically the same as candidate-run tests |
| Browser click-through | **Not automated**; requires candidate confirmation |
| Follow-up prose for “what I personally felt” | Must be completed by the candidate (`[CANDIDATE TO CONFIRM]` in `FOLLOW_UP_ANSWERS.md`) |
| Stale Flask diagnosis | Live HTTP returned old API error body; fixed by restarting process |

## Prompt sequence (summary)

1. **Master brief** — assessment end-to-end (review + calculator + docs)  
2. **Audit** — find/fix MUST FIX defects (Overflow, long-result chaining)  
3. **Enhancement** — expression display, precedence, decimal places  
4. **Enhancement** — parentheses  
5. **Debug** — equals / stale server  
6. **Docs** — sync follow-ups; then hiring-manager polish + disclosure  

Feature prompts (3–4) are **new requirements**, not “AI failed once so we yelled at it.”  
Audit (2) and stale-server (5) are **verification / environment** lessons.

## Latest verification (precision-fix / audit pass)

```text
Command: .\.venv\Scripts\python.exe -m pytest -q
Result:  70 passed, 0 failed, 0 skipped
```

Spot checks: `10 + 5 * 2` → `20`; `(10 + 5) * 2` → `30`; `format_rounded(10/3, 2)` → `3.33`;  
`100000000000000.005` at 2 places → `100000000000000.01` (working `result` retains `.005`).  
These runs were executed in the Cursor environment unless the candidate re-runs them personally.

## What AI did well

- Fast structure against a clear Gist  
- Security review tied to concrete lines (SQLi, fake upsert, secret default, role trust)  
- Testable split: `calculator.py` vs Flask routes  
- Incremental features without introducing `eval` or a large framework

## What AI did poorly (concrete, project-specific)

1. **Environment blindness:** green tests on new code while the browser still hit an old Flask process → equals looked broken.  
2. **Happy-path bias:** Overflow and over-long division results needed an explicit audit probe.  
3. **Interview writing:** early follow-up drafts sounded like generated status reports and blurred who verified what.  
4. **Archival:** full agent transcripts are not automatically a clean in-repo appendix unless exported.

## Lessons

Treat AI as a fast junior pair: specify constraints, verify against the official brief and running system, keep scope small, and separate **feature asks** from **bug fixes** from **ops mistakes**.
