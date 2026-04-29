# Runbook: Mobile API Incident

This is a public-safe demo runbook for troubleshooting mobile API failures in the lab.

## Symptoms

- Mobile app shows API error.
- Health check fails.
- Account fetch fails.
- Demo payment fails.
- API responses are slow.
- Backend returns 5xx errors.

## First Questions

- Is this affecting all users or a subset?
- Is it iOS, Android, web, or all clients?
- Which app version is affected?
- Which environment is affected?
- Which endpoint is failing?
- When did it start?
- Was there a recent deployment or config change?

## Quick Checks

Check backend health:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

Check accounts endpoint:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/accounts
```

Simulate latency:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/slow
```

Simulate backend failure:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/error
```

Check metrics:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/metrics
```

## Investigation Path

1. Confirm mobile app API base URL.
2. Confirm network connectivity.
3. Confirm gateway routing and policies.
4. Confirm certificate validity.
5. Confirm backend health.
6. Search logs by request ID and timestamp.
7. Check latency and error-rate metrics.
8. Identify whether the issue is client config, gateway, backend, dependency, or infrastructure.

## Likely Causes

| Symptom | Possible Cause |
| --- | --- |
| API URL unreachable | Wrong environment config or network issue |
| TLS failure | Expired or invalid certificate |
| 401/403 | Authentication or gateway policy issue |
| 404 | Wrong route or backend path |
| 429 | Rate limit or quota policy |
| 500 | Backend error |
| Slow response | Backend latency or downstream dependency |

## Communication Template

```text
Impact:
Start time:
Affected clients:
Affected endpoint:
Current finding:
Mitigation:
Next update:
```

## Resolution Checklist

- Root cause identified.
- User impact understood.
- Fix or mitigation applied.
- Health check passing.
- Error rate back to normal.
- Latency back to normal.
- Certificate status verified if relevant.
- Follow-up action created.

