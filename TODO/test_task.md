Okay, great! Since you've chosen the **Cloud Functions (2nd Gen, container-based)** approach for simplicity, here's how you can test your refactored worker logic locally using the **Google Cloud Functions Framework**.

This is the recommended way as it most closely simulates the actual Cloud Function environment your code will run in when deployed.

**Prerequisites:**

1.  **Code Refactoring Complete:** Ensure you've completed Step I (Backend Code Changes) and Step II (Dockerfile Changes) from the design plan. Specifically, `worker/main.py` must have the `@functions_framework.cloud_event` decorator on your `handle_pubsub` function, and `functions-framework` must be in `worker/requirements.txt` and installed in your local environment (`uv pip install functions-framework`).
2.  **Environment Variables:** Your local testing environment needs access to all the necessary environment variables (Supabase keys, Jigsaw key, Redis details, table names, etc.) that your `initialize_services()` function requires. The easiest way is usually to:
    - Make sure your `backend/.env.develop` file has the correct values.
    - Run the Functions Framework from a terminal _where these variables are loaded_. You might need to manually export them (`export CONCEPT_SUPABASE_URL=...`) or use a tool like `python-dotenv` if your script loads it (though Functions Framework typically doesn't automatically load `.env`). A common pattern is to prefix the run command: `env $(cat .env.develop | xargs) functions-framework ...` (syntax might vary based on your shell).

**Local Testing Steps:**

1.  **Start the Functions Framework Server:**

    - Open a terminal in your **`backend`** directory.
    - Activate your virtual environment (`source .venv/bin/activate` or similar).
    - Run the framework, pointing it to your worker code:

      ```bash
      functions-framework --source=cloud_run/worker/main.py --target=handle_pubsub --signature-type=cloudevent --port=8080
      ```

      - `--source`: Path to your Python file containing the function.
      - `--target`: The name of the Python function decorated with `@functions_framework.cloud_event` (must match your code).
      - `--signature-type=cloudevent`: Specifies that the function expects events in the CloudEvents format (which Pub/Sub uses).
      - `--port=8080`: The port the local server will listen on (default).

    - You should see output indicating the server is running, like `Serving function... URL: http://localhost:8080/`. Keep this terminal open.

2.  **Prepare a Mock Pub/Sub Message Payload:**

    - Create a file named `mock_payload.json` (you can put it anywhere, e.g., in the `backend` directory) with the structure your API originally sends to Pub/Sub:
      ```json
      // mock_payload.json
      {
        "task_id": "local-gen-task-001",
        "user_id": "test-user-for-local",
        "logo_description": "A cute panda eating bamboo",
        "theme_description": "Minimalist, green and white",
        "num_palettes": 3,
        "task_type": "concept_generation"
      }
      ```
      _(Adjust the content based on whether you're testing generation or refinement)_

3.  **Base64 Encode the Payload:**

    - Pub/Sub messages within CloudEvents are base64 encoded. Encode the content of `mock_payload.json`:
      ```bash
      # macOS/Linux (copy the output string)
      cat mock_payload.json | base64
      ```
      _Example output (will be different for you):_ `ewogICAgInRhc2tfaWQiOiAibG9jYWwtZ2VuLXRhc2stMDAxIiwKICAgICJ1c2VyX2lkIjogInRlc3QtdXNlci1mb3ItbG9jYWwiLAogICAgImxvZ29fZGVzY3JpcHRpb24iOiAiQSBjdXRlIHBhbmRhIGVhdGluZyBiYW1ib28iLAogICAgInRoZW1lX2Rlc2NyaXB0aW9uIjogIk1pbmltYWxpc3QsIGdyZWVuIGFuZCB3aGl0ZSIsCiAgICAibnVtX3BhbGV0dGVzIjogMywKICAgICJ0YXNrX3R5cGUiOiAiY29uY2VwdF9nZW5lcmF0aW9uIgp9Cg==`

4.  **Create a Mock CloudEvent Structure:**

    - Create a file named `mock_cloudevent.json`:
      ```json
      // mock_cloudevent.json
      {
        "specversion": "1.0",
        "type": "google.cloud.pubsub.topic.v1.messagePublished",
        "source": "//pubsub.googleapis.com/projects/local-test-project/topics/local-test-topic",
        "subject": "local-message-id-1",
        "id": "local-event-id-1",
        "time": "2024-05-01T18:00:00Z",
        "datacontenttype": "application/json",
        "data": {
          "message": {
            "data": "PASTE_YOUR_BASE64_ENCODED_PAYLOAD_HERE",
            "messageId": "local-message-id-1",
            "publishTime": "2024-05-01T18:00:00Z"
          },
          "subscription": "projects/local-test-project/subscriptions/local-test-sub"
        }
      }
      ```
    - **Replace** `PASTE_YOUR_BASE64_ENCODED_PAYLOAD_HERE` with the actual base64 string you generated in step 3.

5.  **Send the Mock Event to the Local Server:**

    - Open a **second terminal**.
    - Use `curl` to send the mock CloudEvent as an HTTP POST request:
      ```bash
      curl -X POST http://localhost:8080 \
           -H "Content-Type: application/cloudevents+json" \
           -d @mock_cloudevent.json
      ```
      - `-X POST`: Sends a POST request.
      - `-H "Content-Type: application/cloudevents+json"`: Sets the correct header expected by the framework for this signature type.
      - `-d @mock_cloudevent.json`: Sends the content of the file as the request body.

6.  **Observe the Worker Logs:**

    - Switch back to the **first terminal** (where `functions-framework` is running).
    - You should see the logs generated by your `handle_pubsub` function, including the "Processing Pub/Sub message..." log, logs from `initialize_services`, `process_pubsub_message`, and finally "Successfully processed task ID...".
    - If there are errors in your logic (e.g., connecting to Supabase locally, calling JigsawStack), they will appear here.

7.  **Repeat:** You can modify `mock_payload.json`, re-encode it, update `mock_cloudevent.json`, and send another `curl` request to test different scenarios without restarting the framework server.

This process allows you to thoroughly test your worker's core logic, including service initialization, message parsing, and the actual task processing (`process_pubsub_message`), in an environment that closely mimics how it will be invoked in Google Cloud Functions.
