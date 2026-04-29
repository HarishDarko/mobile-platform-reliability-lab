# Kubernetes Manifests

This folder shows how the FastAPI backend could run in Kubernetes.

These manifests are intentionally small and public-safe. They do not include real secrets, real cloud project IDs, production hostnames, or employer-specific details.

## Files

- `namespace.yaml` - Creates an isolated namespace for the lab.
- `configmap.yaml` - Stores non-secret runtime configuration.
- `secret-example.yaml` - Shows the shape of a Kubernetes Secret with placeholder values only.
- `deployment.yaml` - Runs two backend pods with health probes and resource requests/limits.
- `service.yaml` - Creates an internal stable service name for the backend pods.
- `ingress-example.yaml` - Optional example for exposing the service through an ingress controller.
- `kustomization.yaml` - Groups the core manifests so they can be applied together.

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

## Cleanup

```powershell
kubectl delete namespace mobile-platform-lab
```

Deleting the namespace removes the demo deployment, service, config map, and placeholder secret.

