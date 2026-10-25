# Code Review — Python Webhook (`app.py`)

**Reviewer stance:** Senior engineer reviewing a colleague’s PR before production  
**Language reviewed:** Python only (assessment allows choosing PHP or Python)  
**Source:** Official assessment Gist — Python snippet as provided (copy: `review_subject/original_webhook.py`)  
**Overall decision:** **Request changes** — do not merge until Critical/High issues are addressed

---

## 1. Review overview

### Intended behaviour (verified against source)

The endpoint should:

1. Accept vendor HTTP `POST` requests at `/webhook`.
2. Verify the `X-Signature` header using the documented scheme `SHA256(secret + body)`.
3. Parse JSON payload (email, role, metadata).
4. Upsert the user record.
5. Persist the raw request body for audit/debug.

The implementation roughly follows that shape (signature check → JSON parse → DB writes), but several defects undermine correctness and security.

### Protocol note (not scored as an implementation bug)

Vendor docs specify `SHA256(secret + body)`, not HMAC-SHA256. The code matches that protocol. Preferring HMAC is a reasonable **vendor/protocol** improvement (keyed MAC, better misuse resistance), but changing it unilaterally would break interoperability. Findings below treat the documented scheme as given and focus on defects inside that constraint.

---

## 2. High-priority findings

### Finding 1 — SQL injection via f-string queries

- **Lines:** 41–42, 46–47  
- **Severity:** Critical  
- **Title:** Untrusted input interpolated into SQL

**What:** `email`, `role`, and the decoded raw body are embedded directly into SQL via f-strings.

```python
cur.execute(
    f"INSERT INTO webhook_audit(email, raw_json) VALUES ('{email}', '{raw.decode('utf-8')}')"
)
cur.execute(
    f"INSERT INTO users(email, role) VALUES('{email}', '{role}')"
)
```

**Why it matters:** Any single quote in the body or fields breaks out of the string literal. An authenticated vendor (or anyone who can forge a valid signature if the secret is weak) can execute arbitrary SQL.

**Impact:** Data theft/exfiltration via audit table, privilege escalation in the DB, destructive writes (`DROP TABLE`, etc.).

**Fix:** Use parameterised queries only:

```python
cur.execute(
    "INSERT INTO webhook_audit(email, raw_json) VALUES (?, ?)",
    (email, raw.decode("utf-8")),
)
cur.execute(
    "INSERT INTO users(email, role) VALUES (?, ?)",
    (email, role),
)
```

---

### Finding 2 — Comment says “upsert”; code only INSERTs

- **Lines:** 45–47  
- **Severity:** High  
- **Title:** Insert-only path is not an upsert

**What:** The comment claims an upsert, but the statement is a plain `INSERT` with no `ON CONFLICT` / update path and no uniqueness handling shown in this snippet.

**Why it matters:** Repeat vendor deliveries for the same email will either fail (unique constraint) or create duplicate users (no constraint). Neither matches “upsert the user data.”

**Impact:** Broken idempotency for legitimate retries; inconsistent user rows; intermittent 500s if uniqueness exists.

**Fix:** Define a unique constraint on `users.email` and use a real upsert, e.g.:

```python
cur.execute(
    """
    INSERT INTO users(email, role) VALUES (?, ?)
    ON CONFLICT(email) DO UPDATE SET role = excluded.role
    """,
    (email, role),
)
```

(Exact SQL depends on the schema — which is not created in this PR and should be.)

---

### Finding 3 — Vendor-controlled `role` enables privilege escalation

- **Lines:** 34–35, 46–47  
- **Severity:** High  
- **Title:** Authentication ≠ authorisation for sensitive roles

**What:** After signature verification, `role` is taken from the payload (`default "user"`) and written straight into `users`. Example payload in comments includes `"role":"admin"`.

**Why it matters:** A valid signature proves the request came from someone holding the webhook secret (or a compromised vendor). It does **not** prove that this caller is allowed to grant `admin` in *our* system.

**Impact:** Compromised vendor integration or overly broad vendor trust can create admin users in the application DB.

**Fix:** Map vendor roles through an allowlist / internal mapping; never accept raw privileged roles from the payload. Example:

```python
ALLOWED_ROLES = {"user", "vendor"}
role = payload.get("role", "user")
if role not in ALLOWED_ROLES:
    return ("invalid role", 400)
```

Admin elevation should require a separate, audited internal process.

---

### Finding 4 — Hard-coded fallback webhook secret

- **Line:** 10  
- **Severity:** High  
- **Title:** Insecure default secret if env unset

**What:**

```python
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "dev-secret")  # default for dev
```

**Why it matters:** If production is misconfigured and the env var is missing, the service silently runs with a public, guessable secret. Combined with Finding 1, forged requests become trivial.

**Impact:** Full webhook forgery in misconfigured deployments; attackers can inject users and SQL.

**Fix:** Fail fast when the secret is missing outside explicit development:

```python
WEBHOOK_SECRET = os.environ["WEBHOOK_SECRET"]  # raise if unset
```

Or require a non-default secret and refuse to start if it equals `"dev-secret"` when `FLASK_ENV=production`.

---

## 3. Other meaningful findings

### Finding 5 — Non-constant-time signature comparison

- **Line:** 20  
- **Severity:** Medium  
- **Title:** `==` comparison leaks timing information

**What:** `return expected == sig` compares hex digests with ordinary string equality.

**Why it matters:** In theory, timing differences can help an attacker recover the expected digest byte-by-byte. Practicality over a network varies, but for a security product assessment this is a clear hardening miss. (Still use the vendor’s `SHA256(secret+body)` construction for *computing* the expected value.)

**Fix:**

```python
import hmac
return hmac.compare_digest(expected, sig or "")
```

Ensure both sides are strings of comparable form (e.g. always hex).

---

### Finding 6 — Unhandled parse/DB errors crash the request path

- **Lines:** 18, 30, 37–50  
- **Severity:** Medium  
- **Title:** Missing validation and exception handling

**What:**

- `body.decode("utf-8")` / `json.loads(...)` can raise (`UnicodeDecodeError`, `JSONDecodeError`).
- No check that `payload` is a `dict`, or that `email` is a non-empty string.
- DB errors are uncaught; connection is never closed (`get_db()` opens a connection with no context manager).
- No rollback on failure.

**Why it matters:** Malformed bodies after a valid signature (or encoding edge cases) yield 500s, leaked stack traces depending on Flask config, and potential connection leaks.

**Impact:** Availability issues; noisy ops; harder auditability when bad payloads arrive.

**Fix:** Validate schema explicitly; catch parse errors → 400; use `with get_db() as db:` / try/except with `rollback()`; close cursor/connection reliably.

---

### Finding 7 — Audit row stores full raw body with weak confidentiality controls

- **Lines:** 40–42  
- **Severity:** Medium  
- **Title:** Sensitive audit data without retention/access controls (in this PR)

**What:** Full raw JSON (email, role, metadata) is stored. The PR does not show access control, encryption at rest, or retention policy for `webhook_audit`.

**Why it matters:** Audit tables often become a high-value PII store. Combined with SQL injection, that table is an exfiltration target.

**Impact:** Privacy/compliance exposure; broadened blast radius of Finding 1.

**Fix:** Parameterised insert (Finding 1); restrict DB permissions; consider redacting fields; document retention. Do not log secrets if vendors ever include them in metadata.

---

### Finding 8 — No replay / duplicate-delivery handling

- **Lines:** 22–52 (endpoint as a whole)  
- **Severity:** Low–Medium  
- **Title:** No nonce/timestamp/idempotency key

**What:** Signature verifies integrity/authenticity of *this* body but not freshness. Nothing prevents replaying a captured valid request.

**Why it matters:** Depends on vendor protocol (not fully specified here). If the vendor does not include expiring timestamps or delivery IDs, replays can re-apply role changes.

**Assumption:** Vendor may document replay guidance elsewhere; this PR does not implement any.

**Fix:** If vendor provides timestamp/nonce headers, validate skew and store processed delivery IDs. At minimum, make user upsert idempotent (Finding 2).

---

## 4. Design / security assumptions

- Schema for `users` and `webhook_audit` is assumed to exist; this PR never creates or migrates tables.
- Vendor signature scheme is `SHA256(secret + body)` as documented — HMAC would be preferable *if* the vendor can change.
- Flask debug mode is not enabled in the snippet (good); binding `0.0.0.0:8080` (line 55) exposes the service on all interfaces — fine for a container with network policy, risky on a laptop/dev host.
- Default `DB_PATH` of `/tmp/app.db` (line 9) may be world-readable on shared hosts — prefer a dedicated data directory with locked-down permissions.

---

## 5. Conclusion

This PR should **not** ship as-is. The SQL injection alone is a blocker. Closely behind: insecure secret default, non-upsert “upsert,” and unconstrained role writes. Medium issues (constant-time compare, error handling, audit hygiene, replay) should be tracked before calling the webhook production-ready.

**Suggested merge gate:** Findings 1–4 fixed and covered by tests (forged body with quotes, duplicate email upsert, missing secret in prod config, rejected privileged roles).
