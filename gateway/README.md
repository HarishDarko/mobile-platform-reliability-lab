# API Gateway Simulator

This folder contains a small API gateway style layer that demonstrates Apigee concepts locally.

It is not Apigee and does not try to replace Apigee. It exists to make API management concepts concrete in a small local lab.

## What It Demonstrates

- A stable mobile-facing API path.
- Routing to a backend target service.
- API key policy.
- Simple per-client rate limiting.
- Request ID propagation.
- Gateway-level structured logs.
- `401` for missing/invalid API key.
- `429` for rate limit.
- `502` when the backend target is unavailable.

## Local Run

Start the backend first:

```powershell
cd ..\backend
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --port 8000
```

Start the gateway in another PowerShell window:

```powershell
cd ..\gateway
..\backend\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:BACKEND_BASE_URL="http://127.0.0.1:8000"
$env:DEMO_API_KEY="demo-mobile-key"
..\backend\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 9000
```

Call through the gateway:

```powershell
Invoke-RestMethod http://127.0.0.1:9000/mobile/v1/accounts -Headers @{"x-api-key"="demo-mobile-key"; "x-client-id"="local-demo"}
```

## Explanation

> I did not deploy real Apigee because that would require heavier platform setup. Instead, I added a small API gateway simulator to demonstrate the same concepts: mobile-facing proxy path, target backend routing, API key validation, rate limiting, request ID propagation, and gateway-level errors. In a real Apigee setup, these concerns would be implemented through API proxies, policies, products, analytics, and gateway runtime configuration.
