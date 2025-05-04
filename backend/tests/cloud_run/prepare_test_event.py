#!/usr/bin/env python
"""Utility script to generate a mock CloudEvent for testing Cloud Functions.

This script:
1. Reads the mock_payload.json file
2. Base64 encodes its contents
3. Creates a CloudEvent structure with the encoded payload
4. Writes the CloudEvent to mock_cloudevent.json
"""

import base64
import json
from datetime import datetime
from pathlib import Path

# Get the directory of this script
current_dir = Path(__file__).parent

# Read the mock payload
with open(current_dir / "mock_payload.json", "r") as f:
    payload = f.read()

# Base64 encode the payload
encoded_payload = base64.b64encode(payload.encode()).decode()

print(f"Original payload: {payload}")
print(f"Base64 encoded payload: {encoded_payload}")

# Create the CloudEvent structure
cloud_event = {
    "specversion": "1.0",
    "type": "google.cloud.pubsub.topic.v1.messagePublished",
    "source": "//pubsub.googleapis.com/projects/local-test-project/topics/local-test-topic",
    "subject": "local-message-id-1",
    "id": "local-event-id-1",
    "time": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    "datacontenttype": "application/json",
    "data": {
        "message": {
            "data": encoded_payload,
            "messageId": "local-message-id-1",
            "publishTime": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
        "subscription": "projects/local-test-project/subscriptions/local-test-sub",
    },
}

# Write the CloudEvent to a file
with open(current_dir / "mock_cloudevent.json", "w") as f:
    json.dump(cloud_event, f, indent=2)

print(f"CloudEvent written to {current_dir / 'mock_cloudevent.json'}")
print("\nYou can now test the function with:")
print("functions-framework --source=cloud_run/worker/main.py " "--target=handle_pubsub --signature-type=cloudevent --port=8080")
print("\nAnd in a separate terminal:")
print("curl -X POST http://localhost:8080 " '-H "Content-Type: application/cloudevents+json" ' f"-d @{current_dir / 'mock_cloudevent.json'}")
