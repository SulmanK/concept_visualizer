"""
Test script to trigger Cloud Monitoring alerts by generating specific log entries.
This script simulates an error in the Cloud Function to test if alerts are working properly.
"""

import json
import logging
import os
import sys
import time
from datetime import datetime

# Configure logging to use structured JSON format
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger()


def generate_error_log():
    """Generate a structured error log that matches the alert filter criteria."""
    # Create a structured log message that matches your alert criteria
    log_data = {
        "severity": "ERROR",
        "taskType": "concept_generation",
        "message": "Error in test_task: Deliberately triggered test error for alert verification",
        "timestamp": datetime.now().isoformat(),
    }

    # Log the error as JSON
    logger.error(json.dumps(log_data))

    print("Test error logged. Check your email for alerts in a few minutes.")

    # Add a second error with different format to test the other filter condition
    log_data2 = {"severity": "ERROR", "taskType": "concept_refinement", "message": "CRITICAL: Error updating task status", "timestamp": datetime.now().isoformat()}

    logger.error(json.dumps(log_data2))
    print("Second test error logged.")


def main():
    """Main function to execute the test."""
    print("Generating test log entries to trigger Cloud Monitoring alerts...")

    # Log multiple errors with a slight delay to ensure they're captured
    for i in range(3):
        generate_error_log()
        print(f"Log batch {i+1} generated.")
        time.sleep(2)  # Small delay between logs

    print("\nAll test logs have been generated.")
    print("Note: It may take a few minutes for the logs to be processed and alerts to be triggered.")
    print("Check your Cloud Monitoring alerts at:")
    print("https://console.cloud.google.com/monitoring/alerting/incidents")


if __name__ == "__main__":
    main()
