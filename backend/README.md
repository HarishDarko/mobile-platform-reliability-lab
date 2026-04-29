# Backend

This folder contains the Python FastAPI service used by the mobile platform reliability lab.

## What It Demonstrates

- A small API surface a mobile app can call.
- Fake account and payment workflows with no real customer data.
- Health, metrics, slow, and error endpoints for SRE troubleshooting practice.
- Structured JSON logs that can be shipped to tools like Splunk, Cloud Logging, or Dynatrace.
- Tests that verify the most important API behavior.

## Local Commands

From the repository root:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pytest
python -m uvicorn app.main:app --reload
```

API docs will be available at:

```text
http://127.0.0.1:8000/docs
```

## Docker Commands

From the repository root:

```powershell
docker build -t mobile-platform-reliability-api:local .\backend
docker run --rm -p 8000:8000 mobile-platform-reliability-api:local
```

Successful build output should end with something like:

```text
Successfully tagged mobile-platform-reliability-api:local
```

Successful run output should include:

```text
Uvicorn running on http://0.0.0.0:8000
```

Then test the containerized service:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

Expected response:

```text
status service
------ -------
ok     mobile-platform-reliability-api
```

Stop the container with `Ctrl+C`.

## Browser Demo Note

The backend enables CORS with `ALLOWED_ORIGINS`.

Default:

```text
ALLOWED_ORIGINS=*
```

For a real environment, restrict this to approved app or web origins. The permissive default is only for this public learning lab and Expo Web demo.
