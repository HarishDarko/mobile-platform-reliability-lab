# Certificate Expiry Monitor

This folder contains a small Python script that checks HTTPS certificate expiry.

It is public-safe and uses no real internal endpoints. The example endpoint file uses public demo endpoints only.

## Why It Matters

Expired certificates can break mobile apps even when the app code and backend code are healthy. Mobile users may see login failures, API failures, or generic network errors. A simple automated certificate check helps catch expiry risk before users are affected.

## Files

- `cert_check.py` - Reads HTTPS endpoints, checks TLS certificate expiry, prints `OK`, `WARNING`, or `CRITICAL`, and exits non-zero for alerting.
- `test_cert_check.py` - Unit tests for parsing and classification logic.
- `endpoints.example.txt` - Example public endpoints. Replace with approved endpoints in a real environment.

## Run Tests

From the repository root:

```powershell
cd automation
python -m pytest
```

If `pytest` is not installed globally, run tests from the backend virtual environment:

```powershell
cd ..\backend
.\.venv\Scripts\Activate.ps1
cd ..\automation
python -m pytest
```

Expected result:

```text
6 passed
```

## Run The Check

```powershell
python .\cert_check.py --endpoints-file .\endpoints.example.txt --warning-days 30 --critical-days 14
```

Exit codes:

- `0` - all certificates are OK
- `1` - at least one certificate is in warning range
- `2` - at least one certificate is critical or a check failed

## Explanation

> I wrote a small Python certificate monitor because expired TLS certificates can cause mobile API failures that look like app or network bugs. The script reads endpoints, checks certificate expiry, classifies each endpoint as OK, WARNING, or CRITICAL, and returns a non-zero exit code so it can be used in cron, Ansible, CI, or monitoring automation.
