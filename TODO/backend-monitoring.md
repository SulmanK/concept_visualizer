Okay, let's create a full design plan for your backend health monitoring, focusing on the GCP Uptime Checks and Alerting Policies with a startup grace period.

## Backend Health Monitoring Design Plan

**1. Objective:**

- Implement robust health monitoring for the backend API service running on a GCP Compute Engine VM.
- Ensure the API is reachable and responsive via its designated health endpoint (e.g., `/api/health/ping`).
- Configure alerts to notify relevant personnel of sustained API unavailability or health check failures.
- Incorporate a "grace period" into the alerting logic to prevent false alarms during initial VM/application startup or deployments.

**2. Components Involved (GCP Services):**

- **Compute Engine:** Hosts the API VM. We'll need its external IP address.
- **Cloud Monitoring:**
  - **Uptime Checks:** To periodically send requests to the API's health endpoint.
  - **Alerting Policies:** To define conditions under which an alert is triggered based on uptime check results.
  - **Notification Channels:** To specify how alerts are delivered (e.g., email).
- **Cloud Logging:** (Implicitly) Uptime check results and alert incidents are logged here.
- **Terraform:** To define and manage these GCP resources as Infrastructure as Code.

**3. Monitoring Strategy:**

1.  **Uptime Check Configuration:**

    - A GCP Uptime Check will be configured to target the static external IP address of your API VM.
    - It will send HTTP GET requests to the `/api/health/ping` endpoint (or your chosen health endpoint).
    - It will expect an HTTP 200 OK response.
    - Checks will be performed at regular intervals (e.g., every 1-5 minutes).

2.  **Alerting Policy Configuration:**
    - An Alerting Policy will monitor the `check_passed` metric from the Uptime Check.
    - **Condition:** The alert will trigger if the fraction of successful health checks over a defined `alignment_period` (e.g., 5 minutes) drops below a certain threshold (e.g., 90%).
    - **Grace Period (Startup Delay):** This is achieved by setting the `duration` for the alert condition. The "unhealthy" condition (low success rate) must persist for this entire `duration` (e.g., 10-15 minutes) before an alert is fired. This provides the necessary time for your VM and API container to fully initialize after a deployment or restart.
    - **Notification:** If an alert is triggered, a notification will be sent to the configured email channel.

**4. Terraform Implementation Details:**

We will add/modify resources in your `terraform/` directory.

**a. Variables (`terraform/variables.tf`):**

```terraform
# Add this new variable
variable "api_startup_alert_delay" {
  description = "The duration (e.g., '600s') a failing health check condition must persist before an alert is triggered. Acts as an initial grace period after VM/API setup."
  type        = string
  default     = "600s" # Default to 10 minutes, adjust as needed
}

# Ensure these existing variables are present if not already
variable "alert_email_address" {
  description = "The email address to send monitoring alerts to."
  type        = string
}

variable "alert_alignment_period" {
  description = "The alignment period for alerts (e.g., '300s' for 5 minutes)."
  type        = string
  default     = "300s"
}

# You might already have this from the task failure alert
# variable "alert_duration" { ... }
# If so, consider if you want a separate duration for API health vs task failures.
# For clarity, we use api_startup_alert_delay specifically for this uptime alert.
```

**b. Uptime Check and Alert Policy (`terraform/monitoring.tf`):**

```terraform
# Ensure you have a notification channel defined (you likely do from previous setup)
# resource "google_monitoring_notification_channel" "email_alert_channel" { ... }

# --- API Health Uptime Check ---
resource "google_monitoring_uptime_check_config" "api_health_ping" {
  project      = var.project_id
  display_name = "${var.naming_prefix}-api-health-ping-${var.environment}"
  timeout      = "10s" # How long each ping waits for a response

  http_check {
    path           = "/api/health/ping" # Or your specific health endpoint path
    port           = "80"               # Port your API listens on (e.g., 80 for HTTP, 443 for HTTPS)
    use_ssl        = false              # Set to true if your API VM serves HTTPS and terminates SSL itself
    request_method = "GET"
    # Optional: Validate response content for more robust checks
    # content_matchers {
    #   content = "{\"status\":\"ok\"}" # Ensure this matches your /api/health/ping response
    #   matcher = "MATCHES_JSON_PATH"
    #   json_path_matcher {
    #     json_path    = "$.status"
    #     json_matcher = "EXACT_MATCH"
    #   }
    # }
  }

  # Target the static IP address of your API VM
  monitored_resource {
    type = "uptime_url"
    labels = {
      # This references the static IP resource defined in your compute.tf
      host = google_compute_address.api_static_ip[0].address
    }
  }

  period = "60s" # How often GCP pings your API (e.g., every 60 seconds)
  # Consider adding 'selected_regions' if you want checks from specific locations
}

# --- Alert Policy for API Health Ping Failures ---
resource "google_monitoring_alert_policy" "api_health_ping_failure_alert" {
  project      = var.project_id
  display_name = "${var.naming_prefix}-api-ping-fails-al-${var.environment}"
  combiner     = "OR" # For a single condition

  conditions {
    display_name = "API Health Ping Unsuccessful (Sustained)"
    condition_threshold {
      filter = "metric.type=\"monitoring.googleapis.com/uptime_check/check_passed\" AND resource.type=\"uptime_url\" AND resource.label.check_id==\"${google_monitoring_uptime_check_config.api_health_ping.uptime_check_id}\""

      # Aggregation defines how data points are processed
      aggregations {
        # Group data points into these windows for evaluation.
        alignment_period   = var.alert_alignment_period # e.g., "300s" (5 minutes)
        # Within each alignment_period, calculate the fraction of successful checks.
        # 'check_passed' is 1 if passed, 0 if failed. ALIGN_FRACTION_TRUE gives success rate (0.0 to 1.0).
        per_series_aligner = "ALIGN_FRACTION_TRUE"
      }

      # Condition for triggering an alert
      comparison      = "COMPARISON_LT" # Alert if success rate is LESS THAN...
      threshold_value = 0.9             # ...0.9 (i.e., less than 90% success rate).
                                        # This means if >10% of pings fail in an alignment_period, condition is true.
                                        # For a 60s ping period and 300s alignment, 1 failed ping out of 5 makes it 0.8.

      # This is the "grace period" for startup
      duration = var.api_startup_alert_delay # e.g., "600s" (10 minutes).
                                             # The "unhealthy" condition (pass rate < 90%)
                                             # must persist for this entire duration before an alert fires.

      trigger {
        count = 1 # Trigger if the condition (failing for 'duration') occurs once
      }
    }
  }

  alert_strategy {
    auto_close = "86400s" # Auto-close incidents after 1 day if the issue is resolved
  }

  notification_channels = [
    google_monitoring_notification_channel.email_alert_channel.id, # Reference your existing channel
  ]

  documentation {
    content = <<-EOT
### API Health Ping Failure Alert (${var.environment})

**Summary:** The API health ping endpoint (`http://${google_compute_address.api_static_ip[0].address}:80/api/health/ping`)
has been failing or responding too slowly for a sustained period of **${var.api_startup_alert_delay}**.

**Uptime Check ID:** `${google_monitoring_uptime_check_config.api_health_ping.uptime_check_id}`
**Condition:** Success rate less than 90% over a ${var.alert_alignment_period} window, persisting for ${var.api_startup_alert_delay}.

**Possible Causes:**
*   The API VM instance is down, unresponsive, or still initializing after a deployment/restart.
*   The API application (FastAPI container) is not running, has crashed, or is taking too long to start.
*   Network issues preventing access to the VM.
*   Firewall rules blocking GCP Uptime Checkers.
*   Errors in the API's startup script (`startup-api.sh`).
*   Resource exhaustion on the VM (CPU, Memory, Disk).

**Recommended Actions:**
1.  **Verify VM Status:** Check the API VM instance status in the GCP Compute Engine console.
2.  **Check API Application Logs:**
    *   SSH into the VM and check Docker logs: `sudo docker logs concept-api`
    *   Review logs in Cloud Logging, filtering by `resource.type="gce_instance"` and your instance name/ID.
3.  **Check Startup Script Logs:** On the VM, check `/var/log/startup-script.log` (or similar, depending on OS) for errors during startup.
4.  **Review Firewall Rules:** Ensure GCP firewall rules allow ingress from Google Cloud health checker IP ranges to port 80 (or 443 if using HTTPS) on your API VM.
5.  **Check Uptime Check Details:** In Google Cloud Monitoring, review the specific uptime check configuration and its recent check results for more detailed error information.
6.  **Test Manually:** Try accessing `http://${google_compute_address.api_static_ip[0].address}:80/api/health/ping` from your own machine or another GCP VM.
EOT
    mime_type = "text/markdown"
  }

  user_labels = {
    environment = var.environment
    service     = "${var.naming_prefix}-api"
    tier        = "backend"
  }

  # Ensure dependencies are created in the correct order
  depends_on = [
    google_monitoring_uptime_check_config.api_health_ping,
    google_monitoring_notification_channel.email_alert_channel,
    google_compute_address.api_static_ip, # Depends on the static IP resource
  ]
}
```

**c. Firewall Rule for Uptime Checks (add to `terraform/network.tf` or ensure it exists):**

GCP Uptime Checkers need to be ableto reach your VM.
**Important:** For production, you should restrict `source_ranges` to Google's official health checker IP ranges. You can get these ranges programmatically or from GCP documentation. For development, `0.0.0.0/0` might be acceptable temporarily, but it's not secure for production.

```terraform
# terraform/network.tf

# ... existing firewall rules ...

data "google_netblock_ip_ranges" "health_checkers" {
  range_type = "health-checkers"
}

data "google_netblock_ip_ranges" "legacy_health_checkers" {
  range_type = "legacy-health-checkers"
}

resource "google_compute_firewall" "allow_gcp_health_checks_to_api" {
  project = var.project_id
  name    = "${var.naming_prefix}-allow-gcp-health-checks-api"
  network = data.google_compute_network.default_network.id # Or your specific VPC

  allow {
    protocol = "tcp"
    ports    = ["80", "443"] # Ensure these match your API VM's listening ports
  }

  source_ranges = concat(
    data.google_netblock_ip_ranges.health_checkers.cidr_blocks_ipv4,
    data.google_netblock_ip_ranges.legacy_health_checkers.cidr_blocks_ipv4
  )
  # This uses data sources to get the official IP ranges for GCP health checkers.

  target_tags = ["${var.naming_prefix}-api-vm-${var.environment}"] # Ensure your API VM has this tag

  description = "Allow ingress from GCP health checkers to API VMs."
}
```

**d. Add outputs for new resources (optional, but good for reference in `terraform/outputs.tf`):**

```terraform
output "api_health_uptime_check_id" {
  description = "The ID of the Uptime Check configuration for the API health."
  value       = google_monitoring_uptime_check_config.api_health_ping.uptime_check_id
}

output "api_health_alert_policy_name" {
  description = "The display name of the Alert Policy for API health failures."
  value       = google_monitoring_alert_policy.api_health_ping_failure_alert.display_name
}
```

**5. Environment Variable Configuration (`terraform/environments/*.tfvars`):**

Update your `dev.tfvars` and `prod.tfvars` (or their examples) to include the new variable:

```terraform
# In terraform/environments/dev.tfvars.example and prod.tfvars.example
# ... other variables ...
api_startup_alert_delay = "600s"  # 10 minutes for dev
# For prod, you might want a slightly longer or shorter delay depending on typical startup
# api_startup_alert_delay = "900s"  # 15 minutes for prod
```

**6. Deployment and Verification:**

1.  **Initialize Terraform:** `terraform init` (if you added new providers like for the `google_netblock_ip_ranges` data source).
2.  **Plan:** `terraform plan -var-file="environments/your_env.tfvars" -out=tfplan`
3.  **Apply:** `terraform apply tfplan` (or use your `gcp_apply.sh` script after checking out the correct branch).
4.  **Verify in GCP Console:**
    - Go to Cloud Monitoring > Uptime Checks. You should see your new uptime check (`${var.naming_prefix}-api-health-ping-${var.environment}`). It might take a few minutes for initial checks to appear.
    - Go to Cloud Monitoring > Alerting. You should see your new alert policy (`${var.naming_prefix}-api-ping-fails-al-${var.environment}`).
    - Check the firewall rules in VPC Network > Firewall to ensure the health checker rule is active.

**7. Alert Details (as configured in `documentation` block):**

When an alert triggers, the notification (e.g., email) will contain:

- A summary indicating the API health ping is failing.
- The specific Uptime Check ID for quick lookup in GCP.
- The target URL being checked.
- Information about the condition that triggered the alert (e.g., success rate < 90% for 10 minutes).
- Possible causes for the failure.
- Recommended actions to diagnose and resolve the issue.

**8. Benefits of this Approach:**

- **Startup Grace Period:** The `duration` in the alert policy effectively prevents alerts during normal startup.
- **Sustained Failure Detection:** Alerts only fire if the API remains unhealthy for a significant period, reducing noise from transient blips.
- **Clear Alerting:** Documentation in the alert policy provides immediate context and troubleshooting steps.
- **Infrastructure as Code:** All monitoring components are managed by Terraform, ensuring consistency and reproducibility.
- **Targeted Monitoring:** Uptime checks directly test the availability of your specific health endpoint.

This plan provides a solid foundation for your backend API health monitoring with the desired startup delay. Remember to adjust the `api_startup_alert_delay`, `alignment_period`, and `threshold_value` to best suit your application's startup characteristics and sensitivity requirements.
