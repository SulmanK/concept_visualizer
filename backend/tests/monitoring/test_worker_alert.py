"""
Integration test for Cloud Monitoring alerts by simulating worker function errors.
This test is designed to generate log entries that match the alert filter criteria.
"""

import json
import logging
import os
import sys
import time
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

# Configure logging to use structured JSON format
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger()

# Setup logger to ensure it outputs structured JSON
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(message)s"))
logger.handlers = [handler]
logger.setLevel(logging.INFO)


class TestAlertTrigger:
    """Tests to trigger Cloud Monitoring alerts for worker function errors."""

    def simulate_concept_generation_error(self):
        """Simulate an error in concept generation task processing."""
        logger.error(
            json.dumps(
                {
                    "severity": "ERROR",
                    "taskType": "concept_generation",
                    "message": "Error in concept_generation: Testing alert notification",
                    "taskId": "test-task-1",
                    "timestamp": datetime.now().isoformat(),
                }
            )
        )

    def simulate_concept_refinement_error(self):
        """Simulate an error in concept refinement task processing."""
        logger.error(
            json.dumps({"severity": "ERROR", "taskType": "concept_refinement", "message": "CRITICAL: Error updating task status", "taskId": "test-task-2", "timestamp": datetime.now().isoformat()})
        )

    def test_generate_alert_logs(self):
        """
        Test function to generate error logs that would trigger alerts.

        This is not an actual automated test but rather a utility to
        manually trigger alerts for verification.
        """
        print("\n🔔 Generating logs to test alert triggers...")

        # Generate multiple errors to ensure they're captured
        for i in range(3):
            print(f"\n--- Batch {i+1} ---")
            self.simulate_concept_generation_error()
            print("✓ Concept generation error log sent")
            time.sleep(1)

            self.simulate_concept_refinement_error()
            print("✓ Concept refinement error log sent")
            time.sleep(1)

        print("\n✅ All test logs have been generated!")
        print("⏱️  It may take a few minutes for logs to be processed and alerts to be triggered.")
        print("📊 Check your Cloud Monitoring alerts at:")
        print("   https://console.cloud.google.com/monitoring/alerting/incidents")
        print("\n📧 If your email notification is properly set up and verified, you should")
        print("   receive an alert email within the configured alignment period.")


def main():
    """Run the test directly (not via pytest)."""
    test = TestAlertTrigger()
    test.test_generate_alert_logs()


if __name__ == "__main__":
    main()
