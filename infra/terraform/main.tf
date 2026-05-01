locals {
  runtime_service_account_id = "cloud-run-runtime"
}

resource "google_project_service" "required" {
  for_each = toset([
    "artifactregistry.googleapis.com",
    "container.googleapis.com",
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

resource "google_service_account" "cloud_run_runtime" {
  account_id   = local.runtime_service_account_id
  display_name = "Cloud Run runtime"
  description  = "Runtime identity for the lab Cloud Run service."
}

resource "google_artifact_registry_repository_iam_member" "deployer_can_push_images" {
  location   = google_artifact_registry_repository.backend_images.location
  repository = google_artifact_registry_repository.backend_images.name
  role       = "roles/artifactregistry.writer"
  member     = "serviceAccount:${var.github_deployer_service_account_email}"
}

resource "google_project_iam_member" "deployer_can_manage_cloud_run" {
  project = var.project_id
  role    = "roles/run.admin"
  member  = "serviceAccount:${var.github_deployer_service_account_email}"
}

resource "google_service_account_iam_member" "deployer_can_use_runtime_identity" {
  service_account_id = google_service_account.cloud_run_runtime.name
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:${var.github_deployer_service_account_email}"
}

resource "google_secret_manager_secret_iam_member" "runtime_can_access_demo_secret" {
  project   = var.project_id
  secret_id = google_secret_manager_secret.demo_runtime_secret.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.cloud_run_runtime.email}"
}

resource "google_container_cluster" "autopilot" {
  count = var.enable_gke_autopilot ? 1 : 0

  name                = var.gke_cluster_name
  location            = var.region
  enable_autopilot    = true
  deletion_protection = false

  release_channel {
    channel = "REGULAR"
  }

  depends_on = [google_project_service.required]
}
