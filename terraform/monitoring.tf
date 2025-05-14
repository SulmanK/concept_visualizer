# terraform/monitoring.tf

# 1. Log-Based Metric for Task Failures
resource "google_logging_metric" "concept_task_failures" {
  project     = var.project_id
  name        = "${var.naming_prefix}-task-fails-${var.environment}"
  description = "Counts errors logged by the Concept Visualizer worker function for specific task types."
  filter      = <<EOT
resource.type="cloud_function"
resource.labels.function_name="${var.naming_prefix}-worker-${var.environment}"
jsonPayload.severity="ERROR"
(jsonPayload.taskType="concept_generation" OR jsonPayload.taskType="concept_refinement")
(jsonPayload.message:"Error in" OR jsonPayload.message:"CRITICAL: Error updating task status")
EOT
  # This filter assumes you are using structured JSON logging with fields:
  # - severity: "ERROR"
  # - taskType: "concept_generation" or "concept_refinement"
  # - message: Containing "Error in" or "CRITICAL: Error updating task status"
  # Adjust the filter based on your actual log format if different.

  metric_descriptor {
    metric_kind = "DELTA" # Counts events within an alignment period
    value_type  = "INT64"
    unit        = "1"     # Represents a count of log entries
    # Optional: Add display name if needed
    # display_name = "Concept Task Failures"

    labels {
      key         = "task_type"
      value_type  = "STRING"
      description = "The type of task that failed (e.g., concept_generation)."
    }
    labels {
      key         = "error_message_snippet"
      value_type  = "STRING"
      description = "A snippet of the error message."
    }
  }

  label_extractors = {
    "task_type"             = "EXTRACT(jsonPayload.taskType)"
    "error_message_snippet" = "REGEXP_EXTRACT(jsonPayload.message, \"Error in ([^:]+):.*\")"
    # Add more extractors if needed, e.g., "EXTRACT(jsonPayload.taskId)"
  }

  disabled = false # Ensure it's enabled
}

# 2. Email Notification Channel
resource "google_monitoring_notification_channel" "email_alert_channel" {
  project      = var.project_id
  display_name = "${var.naming_prefix}-alert-email-${var.environment}"
  type         = "email"
  labels = {
    email_address = var.alert_email_address
  }
  description = "Email notification channel for Concept Visualizer alerts (${var.environment})."
  enabled     = true
}

# 3. Alerting Policy for Task Failures
resource "google_monitoring_alert_policy" "concept_task_failure_alert" {
  project      = var.project_id
  display_name = "${var.naming_prefix}-task-fails-al-${var.environment}"
  combiner     = "OR" # How conditions are combined (OR for single condition)

  conditions {
    display_name = "Concept Task Failures Detected"
    condition_threshold {
      filter     = "metric.type=\"logging.googleapis.com/user/${google_logging_metric.concept_task_failures.name}\" AND resource.type=\"cloud_function\" AND resource.label.function_name=\"${var.naming_prefix}-worker-${var.environment}\""
      # This filter targets the specific log-based metric for your function.
      # The resource.type and resource.label.function_name might be automatically inferred by GCP
      # when using a user-defined metric, but it's good to be explicit.

      comparison        = "COMPARISON_GT" # Greater than
      threshold_value   = 0               # Threshold of 0 (any failure)
      duration          = var.alert_duration # How long the condition must be true (e.g., "60s")
                                         # "0s" means alert on the first occurrence within an alignment period

      trigger {
        count = 1 # Trigger if the condition is met once
      }

      aggregations {
        alignment_period   = var.alert_alignment_period # How often to evaluate (e.g., "300s" for 5 mins)
        per_series_aligner = "ALIGN_COUNT"           # Count the number of matching log entries
        # cross_series_reducer = "REDUCE_SUM" # If you had multiple time series (e.g. per task_type label) and wanted to sum them
      }
    }
  }

  alert_strategy {
    # Optional: How quickly to auto-close incidents if the condition is no longer met
    auto_close = "3600s" # e.g., 1 hour
  }

  notification_channels = [
    google_monitoring_notification_channel.email_alert_channel.id,
  ]

  documentation {
    content   = <<-EOT
### Concept Task Failure Alert (${var.environment})

**Summary:** One or more concept generation/refinement tasks have failed in the Cloud Function worker.

**Metric:** `${google_logging_metric.concept_task_failures.name}`
**Threshold:** Greater than 0 failures within a ${var.alert_alignment_period} window for ${var.alert_duration}.

**Affected Function:** `${var.naming_prefix}-worker-${var.environment}`

**Possible Causes:**
*   Errors in the Cloud Function code.
*   Issues with dependent services (Supabase, JigsawStack API, Redis).
*   Resource exhaustion in the Cloud Function.
*   Invalid Pub/Sub message format.

**Recommended Actions:**
1.  **Check Cloud Function Logs:** Go to GCP Logging and filter for `resource.labels.function_name="${var.naming_prefix}-worker-${var.environment}"` and `severity=ERROR`.
2.  **Check Task Status in Database:** Investigate the `tasks_${var.environment}` table for details on failed tasks.
3.  **Review Recent Code Changes:** Check if recent deployments introduced any bugs.
4.  **Check Dependent Service Status:** Verify Supabase, JigsawStack, and Redis are operational.

Refer to the incident details in Google Cloud Monitoring for more information.
EOT
    mime_type = "text/markdown"
  }

  user_labels = {
    environment = var.environment
    service     = "${var.naming_prefix}-worker"
  }

  depends_on = [
    google_logging_metric.concept_task_failures,
    google_monitoring_notification_channel.email_alert_channel,
    google_cloudfunctions2_function.worker_function # Ensure function exists
  ]
}

# 4. API Health Uptime Check
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

# 5. Alert Policy for API Health Ping Failures
resource "google_monitoring_alert_policy" "api_health_ping_failure_alert" {
  project      = var.project_id
  display_name = "${var.naming_prefix}-api-ping-fails-al-${var.environment}"
  combiner     = "OR" # For a single condition

  conditions {
    display_name = "API Health Ping Unsuccessful (Sustained)"
    condition_threshold {
      filter = "metric.type=\"monitoring.googleapis.com/uptime_check/check_passed\" AND resource.type=\"uptime_url\""

      # Change to count failures rather than calculate a percentage
      aggregations {
        # Extended window to allow more potential failures to accumulate
        alignment_period   = "900s" # 15 minutes instead of 5 minutes
        # Count failures instead of calculating a percentage
        per_series_aligner = "ALIGN_COUNT_FALSE"
      }

      # Condition for triggering an alert
      comparison      = "COMPARISON_GT" # Alert if failure count is GREATER THAN...
      threshold_value = 4               # ...4 failures in the alignment period
                                        # This means if we get at least 5 failures in the alignment period, trigger the alert

      # This is the "grace period" for startup
      duration = "2700s" # 45 minutes.
                         # The failures must persist for this entire duration before an alert fires.

      trigger {
        count = 1 # Trigger if the condition is met once
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
**Condition:** At least 5 failed checks within a ${var.alert_alignment_period} window, persisting for ${var.api_startup_alert_delay}.

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

# --- Frontend Availability Uptime Check ---
resource "google_monitoring_uptime_check_config" "frontend_availability" {
  project      = var.project_id
  display_name = "${var.naming_prefix}-frontend-availability-${var.environment}"
  timeout      = "10s" # How long each ping waits for a response

  http_check {
    path           = "/"                # Check the root path of your frontend
    port           = "443"              # Vercel uses HTTPS
    use_ssl        = true
    request_method = "GET"
  }

  # Validates that the page title is present - a good sign the app loaded
  content_matchers {
    content = "<title>Concept Visualizer</title>" # Adjust to your actual <title>
    matcher = "CONTAINS_STRING"                    # Checks if the string is present in the response body
  }

  monitored_resource {
    type = "uptime_url"
    labels = {
      host = var.initial_frontend_hostname_placeholder # This will be updated by CI/CD
    }
  }
  period = "300s" # Check every 5 minutes (valid value)
}

# --- Alert Policy for Frontend Availability Failures ---
resource "google_monitoring_alert_policy" "frontend_availability_failure_alert" {
  project      = var.project_id
  display_name = "${var.naming_prefix}-frontend-down-al-${var.environment}"
  combiner     = "OR"

  conditions {
    display_name = "Frontend Application Unavailable (Sustained)"
    condition_threshold {
      filter = "metric.type=\"monitoring.googleapis.com/uptime_check/check_passed\" AND resource.type=\"uptime_url\" AND metric.label.check_id=\"${google_monitoring_uptime_check_config.frontend_availability.uptime_check_id}\""
      aggregations {
        alignment_period   = var.alert_alignment_period # e.g., "300s"
        per_series_aligner = "ALIGN_FRACTION_TRUE"
      }
      comparison      = "COMPARISON_LT"
      threshold_value = 0.9 # Alert if less than 90% success rate in an alignment_period
      duration        = var.frontend_startup_alert_delay # e.g., "300s"
      trigger {
        count = 1
      }
    }
  }

  notification_channels = [
    google_monitoring_notification_channel.email_alert_channel.id,
  ]

  documentation {
    content = <<-EOT
### Frontend Availability Alert (${var.environment})

**Summary:** The frontend application is failing uptime checks.
**Monitored Host (may be placeholder if CI/CD hasn't updated it yet):** `${var.initial_frontend_hostname_placeholder}`
**Uptime Check ID:** `${google_monitoring_uptime_check_config.frontend_availability.uptime_check_id}`
**Condition:** Success rate less than 90% over a ${var.alert_alignment_period} window, persisting for ${var.frontend_startup_alert_delay}.

**Possible Causes:**
*   Vercel platform issues.
*   DNS resolution problems for your custom domain (if any).
*   Misconfiguration in Vercel deployment settings.
*   The application is not serving the expected content (e.g., your app's title tag).
*   The Uptime Check's target hostname in GCP Monitoring is outdated (CI/CD job may have failed to update it).

**Recommended Actions:**
1.  **Check Vercel Status:** Visit [status.vercel.com](https://status.vercel.com/).
2.  **Check Vercel Deployment Logs:** Review logs for your frontend deployment in the Vercel dashboard.
3.  **Verify DNS Configuration:** If using a custom domain, ensure DNS records are correct.
4.  **Verify Uptime Check Target:** In GCP Monitoring, check the hostname configured for Uptime Check ID `${google_monitoring_uptime_check_config.frontend_availability.uptime_check_id}`. Ensure it matches your latest Vercel deployment URL.
5.  **Manually Access Frontend URL:** Try accessing your Vercel deployment URL from different networks/devices.
    EOT
    mime_type = "text/markdown"
  }

  user_labels = {
    environment = var.environment
    service     = "${var.naming_prefix}-frontend"
    tier        = "frontend"
  }

  depends_on = [
    google_monitoring_uptime_check_config.frontend_availability,
    google_monitoring_notification_channel.email_alert_channel,
  ]
}
