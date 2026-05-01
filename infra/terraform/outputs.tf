output "artifact_repository_id" {
  description = "Artifact Registry repository ID."
  value       = google_artifact_registry_repository.backend_images.repository_id
}

output "cloud_run_runtime_service_account" {
  description = "Dedicated Cloud Run runtime service account."
  value       = google_service_account.cloud_run_runtime.email
}

output "demo_secret_id" {
  description = "Secret Manager secret ID. Secret values are intentionally not managed here."
  value       = google_secret_manager_secret.demo_runtime_secret.secret_id
}

output "github_deployer_service_account" {
  description = "Existing bootstrap service account used by GitHub Actions."
  value       = var.github_deployer_service_account_email
}
