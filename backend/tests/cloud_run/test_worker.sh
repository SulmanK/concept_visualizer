#!/bin/bash
# Test script for the Cloud Function worker

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR/../../"  # Navigate to backend directory

# Generate the mock CloudEvent
echo "Generating mock CloudEvent from payload..."
python tests/cloud_run/prepare_test_event.py

# Check if functions-framework is already running
if lsof -i:8080 > /dev/null; then
  echo "A service is already running on port 8080. Please stop it before running this test."
  exit 1
fi

# Start the functions-framework in the background
echo "Starting Functions Framework..."
functions-framework --source=cloud_run/worker/main.py --target=handle_pubsub --signature-type=cloudevent --port=8080 &
FUNCTIONS_PID=$!

# Give it a moment to start up
sleep 2

# Send the test request
echo "Sending test request..."
curl -X POST http://localhost:8080 \
     -H "Content-Type: application/cloudevents+json" \
     -d @tests/cloud_run/mock_cloudevent.json

# Cleanup
echo "Stopping Functions Framework (PID: $FUNCTIONS_PID)..."
kill $FUNCTIONS_PID
echo "Test completed."
