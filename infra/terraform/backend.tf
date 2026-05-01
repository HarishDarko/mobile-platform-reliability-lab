terraform {
  backend "gcs" {
    bucket = "replace-with-your-terraform-state-bucket"
    prefix = "mobile-platform-reliability-lab"
  }
}
