locals {
  deployer_service_account_id = "github-cloud-run-deployer"
  runtime_service_account_id  = "cloud-run-runtime"
}

resource "google_project_service" "required" {
  for_each = toset([
    "artifactregistry.googleapis.com",
    "iamcredentials.googleapis.com",
    "run.googleapis.com",
    "secretmanager.googleapis.com",
    "sts.googleapis.com",
  ])

  project            = var.project_id
  service            = each.value
  disable_on_destroy = false
}

resource "google_artifact_registry_repository" "backend_images" {
  location      = var.region
  repository_id = var.artifact_repository_id
  description   = "Container images for the mobile platform reliability lab."
  format        = "DOCKER"

  depends_on = [google_project_service.required]
}

resource "google_secret_manager_secret" "demo_runtime_secret" {
  secret_id = var.demo_secret_id

  replication {
    auto {}
  }

  depends_on = [google_project_service.required]
}

resource "google_service_account" "github_deployer" {
  account_id   = local.deployer_service_account_id
  display_name = "GitHub Cloud Run deployer"
  description  = "Service account impersonated by GitHub Actions through Workload Identity Federation."
}

resource "google_service_account" "cloud_run_runtime" {
  account_id   = local.runtime_service_account_id
  display_name = "Cloud Run runtime"
  description  = "Runtime identity for the lab Cloud Run service."
}

resource "google_artifact_registry_repository_iam_member" "deployer_can_push_images" {
  location   = google_artifact_registry_repository.backend_images.location
  repository = google_artifact_registry_repository.backend_images.name
  role       = "roles/artifactregistry.writer"
  member     = "serviceAccount:${google_service_account.github_deployer.email}"
}

resource "google_project_iam_member" "deployer_can_manage_cloud_run" {
  project = var.project_id
  role    = "roles/run.admin"
  member  = "serviceAccount:${google_service_account.github_deployer.email}"
}

resource "google_service_account_iam_member" "deployer_can_use_runtime_identity" {
  service_account_id = google_service_account.cloud_run_runtime.name
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:${google_service_account.github_deployer.email}"
}

resource "google_secret_manager_secret_iam_member" "runtime_can_access_demo_secret" {
  project   = var.project_id
  secret_id = google_secret_manager_secret.demo_runtime_secret.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.cloud_run_runtime.email}"
}

resource "google_iam_workload_identity_pool" "github_actions" {
  workload_identity_pool_id = var.workload_identity_pool_id
  display_name              = "GitHub Actions Pool"
  description               = "OIDC identity pool for GitHub Actions deployments."

  depends_on = [google_project_service.required]
}

resource "google_iam_workload_identity_pool_provider" "github" {
  workload_identity_pool_id          = google_iam_workload_identity_pool.github_actions.workload_identity_pool_id
  workload_identity_pool_provider_id = var.workload_identity_provider_id
  display_name                       = "GitHub repository provider"
  description                        = "Restricts GitHub OIDC trust to the configured repository."

  attribute_mapping = {
    "google.subject"             = "assertion.sub"
    "attribute.actor"            = "assertion.actor"
    "attribute.repository"       = "assertion.repository"
    "attribute.repository_owner" = "assertion.repository_owner"
  }

  attribute_condition = "assertion.repository == '${var.github_repository}'"

  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }
}

resource "google_service_account_iam_member" "github_repo_can_impersonate_deployer" {
  service_account_id = google_service_account.github_deployer.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github_actions.name}/attribute.repository/${var.github_repository}"
}
