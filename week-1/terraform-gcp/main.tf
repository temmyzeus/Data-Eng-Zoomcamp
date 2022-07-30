terraform {
  backend "local" {}
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "4.30.0"
    }
  }
}

provider "google" {
  # Configuration options
  project = var.project_id
  region  = var.region
}

resource "google_storage_bucket" "data-lake-bucket" {
  name     = "data-lake-${var.project_id}"
  location = var.region

  project                     = var.project_id
  uniform_bucket_level_access = true

  storage_class = "STANDARD"

  versioning {
    enabled = true
  }

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 30 // 30 days
    }
  }
  force_destroy = true
}
