# Terraform Monitoring Guide

This document provides guidance on monitoring the Concept Visualizer infrastructure deployed on Google Cloud Platform (GCP).

## Monitoring Overview

The Concept Visualizer's monitoring strategy is built around:

1. **Cloud Monitoring**: GCP's native monitoring solution
2. **Uptime Checks**: To verify that services are available
3. **Alert Policies**: For notification when issues arise
4. **Logging**: Centralized logging for troubleshooting
5. **Custom Metrics**: For application-specific monitoring

## Monitoring Components

### Infrastructure Monitoring

The infrastructure is monitored through several mechanisms:

#### VM Monitoring (`monitoring.tf`)

The API VM instance is monitored for:

- CPU utilization
- Memory usage
- Disk space
- Network traffic
- Instance status

```hcl
# Example alert policy for VM CPU utilization
resource "google_monitoring_alert_policy" "api_cpu_usage" {
  display_name = "${var.naming_prefix}-api-cpu-usage-${terraform.workspace}"
  combiner     = "OR"
  conditions {
    display_name = "High CPU usage on API VM"
    condition_threshold {
      filter     = "metric.type=\"compute.googleapis.com/instance/cpu/utilization\" AND resource.type=\"gce_instance\" AND resource.labels.instance_id = \"${google_compute_instance.api_vm.instance_id}\""
      duration   = "60s"
      comparison = "COMPARISON_GT"
      threshold_value = 0.8
      trigger {
        count = 1
      }
      aggregations {
        alignment_period     = "60s"
        per_series_aligner   = "ALIGN_MEAN"
        cross_series_reducer = "REDUCE_MEAN"
        group_by_fields      = []
      }
    }
  }
  notification_channels = [google_monitoring_notification_channel.email.id]
}
```

#### Cloud Function Monitoring

The worker Cloud Function is monitored for:

- Execution count
- Execution time
- Error rate
- Memory usage

```hcl
# Example alert policy for Cloud Function errors
resource "google_monitoring_alert_policy" "worker_errors" {
  display_name = "${var.naming_prefix}-worker-errors-${terraform.workspace}"
  combiner     = "OR"
  conditions {
    display_name = "High error rate on worker function"
    condition_threshold {
      filter     = "metric.type=\"cloudfunctions.googleapis.com/function/execution_count\" AND resource.type=\"cloud_function\" AND resource.labels.function_name = \"${var.naming_prefix}-worker-${terraform.workspace}\" AND metric.labels.status != \"ok\""
      duration   = "60s"
      comparison = "COMPARISON_GT"
      threshold_value = 5
      trigger {
        count = 1
      }
      aggregations {
        alignment_period     = "60s"
        per_series_aligner   = "ALIGN_RATE"
        cross_series_reducer = "REDUCE_SUM"
        group_by_fields      = []
      }
    }
  }
  notification_channels = [google_monitoring_notification_channel.email.id]
}
```

#### Pub/Sub Monitoring

The Pub/Sub messaging system is monitored for:

- Message delivery latency
- Unacked message count
- Subscription backlog

```hcl
# Example alert policy for Pub/Sub backlog
resource "google_monitoring_alert_policy" "pubsub_backlog" {
  display_name = "${var.naming_prefix}-pubsub-backlog-${terraform.workspace}"
  combiner     = "OR"
  conditions {
    display_name = "Large backlog in Pub/Sub subscription"
    condition_threshold {
      filter     = "metric.type=\"pubsub.googleapis.com/subscription/num_undelivered_messages\" AND resource.type=\"pubsub_subscription\" AND resource.labels.subscription_id = \"${var.naming_prefix}-tasks-sub-${terraform.workspace}\""
      duration   = "300s"
      comparison = "COMPARISON_GT"
      threshold_value = 100
      trigger {
        count = 1
      }
      aggregations {
        alignment_period     = "60s"
        per_series_aligner   = "ALIGN_MEAN"
        cross_series_reducer = "REDUCE_MEAN"
        group_by_fields      = []
      }
    }
  }
  notification_channels = [google_monitoring_notification_channel.email.id]
}
```

### Application Monitoring

#### Frontend Monitoring

The frontend application is monitored for:

- Availability (uptime checks)
- Response time
- HTTP error rates

```hcl
# Example uptime check for frontend
resource "google_monitoring_uptime_check_config" "frontend" {
  display_name = "${var.naming_prefix}-frontend-uptime-${terraform.workspace}"
  timeout      = "10s"
  period       = "60s"

  http_check {
    path           = "/"
    port           = "443"
    use_ssl        = true
    validate_ssl   = true
  }

  monitored_resource {
    type = "uptime_url"
    labels = {
      project_id = var.project_id
      host       = var.frontend_url
    }
  }
}

# Example alert policy for frontend uptime
resource "google_monitoring_alert_policy" "frontend_uptime" {
  display_name = "${var.naming_prefix}-frontend-uptime-${terraform.workspace}"
  combiner     = "OR"
  conditions {
    display_name = "Frontend uptime check failure"
    condition_threshold {
      filter     = "metric.type=\"monitoring.googleapis.com/uptime_check/check_passed\" AND resource.type=\"uptime_url\" AND metric.labels.check_id = \"${google_monitoring_uptime_check_config.frontend.uptime_check_id}\""
      duration   = "${var.frontend_startup_alert_delay}"
      comparison = "COMPARISON_LT"
      threshold_value = 1
      trigger {
        count = 1
      }
      aggregations {
        alignment_period     = "${var.alert_alignment_period}"
        per_series_aligner   = "ALIGN_FRACTION_TRUE"
        cross_series_reducer = "REDUCE_MEAN"
        group_by_fields      = []
      }
    }
  }
  notification_channels = [google_monitoring_notification_channel.email.id]
}
```

#### API Monitoring

The API service is monitored for:

- Endpoint availability
- Response times
- Error rates
- Rate limiting events

```hcl
# Example uptime check for API health endpoint
resource "google_monitoring_uptime_check_config" "api_health" {
  display_name = "${var.naming_prefix}-api-health-uptime-${terraform.workspace}"
  timeout      = "10s"
  period       = "60s"

  http_check {
    path           = "/api/health/ping"
    port           = "80"
    use_ssl        = false
  }

  monitored_resource {
    type = "uptime_url"
    labels = {
      project_id = var.project_id
      host       = google_compute_address.api_ip.address
    }
  }
}
```

### Notification Channels

Alerts are sent through configured notification channels:

```hcl
# Email notification channel
resource "google_monitoring_notification_channel" "email" {
  display_name = "${var.naming_prefix}-email-notification-${terraform.workspace}"
  type         = "email"
  labels = {
    email_address = var.alert_email_address
  }
}
```

## Monitoring Dashboard

A custom dashboard is created to visualize the most important metrics:

```hcl
resource "google_monitoring_dashboard" "overview" {
  dashboard_json = <<EOF
{
  "displayName": "${var.naming_prefix}-overview-dashboard-${terraform.workspace}",
  "gridLayout": {
    "widgets": [
      {
        "title": "API VM CPU Usage",
        "xyChart": {
          "dataSets": [{
            "timeSeriesQuery": {
              "timeSeriesFilter": {
                "filter": "metric.type=\"compute.googleapis.com/instance/cpu/utilization\" AND resource.type=\"gce_instance\"",
                "aggregation": {
                  "perSeriesAligner": "ALIGN_MEAN",
                  "crossSeriesReducer": "REDUCE_MEAN",
                  "alignmentPeriod": "60s"
                }
              }
            }
          }]
        }
      },
      {
        "title": "Worker Function Executions",
        "xyChart": {
          "dataSets": [{
            "timeSeriesQuery": {
              "timeSeriesFilter": {
                "filter": "metric.type=\"cloudfunctions.googleapis.com/function/execution_count\" AND resource.type=\"cloud_function\"",
                "aggregation": {
                  "perSeriesAligner": "ALIGN_RATE",
                  "crossSeriesReducer": "REDUCE_SUM",
                  "alignmentPeriod": "60s"
                }
              }
            }
          }]
        }
      }
      // Add more charts as needed
    ]
  }
}
EOF
}
```

## Logging Strategy

### Log Collection

Logs are collected from multiple sources:

- **API VM Logs**: Application logs, startup script logs, system logs
- **Cloud Function Logs**: Worker execution logs
- **Pub/Sub Logs**: Message delivery logs
- **Cloud Audit Logs**: Administrative activities

### Log Filters

Useful log filters for troubleshooting:

```bash
# API VM application logs
resource.type="gce_instance"
logName="projects/PROJECT_ID/logs/api-application"

# Worker function logs
resource.type="cloud_function"
resource.labels.function_name="FUNCTION_NAME"

# Pub/Sub logs for tasks topic
resource.type="pubsub_topic"
resource.labels.topic_id="TOPIC_ID"

# Startup script logs
resource.type="gce_instance"
logName="projects/PROJECT_ID/logs/startupscript.log"
```

### Log-based Metrics

Custom metrics based on logs for additional monitoring:

```hcl
# Example log-based metric for API error rates
resource "google_logging_metric" "api_errors" {
  name        = "${var.naming_prefix}-api-errors-${terraform.workspace}"
  filter      = "resource.type=\"gce_instance\" AND logName=\"projects/${var.project_id}/logs/api-application\" AND textPayload=~\"ERROR\""
  description = "Count of ERROR level log entries from the API application"

  metric_descriptor {
    metric_kind = "DELTA"
    value_type  = "INT64"
    labels {
      key         = "severity"
      value_type  = "STRING"
      description = "Error severity"
    }
  }

  label_extractors = {
    "severity" = "REGEXP_EXTRACT(textPayload, \"ERROR\\[(\\w+)\\]\")"
  }
}
```

## Monitoring Best Practices

### Implementation Guidelines

1. **Baseline Metrics**: Establish baseline performance metrics for normal operation

   - CPU, memory, and disk usage patterns
   - Typical request latency
   - Normal error rates

2. **Appropriate Thresholds**: Set alert thresholds based on baselines plus tolerance

   - Avoid alert fatigue with too-sensitive thresholds
   - Consider time-of-day patterns in thresholds

3. **Alert Priority Levels**: Categorize alerts by severity

   - Critical: Immediate action required (service down)
   - Warning: Attention needed soon (approaching resource limits)
   - Info: For awareness (unusual patterns)

4. **Actionable Alerts**: Ensure alerts provide enough information to act upon
   - Link to runbooks in alert descriptions
   - Include troubleshooting steps
   - Provide context about the issue

### Operational Procedures

1. **Regular Reviews**: Schedule periodic review of monitoring effectiveness

   - Adjust thresholds based on operational experience
   - Add new metrics as needed
   - Remove noisy or low-value alerts

2. **Incident Response**: Document procedures for handling alerts

   - Who receives which types of alerts
   - Escalation paths
   - Resolution documentation

3. **Post-Mortem Analysis**: After incidents, review monitoring effectiveness
   - Were alerts timely and accurate?
   - Were there missed signals?
   - What monitoring improvements are needed?

## Advanced Monitoring Techniques

### Distributed Tracing

For request flow visibility across services:

1. Add OpenTelemetry or similar instrumentation to both API and worker
2. Configure Cloud Trace integration
3. Analyze traces for performance bottlenecks

### SLO Monitoring

Define Service Level Objectives:

```hcl
# Example SLO for API availability
resource "google_monitoring_slo" "api_availability" {
  service             = google_monitoring_service.api_service.service_id
  slo_id              = "${var.naming_prefix}-api-availability-${terraform.workspace}"
  display_name        = "API Availability SLO"
  goal                = 0.99  # 99% availability
  rolling_period_days = 30

  basic_sli {
    availability {
      enabled = true
    }
  }
}
```

### Cost Management Monitoring

Monitor infrastructure costs:

```hcl
# Example budget alert
resource "google_billing_budget" "project_budget" {
  billing_account = var.billing_account_id
  display_name    = "${var.naming_prefix}-budget-${terraform.workspace}"

  budget_filter {
    projects = ["projects/${var.project_id}"]
  }

  amount {
    specified_amount {
      currency_code = "USD"
      units         = "100"  # $100 budget
    }
  }

  threshold_rules {
    threshold_percent = 0.8  # Alert at 80% of budget
    spend_basis       = "CURRENT_SPEND"
  }

  threshold_rules {
    threshold_percent = 1.0  # Alert at 100% of budget
    spend_basis       = "CURRENT_SPEND"
  }
}
```

## Next Steps

- Review the [Security Overview](security.md) for security monitoring setup
- Check the [Operations Guide](operations.md) for troubleshooting procedures
- Consider implementing [custom metrics](https://cloud.google.com/monitoring/custom-metrics) for application-specific monitoring
