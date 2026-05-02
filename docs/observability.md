# Observability And Incident Simulation

This document explains how the lab demonstrates observability concepts without requiring paid Splunk or Dynatrace accounts.

The primary live path is:

```text
Cloud Run API -> Cloud Logging + Cloud Monitoring -> incident investigation
```

Those same signals map to enterprise tools:

```text
Cloud Logging    -> Splunk-style log search and correlation
Cloud Monitoring -> Dynatrace-style health, latency, errors, dashboards, alerts
```

## Purpose

Mobile app failures often cross system boundaries. A user-facing issue may be caused by:

- Mobile app environment configuration
- Device or emulator networking
- API gateway routing or policies
- Backend errors
- Backend latency
- TLS certificate failures
- Cloud runtime issues

This lab keeps the implementation small while showing how logs, metrics, health checks, and incident simulation endpoints support troubleshooting in a live cloud environment.

## Signals In This Lab

### Health

Endpoint:

```text
GET /health
```

Use:

- Load balancer checks
- Kubernetes probes
- Cloud Run validation
- Uptime monitoring

### Logs

The backend emits structured JSON logs with fields such as:

- `timestamp`
- `level`
- `logger`
- `message`
- `event`
- `request_id`
- `method`
- `path`
- `status_code`
- `duration_ms`

Structured logs are easier to search in log platforms than free-form text.

Example completed request log:

```json
{
  "timestamp": "2026-05-02T14:30:00+00:00",
  "level": "INFO",
  "logger": "mobile-platform-lab",
  "message": "request_completed",
  "event": "request_completed",
  "request_id": "demo-123",
  "method": "GET",
  "path": "/accounts",
  "status_code": 200,
  "duration_ms": 12.4
}
```

### Metrics

Endpoint:

```text
GET /metrics
```

The metrics endpoint exposes Prometheus-style text for:

- total requests
- total accepted demo payments
- total 5xx errors
- requests by method, path, and status code
- request duration sum, count, and maximum by method and path

In a production system, metrics would likely be exported to Prometheus, Cloud Monitoring, Dynatrace, or another observability platform.

Example metrics:

```text
lab_http_requests_total{method="GET",path="/health",status_code="200"} 3
lab_http_requests_total{method="GET",path="/error",status_code="500"} 2
lab_http_request_duration_seconds_max{method="GET",path="/slow"} 2.004321
```

### Incident Simulation

Endpoint:

```text
GET /slow
```

Purpose:

- Simulates backend latency.
- Useful for explaining p95 latency, response time alerts, and mobile loading states.

Endpoint:

```text
GET /error
```

Purpose:

- Simulates HTTP 500 backend failure.
- Useful for explaining error-rate alerts, logs, and API failure handling.

## Generate Live Traffic

Use this script against either localhost or a Cloud Run URL:

```powershell
.\scripts\emit-observability-traffic.ps1 -ApiBaseUrl "http://127.0.0.1:8000"
```

For Cloud Run:

```powershell
.\scripts\emit-observability-traffic.ps1 -ApiBaseUrl "https://YOUR-CLOUD-RUN-URL"
```

This sends normal, slow, and error traffic so logs and metrics have useful signal.

After traffic, check:

```powershell
Invoke-RestMethod "https://YOUR-CLOUD-RUN-URL/metrics"
```

## GCP Observability Mapping

Cloud Logging:

- Search JSON logs by `request_id`.
- Filter by `path="/error"` or `status_code=500`.
- Investigate exact request timestamps and durations.

Cloud Monitoring:

- View Cloud Run request count.
- View latency.
- View 4xx/5xx errors.
- Create uptime checks for `/health`.
- Create alert policies for availability or error-rate symptoms.

Useful Cloud Run log command:

```powershell
gcloud run services logs read mobile-platform-api --region northamerica-northeast1 --limit 50
```

Useful GCP Console path:

```text
Cloud Run -> mobile-platform-api -> Logs
Cloud Run -> mobile-platform-api -> Metrics
Monitoring -> Metrics Explorer
Monitoring -> Uptime checks
Monitoring -> Alerting
```

## Splunk Mapping

Splunk is useful for log search and event analysis.

Example questions Splunk can answer:

- Which endpoint failed?
- When did failures start?
- Which request ID failed?
- Was the status code 500, 404, 401, or another error?
- Did latency increase for a specific path?

Example pseudo-searches:

```text
index=mobile-platform-lab event="request_completed" path="/error" status_code=500
```

```text
index=mobile-platform-lab request_id="mobile-demo-123456789"
```

```text
index=mobile-platform-lab event="request_completed" path="/slow" | stats avg(duration_ms), p95(duration_ms)
```

```text
index=mobile-platform-lab event="request_completed" | stats count by path status_code
```

## Dynatrace Mapping

Dynatrace is useful for APM, service health, latency, traces, dependency maps, and alerting.

Example questions Dynatrace can answer:

- Is the backend service healthy?
- Did p95 latency increase?
- Did the 5xx error rate increase?
- Which dependency is slow or failing?
- Did a deployment correlate with a problem?

For this lab:

- `/slow` maps to latency analysis.
- `/error` maps to failure-rate analysis.
- `/health` maps to availability checks.
- Request IDs map to cross-system correlation.
- Cloud Run metrics map to service-level monitoring.
- Cloud Logging maps to log analysis and incident investigation.

## Alerting Examples

Useful alerts for this lab:

- `/health` uptime check fails.
- Cloud Run 5xx error rate rises.
- p95 latency rises.
- Certificate expiry monitor returns CRITICAL.

Avoid noisy alerts:

- Alert on user-impacting symptoms first.
- Use thresholds and duration windows.
- Route warnings differently from critical pages.
- Add runbook links to alerts.

## Mobile Troubleshooting Flow

If the mobile app shows an API failure:

1. Confirm app environment and API base URL.
2. Confirm device or emulator network access.
3. Check whether the problem affects iOS, Android, web, or all clients.
4. Check API gateway status, policies, routing, and certificates.
5. Check backend `/health`.
6. Search backend logs by request ID and timestamp.
7. Check metrics for latency and error-rate changes.
8. Check certificate expiry if TLS or network errors appear.
9. Communicate impact and next update time.

## Explanation

> I added observability examples because mobile incidents are often cross-layer problems. A login failure or payment failure could be caused by app config, network, API gateway, certificate expiry, or backend health. The lab uses structured logs, health checks, Prometheus-style metrics, request IDs, and simulated slow/error endpoints to practice troubleshooting in Cloud Run without requiring paid observability tools.
