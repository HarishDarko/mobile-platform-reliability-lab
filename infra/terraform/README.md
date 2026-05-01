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
- Dedicated GitHub deployer service account.
- Dedicated Cloud Run runtime service account.
- IAM permissions for deploy and runtime access.
- Workload Identity Federation pool/provider for GitHub Actions OIDC.

GitHub Actions remains responsible for application release:

```text
GitHub Actions -> Docker build -> Artifact Registry push -> Cloud Run deploy
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

## Production Notes

For a real team:

- Use a remote backend such as GCS for Terraform state.
- Enable state locking where supported.
- Restrict access to state because it may contain sensitive metadata.
- Separate dev, test, and production variables/state.
- Review `terraform plan` in pull requests before apply.
- Use least-privilege IAM and resource-level bindings where practical.

## Explanation

> In this lab I first used `gcloud` manually to understand the working deployment path. I then moved application deployment into GitHub Actions. Terraform is added as the next IaC layer to describe the repeatable cloud foundation: APIs, Artifact Registry, Secret Manager, service accounts, IAM, and Workload Identity Federation. I intentionally keep secret values out of Terraform and avoid mixing Terraform ownership with CI/CD image updates unless that ownership model is clearly defined.
