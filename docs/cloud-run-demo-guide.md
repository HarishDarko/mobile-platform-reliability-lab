# Cloud Run Demo Guide

This guide is a read-and-follow deployment runbook for a cloud demo.

Goal:

```text
Local FastAPI backend -> Docker image -> Artifact Registry -> Cloud Run -> Expo app calls cloud API
```

This proves the backend works outside the local laptop and gives a real cloud URL for the Expo React Native app demo.

## 0. What You Are Deploying

You are deploying only the backend service first:

```text
backend/ FastAPI API
Dockerfile
Cloud Run service: mobile-platform-api
```

The mobile app remains local for the demo:

```text
Expo app on Windows -> EXPO_PUBLIC_API_URL=<Cloud Run URL>
```

This is intentional. It is enough to prove the app can call a cloud-hosted API while keeping the demo simple and reliable.

## 1. Why Cloud Run First

Cloud Run is the recommended demo path because:

- It runs containers without managing Kubernetes nodes.
- It is faster and lower-risk than GKE for a short cloud demo.
- It proves the Dockerized backend works in cloud.
- It gives a public HTTPS URL.
- It uses the same image that could later run in GKE.

Explanation:

> I chose Cloud Run for the live demo because it is the fastest low-risk way to prove the containerized backend runs in GCP. The same image could later be deployed to GKE if the team needs Kubernetes-specific controls.

## 2. Official Docs Checked

Official Google Cloud docs used for this guide:

- Cloud Run container deployment: `https://cloud.google.com/run/docs/deploying`
- Cloud Run container port configuration: `https://cloud.google.com/run/docs/configuring/services/containers`
- Artifact Registry Docker push/pull: `https://docs.cloud.google.com/artifact-registry/docs/docker/pushing-and-pulling`
- Google Cloud CLI install: `https://cloud.google.com/sdk/docs/install`

Key points from the docs:

- Cloud Run can deploy container images from Artifact Registry.
- Cloud Run injects a `PORT` environment variable into the container.
- Artifact Registry image names use:

```text
LOCATION-docker.pkg.dev/PROJECT_ID/REPOSITORY/IMAGE:TAG
```

- Docker must authenticate to the Artifact Registry host before pushing.

## 3. Local Readiness Changes Already Made

The backend is ready for Cloud Run:

- Dockerfile now starts Uvicorn using `${PORT:-8000}`.
- This supports Cloud Run's injected `PORT` environment variable.
- CORS is enabled through `ALLOWED_ORIGINS` so Expo Web can call the Cloud Run API.
- Local Docker smoke test passed with `PORT=8080`, matching Cloud Run behavior.

Important file:

```text
backend/Dockerfile
backend/app/main.py
```

## 4. Final Local Checks Already Passed

Latest validation:

```text
backend pytest: 6 passed
backend ruff: All checks passed
gateway pytest: 4 passed
mobile typecheck: passed
mobile lint: passed
automation pytest: 6 passed
kubectl kustomize: passed
docker build: passed
Docker PORT=8080 smoke test: /health returned ok
```

Run these again before deployment if you want a clean final check:

```powershell
cd "<path-to>\mobile-platform-reliability-lab"

cd backend
.\.venv\Scripts\Activate.ps1
python -m pytest
python -m ruff check app tests

cd ..\automation
..\backend\.venv\Scripts\python.exe -m pytest

cd ..\gateway
..\backend\.venv\Scripts\python.exe -m pytest
..\backend\.venv\Scripts\python.exe -m ruff check app tests

cd ..\mobile
npm run typecheck
npm run lint

cd ..
kubectl kustomize .\k8s
docker build -t mobile-platform-reliability-api:local .\backend
```

## 5. Prerequisites

Already confirmed locally:

```text
Docker version 27.1.1
Google Cloud SDK 502.0.0
```

If `gcloud` is missing on another machine, install from:

```text
https://cloud.google.com/sdk/docs/install
```

## 6. Cost Warning

Cloud Run is lower risk than GKE, but it is still a cloud resource.

Before deploying:

- Confirm the active GCP project.
- Confirm billing is expected.
- Delete the Cloud Run service after the demo if you do not need it.
- Delete the Artifact Registry repository if it is only for the demo.
- Do not create GKE for this demo unless you intentionally choose to.

## 7. Choose Deployment Values

Use these variables in PowerShell.

Replace `your-gcp-project-id` with your real project ID.

```powershell
$env:PROJECT_ID="your-gcp-project-id"
$env:REGION="northamerica-northeast1"
$env:REPOSITORY="mobile-platform-lab"
$env:IMAGE_NAME="mobile-platform-reliability-api"
$env:SERVICE_NAME="mobile-platform-api"
$env:TAG="demo"
```

Why this region:

```text
northamerica-northeast1
```

Choose a region close to your users or project requirements. You can use another region if your GCP project has constraints.

## 8. Authenticate And Select Project

Run:

```powershell
gcloud auth login
```

What happens:

- Browser opens.
- Sign in with your Google account.
- Allow Google Cloud SDK access.
- Return to PowerShell.

Then set the project:

```powershell
gcloud config set project $env:PROJECT_ID
gcloud config get-value project
```

Expected:

```text
your-gcp-project-id
```

If you need to find project IDs:

```powershell
gcloud projects list
```

## 9. Enable Required APIs

Run:

```powershell
gcloud services enable artifactregistry.googleapis.com run.googleapis.com cloudbuild.googleapis.com
```

Why:

- `artifactregistry.googleapis.com` stores Docker images.
- `run.googleapis.com` runs Cloud Run services.
- `cloudbuild.googleapis.com` is useful for build/deployment workflows and may be required by some operations.

Expected:

```text
Operation finished successfully
```

If it says the API is already enabled, that is fine.

## 10. Create Artifact Registry Repository

Run:

```powershell
gcloud artifacts repositories create $env:REPOSITORY `
  --repository-format=docker `
  --location=$env:REGION `
  --description="Container images for mobile platform reliability lab"
```

Expected:

```text
Created repository [mobile-platform-lab]
```

If it already exists, that is fine. Continue.

Google Cloud Console UI path:

```text
Google Cloud Console -> Artifact Registry -> Repositories
```

You should see:

```text
mobile-platform-lab
```

## 11. Authenticate Docker To Artifact Registry

Run:

```powershell
gcloud auth configure-docker "$env:REGION-docker.pkg.dev"
```

When prompted, answer:

```text
Y
```

Why:

> Docker needs permission to push images to Artifact Registry.

## 12. Build The Backend Docker Image

From repo root:

```powershell
cd "<path-to>\mobile-platform-reliability-lab"
docker build -t "$env:IMAGE_NAME`:local" .\backend
```

Expected:

```text
naming to docker.io/library/mobile-platform-reliability-api:local done
```

## 13. Tag The Image For Artifact Registry

Run:

```powershell
$env:IMAGE_URI="$env:REGION-docker.pkg.dev/$env:PROJECT_ID/$env:REPOSITORY/$env:IMAGE_NAME`:$env:TAG"
docker tag "$env:IMAGE_NAME`:local" $env:IMAGE_URI
```

Check value:

```powershell
echo $env:IMAGE_URI
```

Expected shape:

```text
northamerica-northeast1-docker.pkg.dev/YOUR_PROJECT/mobile-platform-lab/mobile-platform-reliability-api:demo
```

## 14. Push The Image

Run:

```powershell
docker push $env:IMAGE_URI
```

Expected:

```text
demo: digest: sha256:...
```

Google Cloud Console UI path:

```text
Google Cloud Console -> Artifact Registry -> Repositories -> mobile-platform-lab
```

You should see the image:

```text
mobile-platform-reliability-api
```

## 15. Deploy To Cloud Run

Run:

```powershell
gcloud run deploy $env:SERVICE_NAME `
  --image $env:IMAGE_URI `
  --region $env:REGION `
  --platform managed `
  --allow-unauthenticated `
  --set-env-vars ALLOWED_ORIGINS="*"
```

Why `--allow-unauthenticated`:

> This is a temporary public demo endpoint. It lets the Expo app call the API without setting up IAM authentication.

Production note:

> In production, public access should be reviewed carefully. APIs may be protected by gateway auth, IAM, API keys, OAuth, Apigee policies, or other controls.

Expected:

```text
Service [mobile-platform-api] revision [...] has been deployed
Service URL: https://mobile-platform-api-...
```

Copy the service URL.

Google Cloud Console UI path:

```text
Google Cloud Console -> Cloud Run -> Services -> mobile-platform-api
```

You should see:

- service name
- region
- latest revision
- URL
- logs tab
- metrics tab

## 16. Verify Cloud Run API

Store service URL:

```powershell
$env:SERVICE_URL = gcloud run services describe $env:SERVICE_NAME `
  --region $env:REGION `
  --format "value(status.url)"

echo $env:SERVICE_URL
```

Health:

```powershell
Invoke-RestMethod "$env:SERVICE_URL/health"
```

Expected:

```text
status service
------ -------
ok     mobile-platform-reliability-api
```

Accounts:

```powershell
Invoke-RestMethod "$env:SERVICE_URL/accounts"
```

Expected:

```text
demo-chequing-001
demo-savings-001
```

Metrics:

```powershell
Invoke-RestMethod "$env:SERVICE_URL/metrics"
```

Error simulation:

```powershell
try {
  Invoke-RestMethod "$env:SERVICE_URL/error"
} catch {
  $_.Exception.Response.StatusCode.value__
}
```

Expected:

```text
500
```

Slow simulation:

```powershell
Measure-Command { Invoke-RestMethod "$env:SERVICE_URL/slow" }
```

Expected:

```text
About 2 seconds
```

## 17. Run Expo App Against Cloud Run

Open a new PowerShell window.

Run:

```powershell
cd "<path-to>\mobile-platform-reliability-lab\mobile"
$env:EXPO_PUBLIC_API_URL="<paste-your-cloud-run-url-here>"
npm run web
```

Example:

```powershell
$env:EXPO_PUBLIC_API_URL="https://mobile-platform-api-abc123-nn.a.run.app"
npm run web
```

What to show:

1. The app title: `Demo Mobile Client`.
2. API base URL showing the Cloud Run URL.
3. Click `API health check`.
4. Click `Fetch accounts`.
5. Click `Make demo payment`.
6. Explain loading/success/error states.

Demo wording:

> This is an Expo React Native TypeScript app. I am showing it through Expo Web for demo reliability on Windows. The API URL is configured through an environment variable and points to the Cloud Run backend. The same app code structure is intended for mobile targets, while native iOS builds require macOS and Android can run through emulator/Expo tooling.

## 18. What If CORS Fails

Symptom:

```text
Browser console shows CORS error
```

Fix:

The backend already supports CORS through:

```text
ALLOWED_ORIGINS
```

For demo, redeploy with:

```powershell
gcloud run services update $env:SERVICE_NAME `
  --region $env:REGION `
  --set-env-vars ALLOWED_ORIGINS="*"
```

Production note:

> Do not use wildcard CORS casually in production. Restrict origins to approved app/web origins.

## 19. What If Deploy Fails

### Docker Push Denied

Check:

```powershell
gcloud auth configure-docker "$env:REGION-docker.pkg.dev"
gcloud config get-value project
```

Likely issue:

- Docker not authenticated.
- Wrong project.
- Missing Artifact Registry permissions.

### Cloud Run Service Fails To Start

Check logs:

```powershell
gcloud run services logs read $env:SERVICE_NAME --region $env:REGION --limit 50
```

Likely issue:

- Container did not listen on expected port.
- Startup command failed.
- Missing dependency.

Our mitigation:

> Dockerfile uses `${PORT:-8000}` and passed local `PORT=8080` smoke test.

### API Returns 500

Check:

```powershell
gcloud run services logs read $env:SERVICE_NAME --region $env:REGION --limit 50
```

Then test:

```powershell
Invoke-RestMethod "$env:SERVICE_URL/health"
Invoke-RestMethod "$env:SERVICE_URL/accounts"
```

### Expo App Cannot Reach API

Check:

- Is `EXPO_PUBLIC_API_URL` set to Cloud Run URL?
- Does `/health` work in browser?
- Is CORS enabled?
- Are you using `https://`, not `http://`?

## 20. Optional: Deploy Gateway Simulator Later

Do not do this first.

Primary demo:

```text
Expo app -> Cloud Run backend
```

Optional advanced demo:

```text
Expo app -> Cloud Run gateway simulator -> Cloud Run backend
```

This would require:

- Dockerfile for gateway.
- Gateway Cloud Run service.
- `BACKEND_BASE_URL` set to backend Cloud Run URL.
- Mobile app pointed to gateway routes or API client adjusted.

Recommendation:

> Skip gateway deployment until the backend demo is working and you have extra time. Use the local gateway simulator for API management discussion.

## 21. Cleanup

Delete Cloud Run service:

```powershell
gcloud run services delete $env:SERVICE_NAME --region $env:REGION
```

Delete Artifact Registry repository:

```powershell
gcloud artifacts repositories delete $env:REPOSITORY --location $env:REGION
```

Optional API disable:

```powershell
gcloud services disable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com
```

Billing check:

```text
Google Cloud Console -> Billing -> Reports
```

## 22. How To Explain The Demo

Short explanation:

> I deployed the backend container to Cloud Run to prove the lab works outside my local machine. The image was built locally, pushed to Artifact Registry, deployed to Cloud Run, and then the Expo app was configured with the Cloud Run URL. This demonstrates the path from mobile app to cloud API, while the Kubernetes manifests show how the same container could be discussed in a GKE context.

If they ask why not GKE:

> I prepared Kubernetes manifests and validated them with Kustomize, but for a short live demo I chose Cloud Run because it proves the container works in GCP with less cost and operational risk. GKE would be the next step if the team needs Kubernetes-level controls.

If they ask what failed or what you learned:

> I made the backend Cloud Run ready by ensuring it listens on the injected `PORT` environment variable and enabling CORS for the Expo Web demo. This is a realistic deployment lesson: local containers can work but still need cloud-runtime details handled correctly.

## 23. GitHub Actions Deployment Flow

The repo includes a manual deployment workflow:

```text
.github/workflows/cloud-run-deploy.yml
```

Purpose:

```text
GitHub Actions -> build Docker image -> push Artifact Registry -> deploy Cloud Run
```

Why it is manual:

- A learning lab should not deploy to cloud on every commit.
- Manual `workflow_dispatch` gives controlled deployment.
- The CI workflow validates code on pull request or push.
- The deployment workflow is run only when you intentionally want a cloud release.

Security model:

- No real GCP credentials are committed.
- The workflow expects GitHub secrets for Google Cloud authentication.
- The preferred production pattern is GitHub OIDC / Workload Identity Federation instead of a long-lived service account JSON key.

Expected GitHub secrets:

```text
GCP_WORKLOAD_IDENTITY_PROVIDER
GCP_SERVICE_ACCOUNT
```

Expected GitHub repository variables:

```text
GCP_PROJECT_ID
GCP_REGION
ARTIFACT_REPOSITORY
```

Explanation:

> The CI workflow proves the code is safe to merge by running tests, lint, Docker build, mobile TypeScript checks, mobile lint, Kubernetes rendering, gateway tests, and automation tests. The separate deployment workflow is manually triggered and builds the backend image, pushes it to Artifact Registry, and deploys it to Cloud Run. In a real team, I would protect this workflow with branch rules, approvals, least-privilege IAM, and environment-specific secrets.

## 24. Runtime Secret Manager Integration

The Cloud Run deployment workflow injects a demo runtime secret from Secret Manager:

```text
DEMO_RUNTIME_SECRET=demo-runtime-secret:latest
```

Purpose:

- Keep runtime secrets out of source code.
- Keep secrets out of Docker images.
- Let Cloud Run read secrets at runtime through IAM.
- Let the app verify secret configuration without exposing the value.

The `/health` endpoint reports only whether the secret exists:

```json
{
  "status": "ok",
  "service": "mobile-platform-reliability-api",
  "runtime_secret_configured": true
}
```

The secret value is never printed by the API.

Explanation:

> Runtime secrets should come from a secret vault such as GCP Secret Manager. The app should not log or return secret values. For this lab, Cloud Run receives a fake demo secret and the health endpoint only confirms whether runtime secret configuration is present.
