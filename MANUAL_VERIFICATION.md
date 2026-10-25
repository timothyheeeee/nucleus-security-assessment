# Manual verification checklist (candidate)

Agent-run pytest ≠ your browser verification.

## Start app (Windows)

```powershell
cd c:\Users\Timothy\Desktop\security\nucleus-security-assessment
.\.venv\Scripts\Activate.ps1
python app.py
```

Open http://127.0.0.1:5000/ (Ctrl+F5).

## Checks

| # | Try | Expect |
|---|-----|--------|
| 1 | `1 + 2` then `=` | Shows expression, then `3` |
| 2 | `10 + 5 × 2` then `=` | `20` |
| 3 | `(10 + 5) × 2` then `=` | `30` |
| 4 | Places=2; `10 ÷ 3` then `=` | `3.33`; change places to 4 → `3.3333` without re-entry |
| 5 | `8 ÷ 0` then `=` | Error; no crash |
| 6 | After a result, digit | New expression |
| 7 | After a result, `+` then number `=` | Continues from working result |

Optional API check (PowerShell / curl) for the precision regression:

`POST /api/calculate` with `{"expression":"100000000000000.005 + 0","decimal_places":2}` → `"display":"100000000000000.01"`.

Tick when done: [ ]
