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
