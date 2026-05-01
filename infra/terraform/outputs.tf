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
  description = "Service account GitHub Actions can impersonate."
  value       = google_service_account.github_deployer.email
}

output "workload_identity_provider" {
  description = "Provider resource name for google-github-actions/auth."
  value       = google_iam_workload_identity_pool_provider.github.name
}
