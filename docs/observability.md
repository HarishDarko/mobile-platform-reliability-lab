# Observability And Incident Simulation

This document explains how the lab demonstrates observability concepts without requiring paid Splunk or Dynatrace accounts.

## Purpose

Mobile app failures often cross system boundaries. A user-facing issue may be caused by:

- Mobile app environment configuration
- Device or emulator networking
- API gateway routing or policies
- Backend errors
- Backend latency
- TLS certificate failures
- Cloud runtime issues

This lab keeps the implementation small while showing how logs, metrics, health checks, and incident simulation endpoints support troubleshooting.

## Signals In This Lab

### Health

Endpoint:

```text
GET /health
```

Use:

- Load balancer checks
- Kubernetes probes
- Cloud Run health-style validation
- Basic uptime monitoring

### Logs

The backend emits structured JSON logs with fields such as:

- `timestamp`
- `level`
- `logger`
- `message`
- `request_id`

Structured logs are easier to search in log platforms than free-form text.

### Metrics

Endpoint:

```text
GET /metrics
```

The current metrics endpoint is intentionally simple. It exposes demo counters for:

- total requests
- total accepted demo payments

In a production system, metrics would likely be exported to Prometheus, Cloud Monitoring, Dynatrace, or another observability platform.

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
index=mobile-platform-lab path="/error" status=500
```

```text
index=mobile-platform-lab request_id="mobile-demo-123456789"
```

```text
index=mobile-platform-lab path="/slow" | stats avg(duration_ms), p95(duration_ms)
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
- request IDs map to cross-system correlation.

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

> I added observability examples because mobile incidents are often cross-layer problems. A login failure or payment failure could be caused by app config, network, API gateway, certificate expiry, or backend health. The lab uses structured logs, health checks, a metrics endpoint, request IDs, and simulated slow/error endpoints to practice troubleshooting without requiring paid observability tools.
