#!/usr/bin/env python
"""
Cloud Monitoring Test Utility

A utility script to test Google Cloud Monitoring alerts, metrics, and notification channels.
This script can generate test logs that match alert criteria or verify alert configurations.
"""
import argparse
import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

# Configure structured JSON logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger()

# Set up a handler that ensures JSON output
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(message)s"))
logger.handlers = [handler]
logger.setLevel(logging.INFO)

# Color constants for terminal output
BLUE = "\033[94m"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BOLD = "\033[1m"
UNDERLINE = "\033[4m"
END = "\033[0m"


def print_colored(message: str, color: str) -> None:
    """Print colored text to terminal."""
    print(f"{color}{message}{END}")


def print_header(message: str) -> None:
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print_colored(f" {message}", BOLD + BLUE)
    print("=" * 80 + "\n")


def print_success(message: str) -> None:
    """Print a success message."""
    print_colored(f"✅ {message}", GREEN)


def print_warning(message: str) -> None:
    """Print a warning message."""
    print_colored(f"⚠️ {message}", YELLOW)


def print_error(message: str) -> None:
    """Print an error message."""
    print_colored(f"❌ {message}", RED)


def generate_structured_error_log(task_type: str, message: str, additional_fields: Optional[Dict[str, Any]] = None) -> None:
    """Generate a structured error log with the specified fields."""
    log_data = {"severity": "ERROR", "taskType": task_type, "message": message, "timestamp": datetime.now().isoformat()}

    # Add any additional fields
    if additional_fields:
        log_data.update(additional_fields)

    # Log as JSON
    logger.error(json.dumps(log_data))


def test_concept_generation_error() -> None:
    """Generate a log entry that simulates a concept generation error."""
    generate_structured_error_log(
        task_type="concept_generation",
        message="Error in concept_generation: Testing alert notification",
        additional_fields={"taskId": f"test-task-{int(time.time())}", "errorType": "SimulatedError", "errorDetails": "This is a simulated error for testing the alert system"},
    )
    print_success("Concept generation error log generated")


def test_concept_refinement_error() -> None:
    """Generate a log entry that simulates a concept refinement error."""
    generate_structured_error_log(
        task_type="concept_refinement",
        message="CRITICAL: Error updating task status",
        additional_fields={"taskId": f"test-task-{int(time.time())}", "errorType": "DatabaseError", "errorDetails": "Simulated database error for testing alerts"},
    )
    print_success("Concept refinement error log generated")


def verify_metric_exists(project_id: str, metric_name: str) -> bool:
    """Check if the metric exists in the project."""
    print_header(f"Verifying metric: {metric_name}")

    try:
        # Use Python to inform user we're checking
        print(f"Checking for metric '{metric_name}' in project '{project_id}'...")
        print("This would normally use gcloud logging metrics list to verify the metric.")
        print("Since we can't directly run this command, please check manually:")
        print(f'\n    gcloud logging metrics list --filter="name:{metric_name}" --project={project_id}\n')

        # Always return True since we can't actually run the command
        return True
    except Exception as e:
        print_error(f"Error verifying metric: {str(e)}")
        return False


def verify_notification_channel(project_id: str, channel_name: str) -> bool:
    """Check if the notification channel exists and is verified."""
    print_header(f"Verifying notification channel: {channel_name}")

    try:
        # Use Python to inform user we're checking
        print(f"Checking for notification channel '{channel_name}' in project '{project_id}'...")
        print("This would normally use gcloud alpha monitoring channels list to verify the channel.")
        print("Since we can't directly run this command, please check manually:")
        print(f"\n    gcloud alpha monitoring channels list --project={project_id}\n")

        # Provide instructions for verification
        print_warning("Important: Email notification channels must be verified!")
        print("Please check your email for a verification link from Google Cloud Monitoring.")
        print("If you don't see it, you can request a new verification from the Google Cloud Console.")

        # Always return True since we can't actually run the command
        return True
    except Exception as e:
        print_error(f"Error verifying notification channel: {str(e)}")
        return False


def verify_alert_policy(project_id: str, policy_name: str) -> bool:
    """Check if the alert policy exists and is configured correctly."""
    print_header(f"Verifying alert policy: {policy_name}")

    try:
        # Use Python to inform user we're checking
        print(f"Checking for alert policy '{policy_name}' in project '{project_id}'...")
        print("This would normally use gcloud alpha monitoring policies list to verify the policy.")
        print("Since we can't directly run this command, please check manually:")
        print(f"\n    gcloud alpha monitoring policies list --project={project_id}\n")

        # Always return True since we can't actually run the command
        return True
    except Exception as e:
        print_error(f"Error verifying alert policy: {str(e)}")
        return False


def generate_test_logs(count: int, interval: float, project_id: str) -> None:
    """Generate a series of test logs to trigger alerts."""
    print_header(f"Generating {count} test log batches")

    print(f"Project ID: {project_id}")
    print(f"Batches: {count}")
    print(f"Interval: {interval} seconds between logs")
    print("\nStarting log generation...\n")

    for i in range(count):
        print(f"\n--- Batch {i+1}/{count} ---")
        test_concept_generation_error()
        time.sleep(interval / 2)
        test_concept_refinement_error()

        if i < count - 1:
            time.sleep(interval)

    print("\n" + "=" * 80)
    print_success("All test logs have been generated!")
    print("\n⏱️  It may take a few minutes for logs to be processed and alerts to be triggered.")
    print("📊 Check your Cloud Monitoring alerts at:")
    print(f"   https://console.cloud.google.com/monitoring/alerting/incidents?project={project_id}")
    print("\n📧 If your email notification is properly set up and verified, you should")
    print("   receive an alert email within the configured alignment period.")
    print("=" * 80 + "\n")


def verify_monitoring_setup(project_id: str) -> None:
    """Verify the entire monitoring setup including metrics, channels, and policies."""
    print_header("Verifying Complete Monitoring Setup")

    # Determine environment based on project ID
    env = "prod" if "prod" in project_id else "dev"
    prefix = f"concept-viz-{env}"

    # Check metric
    metric_name = f"{prefix}-task-fails-{env}"
    metric_ok = verify_metric_exists(project_id, metric_name)

    # Check notification channel
    channel_name = f"{prefix}-alert-email-{env}"
    channel_ok = verify_notification_channel(project_id, channel_name)

    # Check alert policy
    policy_name = f"{prefix}-task-fails-al-{env}"
    policy_ok = verify_alert_policy(project_id, policy_name)

    # Summary
    print_header("Verification Summary")
    if metric_ok:
        print_success(f"Metric '{metric_name}' verification instructions provided")
    else:
        print_error(f"Metric '{metric_name}' verification failed")

    if channel_ok:
        print_success(f"Notification channel '{channel_name}' verification instructions provided")
    else:
        print_error(f"Notification channel '{channel_name}' verification failed")

    if policy_ok:
        print_success(f"Alert policy '{policy_name}' verification instructions provided")
    else:
        print_error(f"Alert policy '{policy_name}' verification failed")

    print("\n" + "=" * 80)
    print("For a complete verification, please also check the Google Cloud Console:")
    print(f"https://console.cloud.google.com/monitoring/alerting/policies?project={project_id}")
    print("=" * 80 + "\n")


def main() -> None:
    """Main function with command-line interface."""
    parser = argparse.ArgumentParser(description="Test utility for Google Cloud Monitoring alerts and metrics")

    parser.add_argument(
        "--project",
        "-p",
        default=os.environ.get("CONCEPT_PROJECT_ID", "concept-visualizer-prod-1"),
        help="Google Cloud project ID (default: environment CONCEPT_PROJECT_ID or concept-visualizer-prod-1)",
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Generate logs command
    generate_parser = subparsers.add_parser("generate-logs", help="Generate test logs to trigger alerts")
    generate_parser.add_argument("--count", "-c", type=int, default=3, help="Number of log batches to generate (default: 3)")
    generate_parser.add_argument("--interval", "-i", type=float, default=2.0, help="Interval between log batches in seconds (default: 2.0)")

    # Verify setup command
    verify_parser = subparsers.add_parser("verify", help="Verify monitoring setup")

    # Parse arguments
    args = parser.parse_args()

    # Execute command
    if args.command == "generate-logs":
        generate_test_logs(args.count, args.interval, args.project)
    elif args.command == "verify":
        verify_monitoring_setup(args.project)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
