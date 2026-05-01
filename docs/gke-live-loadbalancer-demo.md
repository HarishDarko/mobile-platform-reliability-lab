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

## 1. Create Foundation And Image

Run these from GitHub Actions:

```text
Terraform Apply
Deploy Backend To Cloud Run
```

Use image tag:

```text
demo
```

The deployment workflow builds and pushes this image:

```text
northamerica-northeast1-docker.pkg.dev/PROJECT_ID/ARTIFACT_REPOSITORY/mobile-platform-reliability-api:demo
```

## 2. Create Temporary GKE Autopilot Cluster

PowerShell:

```powershell
$ProjectId = "mobile-devops-494819"
$Region = "northamerica-northeast1"
$Cluster = "mobile-platform-lab-autopilot"

gcloud services enable container.googleapis.com --project $ProjectId

gcloud container clusters create-auto $Cluster `
  --project $ProjectId `
  --region $Region `
  --release-channel regular

gcloud container clusters get-credentials $Cluster `
  --project $ProjectId `
  --region $Region
```

Successful output should show the cluster created and kubeconfig updated.

## 3. Deploy The GKE Overlay

PowerShell:

```powershell
$ProjectId = "mobile-devops-494819"
$Region = "northamerica-northeast1"
$Repository = "mobile-platform-lab"
$ImageTag = "demo"
$ImageUri = "$Region-docker.pkg.dev/$ProjectId/$Repository/mobile-platform-reliability-api:$ImageTag"

kubectl kustomize .\k8s\overlays\gke |
  ForEach-Object { $_ -replace "GKE_IMAGE_URI_PLACEHOLDER:demo", $ImageUri } |
  kubectl apply -f -
```

This keeps the repo public-safe while still deploying the real image during the local demo.

## 4. Verify Rollout

```powershell
kubectl rollout status deployment/mobile-platform-api -n mobile-platform-lab --timeout=180s
kubectl get pods -n mobile-platform-lab -o wide
kubectl get service mobile-platform-api -n mobile-platform-lab
```

Wait until `EXTERNAL-IP` is no longer pending.

```powershell
kubectl get service mobile-platform-api -n mobile-platform-lab -w
```

## 5. Test The Public API

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

## 6. Troubleshooting Commands

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

## 7. Cleanup

Delete the app namespace first:

```powershell
kubectl delete namespace mobile-platform-lab --ignore-not-found
```

Delete the cluster:

```powershell
gcloud container clusters delete mobile-platform-lab-autopilot `
  --project mobile-devops-494819 `
  --region northamerica-northeast1 `
  --quiet
```

Verify cleanup:

```powershell
gcloud container clusters list --project mobile-devops-494819
gcloud compute forwarding-rules list --project mobile-devops-494819
gcloud compute addresses list --project mobile-devops-494819
```

Then run:

```text
Terraform Destroy
```

## Interview Explanation

> I used Cloud Run for the simple serverless container path, then deployed the same backend image to GKE Autopilot to understand the Kubernetes runtime path. The Kubernetes deployment used replicas, probes, resource requests/limits, rolling update settings, and a LoadBalancer service for public access. I verified rollout status, pods, service external IP, logs, and `/health`, then deleted the namespace and cluster to control cost.
