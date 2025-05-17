# Terraform Security Overview

This document outlines the security measures implemented in the Concept Visualizer infrastructure and provides guidance on secure operations.

## Security Architecture

The Concept Visualizer infrastructure follows a defense-in-depth approach with multiple security layers:

### Identity and Access Management

- **Service Accounts**: Each component uses dedicated service accounts with minimal privileges

  - API service account: Used by the API VM
  - Worker service account: Used by Cloud Functions
  - CI/CD service account: Used for deployment via GitHub Actions

- **Workload Identity Federation**: Allows GitHub Actions to authenticate as GCP service accounts without using service account keys

  - Eliminates the need for long-lived credentials
  - Restricts permissions to specific repositories and actions

- **Principle of Least Privilege**: All service accounts are granted only the permissions they need
  - API service account: Access to specific secrets, Pub/Sub
  - Worker service account: Access to specific secrets, Pub/Sub, storage
  - CI/CD service account: Access to deployment-related services only

### Network Security

- **VPC Network**: Dedicated Virtual Private Cloud for resources

  - Isolation from other GCP projects

- **Firewall Rules**: Restrictive rules that only allow necessary traffic

  - Allow HTTP/HTTPS to API VM (ports 80, 443)
  - Allow health check traffic
  - Allow SSH from authorized IPs only (configurable)

- **External Access**: Limited external IP addresses
  - Only the API VM has a public IP
  - Cloud Functions are not publicly accessible

### Data Protection

- **Secret Management**: All sensitive credentials stored in Google Secret Manager

  - API keys, database credentials, JWT secrets
  - IAM-based access control to secrets
  - No secrets stored in code or Terraform state

- **Encryption**:
  - Secrets encrypted at rest and in transit
  - Database communication encrypted with TLS
  - API uses HTTPS for communication

### Operational Security

- **Logging and Monitoring**:
  - Centralized logging for all components
  - Alert policies for security-relevant events
  - Uptime monitoring for critical endpoints

## Security Best Practices

### Credential Management

1. **Rotate Credentials Regularly**:

   - Database credentials
   - API keys
   - JWT secret

2. **Use Temporary Credentials**:

   - For development and operational tasks
   - Avoid long-lived access keys

3. **Restrict Access to Secrets**:
   - Only grant access to services that need specific secrets
   - Review secret access regularly

### Network Security

1. **Use IP Restrictions**:

   - Limit SSH access to VMs to specific IPs
   - Use VPN when applicable for administrative access

2. **Implement HTTPS**:

   - Always use HTTPS for API communication
   - Consider adding a load balancer with SSL termination for production

3. **Regular Firewall Audits**:
   - Review and update firewall rules
   - Remove unnecessary access

### Infrastructure Security

1. **Regular Updates**:

   - Keep base VM images updated
   - Apply security patches promptly
   - Update dependencies in Docker images

2. **Vulnerability Scanning**:

   - Scan Docker images for vulnerabilities
   - Use Container Analysis API to scan images in Artifact Registry

3. **Secure CI/CD**:
   - Review GitHub Actions workflows
   - Secure GitHub repository settings
   - Implement branch protection rules

## Security Configurations in Terraform

### Service Account Configuration (`iam.tf`)

Service accounts are created with minimal permissions:

```hcl
# Example from iam.tf
resource "google_service_account" "api_service_account" {
  account_id   = "${var.naming_prefix}-api-sa-${terraform.workspace}"
  display_name = "Concept API Service Account ${terraform.workspace}"
  description  = "Service account for the API VM"
  project      = var.project_id
}

# Only grant necessary permissions
resource "google_project_iam_member" "api_sa_secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.api_service_account.email}"
}
```

### Secret Management (`secrets.tf`)

Secrets are created in Secret Manager with restricted access:

```hcl
# Example from secrets.tf
resource "google_secret_manager_secret" "supabase_url" {
  secret_id = "${var.naming_prefix}-supabase-url-${terraform.workspace}"
  project   = var.project_id

  replication {
    automatic = true
  }
}

# Grant access to specific service accounts only
resource "google_secret_manager_secret_iam_member" "api_sa_can_access_secrets" {
  project   = var.project_id
  secret_id = google_secret_manager_secret.supabase_url.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.api_service_account.email}"
}
```

### Network Security (`network.tf`)

Firewall rules restrict access to the necessary ports:

```hcl
# Example from network.tf
resource "google_compute_firewall" "allow_http" {
  name    = "${var.naming_prefix}-allow-http-${terraform.workspace}"
  network = google_compute_network.vpc_network.name
  project = var.project_id

  allow {
    protocol = "tcp"
    ports    = ["80", "443"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["http-server"]
}

resource "google_compute_firewall" "allow_ssh" {
  name    = "${var.naming_prefix}-allow-ssh-${terraform.workspace}"
  network = google_compute_network.vpc_network.name
  project = var.project_id

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  # Restrict SSH access to specific IP ranges
  source_ranges = var.ssh_allowed_ips
  target_tags   = ["ssh"]
}
```

## Security Hardening Recommendations

### Further Hardening Steps

1. **API Security**:

   - Implement API rate limiting
   - Consider adding Web Application Firewall (WAF)
   - Use OAuth or another strong authentication method

2. **VM Hardening**:

   - Implement OS hardening
   - Install intrusion detection system
   - Use shielded VMs

3. **Network Security**:

   - Consider implementing a VPC Service Controls perimeter
   - Use Private Google Access for Cloud APIs
   - Implement network ingress/egress monitoring

4. **Data Protection**:
   - Implement data encryption at application level
   - Set up regular database backups
   - Implement data access logging and monitoring

## Security Incident Response

### Preparing for Security Incidents

1. **Create an Incident Response Plan**:

   - Define roles and responsibilities
   - Establish communication channels
   - Document response procedures

2. **Ensure Proper Logging**:

   - Enable audit logging
   - Set up log retention policies
   - Consider exporting logs to a secure storage bucket

3. **Prepare Recovery Procedures**:
   - Document steps to restore from backups
   - Create procedures for revoking compromised credentials
   - Establish guidelines for post-incident analysis

## Compliance Considerations

The infrastructure can be configured to meet various compliance requirements:

- **GDPR**: Ensure proper data handling and processing records
- **HIPAA**: Additional controls needed for health information
- **SOC 2**: Controls around security, availability, and confidentiality

## Next Steps

- Review the [Monitoring Guide](monitoring.md) for security monitoring setup
- Check the [Operations Guide](operations.md) for secure operational procedures
- Consider implementing additional security tools and controls based on your specific requirements
