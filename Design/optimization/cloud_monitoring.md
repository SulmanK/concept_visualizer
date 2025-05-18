Yes, you absolutely can and **should** manage your GCP Monitoring resources (log-based metrics, alerting policies, notification channels) using Terraform. This is a best practice for Infrastructure as Code (IaC) as it keeps your entire monitoring setup version-controlled, repeatable, and documented.

Here's how you can add the necessary Terraform configurations. We'll create:

1.  A **Log-Based Metric** to count your specific task failures.
2.  An **Email Notification Channel** for your main email.
3.  An **Alerting Policy** that uses the metric and sends notifications via the email channel.

**Step 1: Add New Variables (in `terraform/variables.tf`)**

First, let's add a variable for your email address and some for alert configuration:

```terraform
# terraform/variables.tf

variable "alert_email_address" {
  description = "The email address to send monitoring alerts to."
  type        = string
}

variable "alert_alignment_period" {
  description = "The alignment period for the task failure alert (e.g., '300s' for 5 minutes)."
  type        = string
  default     = "300s" # 5 minutes
}

variable "alert_duration" {
  description = "How long the failure condition must persist before an alert is sent (e.g., '60s'). Use '0s' to alert on the first instance within an alignment period."
  type        = string
  default     = "0s" # Alert immediately on first failure in an alignment period
}
```

**Step 2: Update Your `.tfvars.example` Files**

Add the new variable to your example files (and your actual `.tfvars` files):

**`terraform/environments/dev.tfvars.example` (and `dev.tfvars`)**

```terraform
# ... existing variables ...
alert_email_address         = "your-main-dev-alert-email@example.com" # <-- REPLACE
alert_alignment_period      = "300s" # 5 minutes
alert_duration              = "60s"  # Alert if condition met for 1 minute
```

**`terraform/environments/prod.tfvars.example` (and `prod.tfvars`)**

```terraform
# ... existing variables ...
alert_email_address         = "your-main-prod-alert-email@example.com" # <-- REPLACE
alert_alignment_period      = "300s" # 5 minutes
alert_duration              = "0s"   # Alert immediately on first failure in an alignment period
```

**Important:** Replace `"your-main-dev-alert-email@example.com"` and `"your-main-prod-alert-email@example.com"` with your actual email addresses.

**Step 3: Define the Monitoring Resources (e.g., in a new file `terraform/monitoring.tf`)**

Create a new file, for example, `terraform/monitoring.tf`:

```terraform
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
      key             = "task_type"
      value_type      = "STRING"
      description     = "The type of task that failed (e.g., concept_generation)."
      value_extractor = "EXTRACT(jsonPayload.taskType)"
    }
    labels {
      key             = "error_message_snippet"
      value_type      = "STRING"
      description     = "A snippet of the error message."
      value_extractor = "REGEXP_EXTRACT(jsonPayload.message, \"Error in ([^:]+):.*\")" # Example to extract part of message
    }
  }

  label_extractors = {
    "task_type"               = "EXTRACT(jsonPayload.taskType)"
    "error_message_snippet"   = "REGEXP_EXTRACT(jsonPayload.message, \"Error in ([^:]+):.*\")"
     # Add more extractors if needed, e.g., "EXTRACT(jsonPayload.taskId)"
  }

  bucket_options {
    linear_buckets {
      num_finite_buckets = 1 # Required for DELTA metrics, but not very useful for simple counters
      width              = 1
      offset             = 0
    }
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
```

**Explanation of `terraform/monitoring.tf`:**

1.  **`google_logging_metric.concept_task_failures`**:

    - `name`: A unique name for your metric. It's good practice to include the `naming_prefix` and `environment`.
    - `filter`: This is the crucial part.
      - `resource.type="cloud_function"`: Targets logs from Cloud Functions.
      - `resource.labels.function_name="${var.naming_prefix}-worker-${var.environment}"`: Narrows it down to _your specific_ worker function. **Ensure this matches the `name` attribute of your `google_cloudfunctions2_function` resource.**
      - `jsonPayload.severity="ERROR"`: Filters for logs where your Python logger used `logger.error()` or similar and you're outputting structured (JSON) logs.
      - `(jsonPayload.taskType="concept_generation" OR jsonPayload.taskType="concept_refinement")`: Further filters by the task type if you include `taskType` in your structured logs.
      - `(jsonPayload.message:"Error in" OR jsonPayload.message:"CRITICAL: Error updating task status")`: Looks for specific substrings in your error messages. The `OR` condition allows you to catch multiple distinct error messages that signify a failure you want to monitor.
        - **Note on Filter:** If your Python logs are not structured JSON, you'd use `textPayload` instead of `jsonPayload.field`. For example: `textPayload:"Error in concept_generation task"`. Structured logs are generally more reliable for filtering. The example you provided for textPayload is a good start if you're not using structured JSON logging.
    - `metric_descriptor`: Defines the type of metric (DELTA for changes over time, INT64 for counts).
    - `label_extractors`: (Optional but good) Allows you to create labels on your metric from parts of the log message (e.g., extract the `taskType`). This can give you more granular alerting or charting.
    - `bucket_options`: Required for DELTA metrics to define how data is aggregated, though less critical for a simple counter.

2.  **`google_monitoring_notification_channel.email_alert_channel`**:

    - `display_name`: A friendly name for the channel in the GCP console.
    - `type = "email"`: Specifies it's an email channel.
    - `labels = { email_address = var.alert_email_address }`: Sets your email.
    - **Verification:** GCP will send a verification email to this address. You **must click the link in that email** to activate the notification channel before it can receive alerts. Terraform can create the channel, but it cannot perform the email verification step.

3.  **`google_monitoring_alert_policy.concept_task_failure_alert`**:
    - `display_name`: A friendly name for the alert policy.
    - `combiner = "OR"`: Since we have one condition, OR is fine.
    - `conditions`: Defines when the alert triggers.
      - `filter`: Specifies which metric to watch. It uses the `metric.type` which is `logging.googleapis.com/user/YOUR_METRIC_NAME`.
      - `comparison = "COMPARISON_GT"`: Trigger when the metric is "Greater Than".
      - `threshold_value = 0`: The value the metric must exceed. For a count of errors, `0` means any error.
      - `duration = var.alert_duration`: How long the condition (`>0` errors) must be true before an alert is sent. `0s` means it will trigger as soon as the alignment period shows a count > 0.
      - `aggregations`:
        - `alignment_period = var.alert_alignment_period`: How frequently the metric is evaluated (e.g., "300s" for every 5 minutes).
        - `per_series_aligner = "ALIGN_COUNT"`: We are counting the log entries.
    - `notification_channels`: Links to the email channel created above.
    - `documentation`: (Highly Recommended) Provides context and steps for whoever receives the alert.
    - `depends_on`: Ensures the metric and channel are created before the policy.

**Step 4: Apply Terraform Changes**

1.  Ensure you have updated your `.tfvars` file with your actual `alert_email_address`.
2.  Run `terraform init` (if you added a new provider or made backend changes, though not strictly necessary for just adding resources).
3.  Run `terraform plan -var-file="environments/your_env.tfvars" -out=tfplan.monitoring`
4.  Review the plan.
5.  Run `terraform apply tfplan.monitoring`

**After Applying:**

- **Verify Email Notification Channel:** Go to GCP Console -> Monitoring -> Alerting -> Edit Notification Channels. Find the channel Terraform created and ensure it's verified. If not, there should be an option to resend the verification email. Click the link in that email.
- **Test the Alert (Optional but Recommended):**
  - Temporarily modify your Cloud Function code to deliberately log an error that matches your log-based metric's filter (e.g., `logger.error(json.dumps({"severity": "ERROR", "taskType": "concept_generation", "message": "Error in test task: Deliberate test error"}))`).
  - Trigger the function.
  - Wait for the alignment period + duration. You should receive an email.
  - Remember to remove the test error log and redeploy your function.

This setup provides a solid foundation for getting email alerts on your task failures. You can expand on it by adding more sophisticated filters, different notification channels (like PagerDuty or Slack via Pub/Sub), or more granular metrics.
