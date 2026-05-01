variable "project_id" {
  description = "GCP project ID where lab infrastructure should be provisioned."
  type        = string
}

variable "region" {
  description = "GCP region for regional resources."
  type        = string
  default     = "northamerica-northeast1"
}

variable "artifact_repository_id" {
  description = "Artifact Registry repository ID for backend container images."
  type        = string
  default     = "mobile-platform-lab"
}

variable "demo_secret_id" {
  description = "Secret Manager secret ID used by Cloud Run runtime configuration."
  type        = string
  default     = "demo-runtime-secret"
}

variable "github_repository" {
  description = "GitHub repository allowed to impersonate the deployer service account, in owner/name form."
  type        = string
}

variable "workload_identity_pool_id" {
  description = "Workload Identity Pool ID for GitHub Actions OIDC."
  type        = string
  default     = "github-actions"
}

variable "workload_identity_provider_id" {
  description = "Workload Identity Pool Provider ID for GitHub Actions OIDC."
  type        = string
  default     = "github"
}
