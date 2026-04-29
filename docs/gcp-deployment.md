# GCP Deployment Path

This document explains two GCP deployment paths for the lab backend:

1. Cloud Run - recommended for a fast, low-complexity demo path.
2. GKE Autopilot - useful for Kubernetes platform discussion, but heavier and more cost-sensitive.

No real secrets, production hostnames, employer details, or customer data are used.

## Cost Warning

Do not create GCP resources casually.

Before running deployment commands:

- Confirm the active project.
- Confirm billing is expected.
- Use a small region close to you, such as `northamerica-northeast1` for Montreal or `us-central1` for common examples.
- Delete resources after testing.
- Prefer Cloud Run first because it is simpler than standing up a GKE cluster.

Check active project:

```powershell
gcloud config get-value project
```

Set variables for the session:

```powershell
$env:PROJECT_ID="your-gcp-project-id"
$env:REGION="northamerica-northeast1"
$env:REPOSITORY="mobile-platform-lab"
$env:IMAGE_NAME="mobile-platform-reliability-api"
$env:SERVICE_NAME="mobile-platform-api"
```

Set the project:

```powershell
gcloud config set project $env:PROJECT_ID
```

## Required APIs

```powershell
gcloud services enable artifactregistry.googleapis.com run.googleapis.com cloudbuild.googleapis.com
```

For GKE only:

```powershell
gcloud services enable container.googleapis.com
```

## Option 1: Cloud Run Path

Cloud Run is the fastest practical GCP deployment path for this lab. It runs containers without managing Kubernetes nodes or clusters.

### Create Artifact Registry Repository

```powershell
gcloud artifacts repositories create $env:REPOSITORY `
  --repository-format=docker `
  --location=$env:REGION `
  --description="Container images for mobile platform reliability lab"
```

Configure Docker authentication:

```powershell
gcloud auth configure-docker "$env:REGION-docker.pkg.dev"
```

### Build, Tag, And Push The Backend Image

From the repository root:

```powershell
docker build -t "$env:IMAGE_NAME`:local" .\backend
docker tag "$env:IMAGE_NAME`:local" "$env:REGION-docker.pkg.dev/$env:PROJECT_ID/$env:REPOSITORY/$env:IMAGE_NAME`:latest"
docker push "$env:REGION-docker.pkg.dev/$env:PROJECT_ID/$env:REPOSITORY/$env:IMAGE_NAME`:latest"
```

### Deploy To Cloud Run

```powershell
gcloud run deploy $env:SERVICE_NAME `
  --image "$env:REGION-docker.pkg.dev/$env:PROJECT_ID/$env:REPOSITORY/$env:IMAGE_NAME`:latest" `
  --region $env:REGION `
  --platform managed `
  --allow-unauthenticated `
  --port 8000
```

For a temporary public demo, `--allow-unauthenticated` is convenient. In real production systems, access should be controlled.

### Test Cloud Run

After deploy, get the service URL:

```powershell
$env:SERVICE_URL = gcloud run services describe $env:SERVICE_NAME `
  --region $env:REGION `
  --format "value(status.url)"
```

Call health:

```powershell
Invoke-RestMethod "$env:SERVICE_URL/health"
```

Expected response:

```text
status service
------ -------
ok     mobile-platform-reliability-api
```

Use this URL for the mobile app:

```powershell
$env:EXPO_PUBLIC_API_URL=$env:SERVICE_URL
npm run web
```

### Cloud Run Cleanup

Delete the service:

```powershell
gcloud run services delete $env:SERVICE_NAME --region $env:REGION
```

Delete the Artifact Registry repository:

```powershell
gcloud artifacts repositories delete $env:REPOSITORY --location $env:REGION
```

Disable APIs only if you are done using them in the project:

```powershell
gcloud services disable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com
```

## Option 2: GKE Autopilot Path

GKE Autopilot is useful to discuss Kubernetes, but it is heavier than Cloud Run for this lab. Use it only if you intentionally want to practice GKE.

Set cluster name:

```powershell
$env:CLUSTER_NAME="mobile-platform-lab"
```

Create an Autopilot cluster:

```powershell
gcloud container clusters create-auto $env:CLUSTER_NAME `
  --location $env:REGION `
  --project $env:PROJECT_ID
```

Get credentials:

```powershell
gcloud container clusters get-credentials $env:CLUSTER_NAME `
  --location $env:REGION `
  --project $env:PROJECT_ID
```

Update the Kubernetes deployment image to the Artifact Registry image:

```powershell
kubectl set image deployment/mobile-platform-api `
  api="$env:REGION-docker.pkg.dev/$env:PROJECT_ID/$env:REPOSITORY/$env:IMAGE_NAME`:latest" `
  -n mobile-platform-lab
```

If deploying for the first time, apply the manifests:

```powershell
kubectl apply -k .\k8s
kubectl get pods -n mobile-platform-lab
kubectl get svc -n mobile-platform-lab
```

For external access, you would need an ingress controller, Gateway API setup, or a LoadBalancer service. This lab keeps that optional to avoid unnecessary cloud cost and complexity.

### GKE Cleanup

Delete the lab namespace:

```powershell
kubectl delete namespace mobile-platform-lab
```

Delete the GKE cluster:

```powershell
gcloud container clusters delete $env:CLUSTER_NAME `
  --location $env:REGION `
  --project $env:PROJECT_ID
```

Delete the Artifact Registry repository if no longer needed:

```powershell
gcloud artifacts repositories delete $env:REPOSITORY --location $env:REGION
```

Disable GKE API only if you are done using it:

```powershell
gcloud services disable container.googleapis.com
```

## Explanation

Cloud Run answer:

> For a small containerized backend, I would choose Cloud Run first because it lets me deploy a container without managing a Kubernetes cluster. It is faster, simpler, and a better fit for a learning lab or small service. The same Docker image can later be used in GKE if the team needs Kubernetes-specific controls.

GKE answer:

> GKE is useful when the team needs Kubernetes primitives such as Deployments, Services, ConfigMaps, Secrets, probes, autoscaling, ingress, and stronger platform control. It is more powerful, but it also adds operational responsibility and cost compared to Cloud Run.

Cloud Run versus GKE:

> Cloud Run is the simpler serverless container path. GKE is the Kubernetes platform path. For this lab, Cloud Run is the practical deployment option, while GKE helps me explain how the Kubernetes manifests would map to a real cluster.
