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
  description = "GitHub repository that deploys the lab, in owner/name form. Used for documentation and future policy expansion."
  type        = string
}

variable "github_deployer_service_account_email" {
  description = "Existing bootstrap service account email used by GitHub Actions for deployment."
  type        = string
}
