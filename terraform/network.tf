# terraform/network.tf

data "google_compute_network" "default_network" {
  name = "default"
}

resource "google_compute_firewall" "allow_api_ingress" {
  name    = "${var.naming_prefix}-allow-api-ingress"
  network = data.google_compute_network.default_network.id
  allow {
    protocol = "tcp"
    ports    = ["80", "443"]
  }
  source_ranges = ["0.0.0.0/0"] # Adjust if using LB
  target_tags   = ["${var.naming_prefix}-api-vm-${var.environment}"]
}

resource "google_compute_firewall" "allow_ssh_ingress" {
  count   = length(var.allow_ssh_ips) > 0 ? 1 : 0
  name    = "${var.naming_prefix}-allow-ssh-ingress"
  network = data.google_compute_network.default_network.id
  allow {
    protocol = "tcp"
    ports    = ["22"]
  }
  source_ranges = var.allow_ssh_ips
  target_tags   = ["${var.naming_prefix}-api-vm-${var.environment}"]
}

# Get Google Cloud health checker IP ranges
data "google_netblock_ip_ranges" "health_checkers" {
  range_type = "health-checkers"
}

data "google_netblock_ip_ranges" "legacy_health_checkers" {
  range_type = "legacy-health-checkers"
}

# Firewall rule to allow GCP health checks to reach the API VM
resource "google_compute_firewall" "allow_gcp_health_checks_to_api" {
  project = var.project_id
  name    = "${var.naming_prefix}-allow-gcp-health-checks-api"
  network = data.google_compute_network.default_network.id

  allow {
    protocol = "tcp"
    ports    = ["80", "443"] # Ensure these match your API VM's listening ports
  }

  source_ranges = concat(
    data.google_netblock_ip_ranges.health_checkers.cidr_blocks_ipv4,
    data.google_netblock_ip_ranges.legacy_health_checkers.cidr_blocks_ipv4
  )

  target_tags = ["${var.naming_prefix}-api-vm-${var.environment}"] # Ensure your API VM has this tag

  description = "Allow ingress from GCP health checkers to API VMs."
}
