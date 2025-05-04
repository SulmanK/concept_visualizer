# Cloud Function Worker Testing

This directory contains tools for testing the Cloud Function worker locally, which processes Pub/Sub messages for concept generation and refinement.

## Prerequisites

1. Ensure you have the `functions-framework` package installed:

   ```bash
   uv pip install functions-framework
   ```

2. Make sure your `.env.develop` file has the necessary environment variables:
   ```
   CONCEPT_SUPABASE_URL=...
   CONCEPT_SUPABASE_KEY=...
   CONCEPT_SUPABASE_SERVICE_ROLE=...
   CONCEPT_SUPABASE_JWT_SECRET=...
   CONCEPT_JIGSAWSTACK_API_KEY=...
   CONCEPT_UPSTASH_REDIS_ENDPOINT=...
   CONCEPT_UPSTASH_REDIS_PASSWORD=...
   CONCEPT_UPSTASH_REDIS_PORT=6379
   CONCEPT_DB_TABLE_TASKS=tasks_dev
   CONCEPT_DB_TABLE_CONCEPTS=concepts_dev
   CONCEPT_DB_TABLE_PALETTES=color_variations_dev
   CONCEPT_STORAGE_BUCKET_CONCEPT=concept-images-dev
   CONCEPT_STORAGE_BUCKET_PALETTE=palette-images-dev
   CONCEPT_LOG_LEVEL=DEBUG
   ```

## Test Files

- `mock_payload.json` - A sample task payload like what would be sent to Pub/Sub
- `prepare_test_event.py` - Script to encode the payload and prepare a CloudEvent
- `test_worker.sh` (Unix/Mac) or `test_worker.ps1` (Windows) - Scripts to run the test

## Testing Process

### Automated Testing

Run the appropriate script for your platform:

**Unix/Mac:**

```bash
cd backend
chmod +x tests/cloud_run/test_worker.sh
./tests/cloud_run/test_worker.sh
```

**Windows (PowerShell):**

```powershell
cd backend
.\tests\cloud_run\test_worker.ps1
```

### Manual Testing

1. **First, prepare the CloudEvent:**

   ```bash
   cd backend
   python tests/cloud_run/prepare_test_event.py
   ```

2. **Start the Functions Framework in one terminal:**

   ```bash
   cd backend
   # Load environment variables first (Unix/Mac)
   export $(cat .env.develop | xargs)
   # For Windows PowerShell, you may need to load variables differently
   # Get-Content .env.develop | ForEach-Object { if ($_ -match '^[^#]') { $env:$($_.Split('=')[0])=$_.Substring($_.IndexOf('=')+1) } }

   functions-framework --source=cloud_run/worker/main.py --target=handle_pubsub --signature-type=cloudevent --port=8080
   ```

3. **Send the test request from another terminal:**
   ```bash
   cd backend
   curl -X POST http://localhost:8080 \
        -H "Content-Type: application/cloudevents+json" \
        -d @tests/cloud_run/mock_cloudevent.json
   ```

## Troubleshooting

- **Missing environment variables:** Ensure all required environment variables are set
- **Port already in use:** Make sure no other service is running on port 8080
- **Installation issues:** Verify functions-framework is installed correctly
- **Permission denied:** For Unix/Mac, make sure the shell script is executable (`chmod +x`)

## Customizing Tests

You can modify `mock_payload.json` to test different scenarios, such as:

- Different descriptions
- Varying number of palettes
- Different task types (concept_generation vs concept_refinement)

After modifying, run `prepare_test_event.py` again to regenerate the CloudEvent.
