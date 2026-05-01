# Kubernetes Manifests

This folder shows how the FastAPI backend could run in Kubernetes.

These manifests are intentionally small and public-safe. They do not include real secrets, real cloud project IDs, production hostnames, or employer-specific details.

## Files

- `base/` - Core manifests for namespace, config, placeholder secret, deployment, service, and optional ingress.
- `overlays/gke/` - GKE Autopilot overlay that uses an Artifact Registry image placeholder and exposes the backend with a LoadBalancer service.
- `kustomization.yaml` - Renders the base manifests for local validation.

## Why It Matters

Kubernetes separates the desired state of the service from the machine where it runs.

For this lab:

- The `Deployment` says how many backend pods should exist.
- The `Service` gives those pods a stable internal network name.
- The `ConfigMap` separates non-secret config from the container image.
- The `Secret` shows where sensitive config would be injected, though real production secrets should come from a proper secret management flow.
- The readiness and liveness probes call `/health` so Kubernetes can decide when a pod is ready for traffic and when it should be restarted.

## Validate Manifests Locally

If `kubectl` is installed:

```powershell
kubectl kustomize .\k8s
kubectl kustomize .\k8s\overlays\gke
```

Expected result:

```text
apiVersion: v1
kind: Namespace
...
```

If you have a local Kubernetes cluster such as Docker Desktop Kubernetes enabled:

```powershell
kubectl apply -k .\k8s
kubectl get pods -n mobile-platform-lab
kubectl get svc -n mobile-platform-lab
```

Expected result after the image is available to the cluster:

```text
NAME                                   READY   STATUS    RESTARTS
mobile-platform-api-...                1/1     Running   0
```

## Local Image Note

The deployment uses:

```text
mobile-platform-reliability-api:local
```

That works only when the Kubernetes cluster can access that local image. For a real cluster, the image would be pushed to a registry such as Artifact Registry, then the deployment image would be updated to that registry path.

## GKE LoadBalancer Demo

For the live GKE Autopilot and external LoadBalancer walkthrough, see:

```text
docs/gke-live-loadbalancer-demo.md
```

The GKE overlay intentionally uses this placeholder:

```text
GKE_IMAGE_URI_PLACEHOLDER:demo
```

The live demo replaces it at deploy time with the Artifact Registry image URI so no real project-specific image path needs to be committed.

## Cleanup

```powershell
kubectl delete namespace mobile-platform-lab
```

Deleting the namespace removes the demo deployment, service, config map, and placeholder secret.
