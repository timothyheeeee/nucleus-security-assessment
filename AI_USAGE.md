# AI Usage Record

Nucleus encourages AI use and asks candidates to share prompts and reflect on them.  
This file is the **high-level map**. The chronological recoverable record is in [`AI_PROMPT_TRANSCRIPT.md`](AI_PROMPT_TRANSCRIPT.md).  
Follow-up answers that cite this work: [`FOLLOW_UP_ANSWERS.md`](FOLLOW_UP_ANSWERS.md).

Cursor chat history for this project still exists in the IDE. This repository documents recoverable paraphrases, quoted fragments, and verified artefacts. It does **not** claim a complete token-level export is checked into git. That is an export gap, not proof that the original text never existed.

## Tooling

| Item | Value |
|------|--------|
| Primary environment | Cursor IDE |
| Primary assistant | Cursor agent (in-product label: Auto / Composer-family) |
| Model ID | Not independently confirmed beyond the product UI — do not invent a vendor model name |
| Additional AI | ChatGPT — helped review and draft some assessment instruction / submission editorial text (not the live Flask calculator runtime) |
| Official assessment | [Gist `642cf8247c11e7a34bb03e318af549b4`](https://gist.github.com/zlee-nucleussec/642cf8247c11e7a34bb03e318af549b4) |

## How AI was used (accurate attribution)

| Work | Who did what |
|------|----------------|
| Official Gist retrieval & parsing | Cursor tools |
| Webhook `CODE_REVIEW.md` draft | Cursor-generated; findings map to Gist line numbers in `review_subject/original_webhook.py`; later enriched with concrete SQLite `execute` injection examples from the pre-submission review |
| Calculator implementation | Cursor-generated under candidate-specified constraints (Flask, no `eval`, pytest, later expression/rounding/parens/precision) |
| Automated tests execution | Run in Cursor’s shell (`py -3 -m pytest -q`) — **not** the same as a separately documented candidate-only run |
| Browser click-through | **Not** established in the conversation record after the precision/cleanup fixes |
| Pre-submission technical review | Candidate asked understanding questions; Cursor answered with code inspection, spot checks, and pytest; concluded no calculator rewrite |
| Stale Flask diagnosis | Live HTTP returned old API error body; fixed by restarting process |
| Submission / editorial drafting | Cursor + ChatGPT assisted; candidate owns final send |

## Prompt sequence (summary — matches transcript)

1. **Master brief** — assessment end-to-end (review + calculator + docs)  
2. **Audit** — find/fix MUST FIX defects (Overflow, long-result chaining)  
3. **Enhancement** — expression display, precedence, decimal places  
4. **Enhancement** — parentheses  
5. **Debug** — equals / stale server  
6. **Docs** — follow-up currency check  
7. **Docs** — hiring-manager polish + disclosure  
8. **Defect fix** — destructive 16-digit working serialization; `localcontext` / 50-digit working precision  
9. **Cleanup** — public/private file split; `1e50` magnitude vs quantize consistency; doc sync  
10. **Technical review** — SQLite realism, auth vs authz, precision cases, parser/tests, merge blockers; no unnecessary rewrite  

Feature prompts (3–4) are **new requirements**.  
Audit (2), stale-server (5), precision (8), magnitude (9), and review (10) are **verification / corrective / understanding** lessons.

## Latest verification (submission-completeness pass)

```text
Command: py -3 -m pytest -q
Python:  3.14.3
Result:  72 passed, 0 failed, 0 skipped
```

Spot checks (Cursor agent): `0.1 + 0.2` → `0.3`; `1/7` then `×7` → finite `0.999…` (not exact `1`);  
`100000000000000.005` @ 2 places → display `…01`, working keeps `.005`;  
`1e50` rejected; precedence/parens/`2*-3`; `__import__` rejected.  
These runs were executed in the Cursor environment. The conversation record does not establish a separate candidate-only pytest or browser E2E.

## What AI did well

- Fast structure against a clear Gist  
- Security review tied to concrete lines (SQLi, fake upsert, secret default, role trust)  
- Testable split: `calculator.py` vs Flask routes  
- Incremental features without introducing `eval` or a large framework  
- When asked, distinguished overstated multi-statement SQLite myths from real single-statement injection

## What AI did poorly (concrete, project-specific)

1. **Environment blindness:** green tests on new code while the browser still hit an old Flask process → equals looked broken.  
2. **Happy-path bias:** Overflow, over-long division results, destructive 16-digit formatting, and the `1e50` quantize edge needed explicit probes.  
3. **Interview writing:** early follow-up drafts sounded like generated status reports and blurred who verified what.  
4. **Archival:** full agent transcripts are not automatically a clean in-repo appendix unless exported.

## Lessons

Treat AI as a fast junior pair: specify constraints, verify against the official brief and running system, keep scope small, and separate **feature asks** from **bug fixes** from **ops mistakes**. Label agent-run tests as agent-run. Do not invent personal browser or pytest claims the conversation does not support.
