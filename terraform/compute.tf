# terraform/compute.tf

resource "google_compute_address" "api_static_ip" {
  count        = 1  # Create for both dev and prod environments now
  name         = "${var.naming_prefix}-api-ip-${var.environment}"
  project      = var.project_id
  region       = var.region
  network_tier = var.environment == "prod" ? "PREMIUM" : "STANDARD"  # Use STANDARD tier for dev to reduce costs
}

resource "google_compute_instance_template" "api_template" {
  project      = var.project_id
  name_prefix  = "${var.naming_prefix}-api-tpl-${var.environment}-"
  machine_type = var.api_vm_machine_type
  region       = var.region

  disk {
    source_image = "debian-cloud/debian-11"
    auto_delete  = true
    boot         = true
    disk_size_gb = 20
  }

  network_interface {
    network = data.google_compute_network.default_network.id
    access_config {
      nat_ip       = google_compute_address.api_static_ip[0].address  # Always use static IP now
      network_tier = var.environment == "prod" ? "PREMIUM" : "STANDARD"  # Match network tier with the static IP
    }
  }

  service_account {
    email  = google_service_account.api_service_account.email
    scopes = ["cloud-platform"]
  }

  tags = ["${var.naming_prefix}-api-vm-${var.environment}", "http-server", "https-server"]

  metadata = {
    # Pass variables needed by startup script
    environment   = var.environment
    naming_prefix = var.naming_prefix
    region        = var.region
  }
  metadata_startup_script = file("${path.module}/scripts/startup-api.sh")

  lifecycle { create_before_destroy = true }
}

resource "google_compute_instance_group_manager" "api_igm" {
  project            = var.project_id
  name               = "${var.naming_prefix}-api-igm-${var.environment}"
  zone               = var.zone
  base_instance_name = "${var.naming_prefix}-api-vm-${var.environment}"
  target_size        = 1

  version {
    instance_template = google_compute_instance_template.api_template.id
  }
}

# Add optional Load Balancer resources here if needed for prod
