# Terraform GCP Foundation

This folder shows how the cloud foundation for the lab can be described as Infrastructure as Code.

It is intentionally safe for a public repository:

- No real project ID is committed.
- No secret values are committed.
- No service account JSON key is created.
- Secret Manager metadata is managed, but secret versions/values are not.

## What Terraform Owns

Terraform is responsible for foundational cloud resources:

- Required GCP APIs.
- Artifact Registry repository for Docker images.
- Secret Manager secret metadata.
- Dedicated Cloud Run runtime service account.
- IAM permissions for deploy and runtime access.
- IAM access for an existing GitHub Actions deployer service account.
- Remote Terraform state in GCS is used by GitHub Actions, but the state bucket itself is a one-time bootstrap resource.

Terraform intentionally does not own the GitHub OIDC bootstrap resources:

- Workload Identity Pool.
- Workload Identity Provider.
- GitHub deployer service account creation.
- GitHub Actions secrets and variables.

Those bootstrap resources must exist before GitHub Actions can run Terraform.

`backend.tf` contains a non-secret placeholder bucket so Terraform validation works in CI. The GitHub Actions workflows override that placeholder at runtime using these repository variables and secrets:

- Variable: `GCP_PROJECT_ID`
- Variable: `GCP_REGION`
- Variable: `ARTIFACT_REPOSITORY`
- Variable: `TF_STATE_BUCKET`
- Secret: `GCP_WORKLOAD_IDENTITY_PROVIDER`
- Secret: `GCP_SERVICE_ACCOUNT`
- Secret: `DEMO_RUNTIME_SECRET_VALUE`

GitHub Actions remains responsible for application release:

```text
GitHub Actions -> Docker build -> Artifact Registry push -> Cloud Run deploy
```

Manual workflow order:

```text
Terraform Plan
-> Terraform Apply
-> Deploy Backend To Cloud Run
-> verify /health
-> delete Cloud Run service
-> Terraform Destroy
```

## Why Cloud Run Service Is Not Managed Here

The lab currently deploys Cloud Run with GitHub Actions using `gcloud run deploy`.

Terraform can manage Cloud Run services, but mixing Terraform-managed service definitions with image updates from CI/CD can create drift unless the team defines a clear ownership model.

For this lab:

```text
Terraform = foundation provisioning
GitHub Actions = application deployment
Ansible = configuration automation for operational scripts
```

That split keeps the project architecture clear and avoids pretending a larger platform process is complete.

## Usage

Copy the example variables file:

```powershell
cd infra\terraform
Copy-Item terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` with your own project and GitHub repository values.

Initialize and validate:

```powershell
terraform init
terraform fmt -check
terraform validate
```

Plan:

```powershell
terraform plan
```

Apply only if you intentionally want Terraform to create or manage these resources:

```powershell
terraform apply
```

The GitHub Actions `Terraform Apply` workflow also adds a fake demo secret version after the secret metadata is created. Real teams should use approved secret loading or rotation processes rather than storing secret values in Terraform.

Before destroying the foundation, delete the Cloud Run service that uses the Artifact Registry image and Secret Manager secret.

## Production Notes

For a real team:

- Use a remote backend such as GCS for Terraform state. This lab uses a GCS backend configured at workflow runtime.
- Enable state locking where supported.
- Restrict access to state because it may contain sensitive metadata.
- Separate dev, test, and production variables/state.
- Review `terraform plan` in pull requests before apply.
- Use least-privilege IAM and resource-level bindings where practical.

## Explanation

> In this lab I first used `gcloud` manually to understand the working deployment path. I then moved application deployment into GitHub Actions. Terraform is added as the next IaC layer to describe the repeatable app foundation: APIs, Artifact Registry, Secret Manager metadata, runtime identity, and IAM. I intentionally keep secret values out of Terraform and leave GitHub OIDC bootstrap outside this module so GitHub Actions can use Terraform to recreate the app foundation safely.
