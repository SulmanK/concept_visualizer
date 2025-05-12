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
