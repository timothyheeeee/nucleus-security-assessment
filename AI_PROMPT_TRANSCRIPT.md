# AI Prompt / Output Transcript (Index)

Concise chronological index of Cursor assessment interactions.  
**Full recovered prompts and user-visible AI text:** [`AI_FULL_INTERACTIONS.md`](AI_FULL_INTERACTIONS.md)

Overview map: [`AI_USAGE.md`](AI_USAGE.md) · Follow-ups: [`FOLLOW_UP_ANSWERS.md`](FOLLOW_UP_ANSWERS.md)

## Source and limits

- **Recovered from:** local Cursor agent transcript JSONL  
  `agent-transcripts/f4b8820b-ab79-4c66-a042-e78a7f5e68dc/…jsonl`  
  (IDE path; not checked into git)
- **Prompts:** verbatim `<user_query>` text for Interactions 1–31
- **AI responses:** user-visible assistant text only (tool JSON / hidden reasoning omitted)
- **ChatGPT** drafting chats: **not** present in accessible Cursor archives — disclosed as provenance only
- Personal email found in one recovered AI paragraph was **redacted** in `AI_FULL_INTERACTIONS.md`

## Chronological index

| # | Title | Type | Full record |
|---|--------|------|-------------|
| 1 | Master assessment brief | Implementation | [Interaction 1](AI_FULL_INTERACTIONS.md#interaction-1--master-assessment-brief--build-review--calculator) |
| 2 | Cursor system follow-up (auto) | System meta | [Interaction 2](AI_FULL_INTERACTIONS.md) |
| 3 | Prompt 1 status check | Docs / status | [Interaction 3](AI_FULL_INTERACTIONS.md) |
| 4 | Independent audit (Prompt 2) | Corrective | [Interaction 4](AI_FULL_INTERACTIONS.md) |
| 5 | Expression + decimal places | Feature | [Interaction 5](AI_FULL_INTERACTIONS.md) |
| 6 | Parentheses | Feature | [Interaction 6](AI_FULL_INTERACTIONS.md) |
| 7 | Equals / stale Flask | Debug | [Interaction 7](AI_FULL_INTERACTIONS.md) |
| 8 | Cursor system follow-up (auto) | System meta | [Interaction 8](AI_FULL_INTERACTIONS.md) |
| 9 | Follow-up currency | Docs | [Interaction 9](AI_FULL_INTERACTIONS.md) |
| 10 | Approve updating follow-ups | Docs | [Interaction 10](AI_FULL_INTERACTIONS.md) |
| 11 | Interview submission optimisation | Docs | [Interaction 11](AI_FULL_INTERACTIONS.md) |
| 12–14 | Confirmation-marker clarifications | Docs | [Interactions 12–14](AI_FULL_INTERACTIONS.md) |
| 15 | Final submission preparation | Audit / docs | [Interaction 15](AI_FULL_INTERACTIONS.md) |
| 16 | Edit follow-ups (remove email sections) | Docs | [Interaction 16](AI_FULL_INTERACTIONS.md) |
| 17 | GitHub profile URL | Repo setup | [Interaction 17](AI_FULL_INTERACTIONS.md) |
| 18 | Cursor system follow-up (auto) | System meta | [Interaction 18](AI_FULL_INTERACTIONS.md) |
| 19 | Evidence-first precision pass | Defect fix | [Interaction 19](AI_FULL_INTERACTIONS.md) |
| 20–22 | GitHub push status / push | Repo | [Interactions 20–22](AI_FULL_INTERACTIONS.md) |
| 23–24 | Final repository cleanup (+ compaction continue) | Cleanup | [Interactions 23–24](AI_FULL_INTERACTIONS.md) |
| 25–26 | Cleanup push | Repo | [Interactions 25–26](AI_FULL_INTERACTIONS.md) |
| 27 | Pre-submission technical review | Technical review | [Interaction 27](AI_FULL_INTERACTIONS.md) |
| 28 | Push (already clean) | Repo | [Interaction 28](AI_FULL_INTERACTIONS.md) |
| 29–30 | Submission-completeness + push | Docs / repo | [Interactions 29–30](AI_FULL_INTERACTIONS.md) |
| 31 | Final AI disclosure packaging | Disclosure | [Interaction 31](AI_FULL_INTERACTIONS.md) |

## Technical reasoning visible in the original process

Supported by the recovered prompts/outcomes in `AI_FULL_INTERACTIONS.md` (often AI-proposed first under candidate constraints, then verified):

- F-string SQL injection risk and realistic SQLite `execute` impact  
- Authentication vs authorisation for vendor `role`  
- Vendor `SHA256(secret + body)` vs unilateral HMAC  
- Comment says upsert; code only INSERTs  
- Restricted expression parsing instead of `eval`  
- Working Decimal precision vs display rounding  
- Stale Flask process vs green tests  
- Destructive 16-significant-digit serialization  
- `1e50` / magnitude vs quantize consistency  
- Distinguishing real defects from unnecessary enhancements (Interaction 27)

## Latest automated verification (Cursor agent)

```text
Command: py -3 -m pytest -q
Result:  72 passed, 0 failed, 0 skipped
```
