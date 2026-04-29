# Apigee Proxy Bundle

This folder contains a small Apigee-style API proxy bundle for the demo mobile API.

It is intentionally public-safe:

- No real Apigee organization names.
- No real API keys.
- No customer data.
- No employer-specific configuration.
- The target URL is a placeholder and must be replaced before deployment.

## Purpose

The proxy demonstrates how a mobile API could be exposed through an API management layer before reaching the backend.

Conceptual flow:

```text
Mobile app
-> Apigee proxy base path /mobile/v1
-> policies: API key, spike arrest, quota, headers
-> Cloud Run / FastAPI backend
```

## Files

- `apiproxy/mobile-platform-api.xml` - top-level API proxy descriptor.
- `apiproxy/proxies/default.xml` - client-facing proxy endpoint and request flow.
- `apiproxy/targets/default.xml` - backend target endpoint.
- `apiproxy/policies/Verify-API-Key.xml` - validates API key from `x-api-key`.
- `apiproxy/policies/Spike-Arrest.xml` - protects backend from sudden traffic spikes.
- `apiproxy/policies/Quota.xml` - limits total calls over a time window.
- `apiproxy/policies/Add-Proxy-Headers.xml` - adds gateway context headers before routing.

## Deployment Note

Before importing this bundle into Apigee, update:

```text
apiproxy/targets/default.xml
```

Replace:

```text
https://replace-with-cloud-run-service-url
```

with the real backend base URL for the target environment.

## Explanation

> I did not install Apigee Hybrid end to end in this lab because that requires an enterprise Apigee organization and Kubernetes runtime setup. Instead, I created an Apigee-style proxy bundle showing the key platform concepts: proxy endpoint, target endpoint, API key validation, quota, spike arrest, and request header enrichment. This lets me explain how a mobile app request would pass through an API management layer before reaching the backend.
