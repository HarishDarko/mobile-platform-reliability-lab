# Live GKE Autopilot LoadBalancer Demo

This is a temporary hands-on Kubernetes demo. Delete the cluster immediately after testing.

## What This Proves

```text
Docker image in Artifact Registry
-> GKE Autopilot cluster
-> Kubernetes Deployment
-> readiness/liveness probes
-> Kubernetes Service type LoadBalancer
-> public external IP
-> /health test
```

Cloud Run remains the simpler production-style demo path for this lab. GKE shows the Kubernetes runtime path.

## 1. Create Foundation And GKE Cluster

Run this from GitHub Actions:

```text
Terraform Apply
```

Set workflow input:

```text
enable_gke_autopilot = true
gke_cluster_name = mobile-platform-lab-autopilot
```

Terraform creates:

```text
Artifact Registry
Secret Manager metadata
Cloud Run runtime service account
IAM bindings
GKE Autopilot cluster
```

## 2. Build Image And Deploy To GKE

Run this from GitHub Actions:

```text
Deploy Backend To GKE
```

Use inputs:

```text
image_tag = demo
cluster_name = mobile-platform-lab-autopilot
```

The workflow builds the backend image, pushes it to Artifact Registry, gets GKE credentials, applies the GKE Kubernetes overlay, waits for rollout, waits for the external LoadBalancer IP, and smoke-tests `/health` and `/accounts`.

## 3. Optional Local Verification

```powershell
gcloud container clusters get-credentials mobile-platform-lab-autopilot `
  --project mobile-devops-494819 `
  --region northamerica-northeast1

kubectl rollout status deployment/mobile-platform-api -n mobile-platform-lab --timeout=180s
kubectl get pods -n mobile-platform-lab -o wide
kubectl get service mobile-platform-api -n mobile-platform-lab
```

Wait until `EXTERNAL-IP` is no longer pending.

```powershell
kubectl get service mobile-platform-api -n mobile-platform-lab -w
```

## 4. Test The Public API

PowerShell:

```powershell
$ExternalIp = kubectl get service mobile-platform-api -n mobile-platform-lab -o jsonpath="{.status.loadBalancer.ingress[0].ip}"
Invoke-RestMethod "http://$ExternalIp/health"
Invoke-RestMethod "http://$ExternalIp/accounts"
```

Browser:

```text
http://EXTERNAL_IP/docs
```

## 5. Troubleshooting Commands

```powershell
kubectl describe deployment mobile-platform-api -n mobile-platform-lab
kubectl describe service mobile-platform-api -n mobile-platform-lab
kubectl describe pods -n mobile-platform-lab
kubectl logs deployment/mobile-platform-api -n mobile-platform-lab
kubectl get events -n mobile-platform-lab --sort-by=.lastTimestamp
```

Common issues:

- `ImagePullBackOff`: image path is wrong or cluster cannot pull from Artifact Registry.
- `EXTERNAL-IP pending`: load balancer is still provisioning or quota/networking has an issue.
- Readiness probe failure: container is running but `/health` is failing.
- 404 on `/`: expected, because the API exposes `/health`, `/docs`, `/accounts`, and other specific routes.

## 6. Cleanup

You can delete the namespace first if you want to remove the LoadBalancer before cluster deletion:

```powershell
kubectl delete namespace mobile-platform-lab --ignore-not-found
```

Then run this from GitHub Actions:

```text
Terraform Destroy
```

Use the same cluster input values:

```text
enable_gke_autopilot = true
gke_cluster_name = mobile-platform-lab-autopilot
```

Verify cleanup:

```powershell
gcloud container clusters list --project mobile-devops-494819
gcloud compute forwarding-rules list --project mobile-devops-494819
gcloud compute addresses list --project mobile-devops-494819
```

## Interview Explanation

> I first created GKE manually to understand the moving parts, then moved the GKE Autopilot cluster into Terraform. Terraform can now create and destroy the temporary cluster, while GitHub Actions builds the backend image, deploys the Kubernetes overlay, waits for rollout, waits for the external LoadBalancer IP, and smoke-tests the public API.
