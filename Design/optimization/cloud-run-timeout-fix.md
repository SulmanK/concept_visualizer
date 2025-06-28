# Cloud Run Worker Timeout Fix

## Problem Statement

The Cloud Run worker function was timing out at exactly 540 seconds (9 minutes) during the palette variation processing phase. The function would successfully:

1. Generate the base concept image
2. Store the base image
3. Generate color palettes
4. Start "parallel processing of 7 palette variations"

But then timeout before completing the palette variations.

## Root Cause Analysis

The issue was caused by **resource contention** during parallel processing:

1. **CPU Bottleneck**: Processing 7 high-resolution images concurrently overwhelmed the single CPU core in Cloud Run
2. **Memory Pressure**: Even with 2GB memory, concurrent image processing consumed significant RAM
3. **I/O Saturation**: Concurrent uploads to Supabase storage hit bandwidth/rate limits

The "parallel processing" was actually creating **resource starvation** rather than improving performance.

## Solution Implemented

### 1. Concurrency Limiting with Semaphore

Added `asyncio.Semaphore` to limit concurrent palette variations:

```python
# Create a semaphore to limit concurrent processing
max_concurrent = min(config_limit, len(palettes))  # Default: 3 concurrent operations
semaphore = asyncio.Semaphore(max_concurrent)
```

### 2. Individual Operation Timeouts

Added timeout for each palette variation to prevent hanging:

```python
return await asyncio.wait_for(
    self._process_single_palette_variation(...),
    timeout=float(timeout_seconds)  # Default: 120 seconds
)
```

### 3. Configuration Options

Added environment variables for fine-tuning:

- `CONCEPT_PALETTE_PROCESSING_CONCURRENCY_LIMIT`: Max concurrent operations (default: 3)
- `CONCEPT_PALETTE_PROCESSING_TIMEOUT_SECONDS`: Individual operation timeout (default: 120)

### 4. Enhanced Error Handling

Improved error reporting to distinguish between:

- Individual palette failures (logged but doesn't fail entire batch)
- Timeout errors (clearly identified)
- Resource errors (memory/CPU related)

## Quick Fix (Deploy Immediately)

To fix the timeout issue right now while deploying the code changes:

```bash
# Set your function name and project
FUNCTION_NAME="concept-viz-prod-worker-prod"
PROJECT_ID="your-project-id"
REGION="us-east1"

# Update the function with better resources and configuration
gcloud functions deploy $FUNCTION_NAME \
  --gen2 \
  --project=$PROJECT_ID \
  --region=$REGION \
  --timeout=600s \
  --memory=4096Mi \
  --cpu=2 \
  --update-env-vars="CONCEPT_PALETTE_PROCESSING_CONCURRENCY_LIMIT=2,CONCEPT_PALETTE_PROCESSING_TIMEOUT_SECONDS=180" \
  --quiet

echo "✅ Cloud Function updated with better timeout and concurrency settings"
```

**Note**: Replace `your-project-id` with your actual GCP project ID. This will take effect immediately after deployment.

## Cloud Run/Cloud Function Configuration Changes

### Immediate Infrastructure Fix

Update your deployment to increase resources and timeout:

```bash
# For Cloud Function (current setup)
gcloud functions deploy concept-viz-prod-worker-prod \
  --gen2 \
  --runtime=python311 \
  --timeout=600s \
  --memory=4096Mi \
  --cpu=2 \
  --set-env-vars="CONCEPT_PALETTE_PROCESSING_CONCURRENCY_LIMIT=2,CONCEPT_PALETTE_PROCESSING_TIMEOUT_SECONDS=180" \
  # ... other flags
```

### Terraform Configuration Updates

Update your `terraform/variables.tf`:

```hcl
variable "worker_memory" {
  description = "Memory allocation for the Cloud Function worker."
  type        = string
  default     = "4096Mi"  # Increased from 2048Mi
}

variable "worker_cpu" {
  description = "CPU allocation for the Cloud Function worker."
  type        = string
  default     = "2"  # Increased from 1
}

variable "worker_timeout" {
  description = "Timeout for the Cloud Function worker in seconds."
  type        = number
  default     = 600  # Increased from 540
}
```

Update your `terraform/cloud_function.tf`:

```hcl
service_config {
  timeout_seconds     = var.worker_timeout
  available_memory    = var.worker_memory
  available_cpu       = var.worker_cpu

  environment_variables = {
    # ... existing vars ...
    CONCEPT_PALETTE_PROCESSING_CONCURRENCY_LIMIT = "2"
    CONCEPT_PALETTE_PROCESSING_TIMEOUT_SECONDS   = "180"
  }
}
```

## Performance Benefits

### Before Fix

- **Timeout**: 540 seconds (function timeout)
- **Success Rate**: 0% (all timeouts)
- **Resource Usage**: CPU/Memory spikes, then timeout

### After Fix

- **Expected Time**: 3-4 minutes for 7 palettes
- **Success Rate**: High (individual failures don't block others)
- **Resource Usage**: Controlled, sustainable load

### Calculation

With 2 concurrent operations and more CPU:

- **Sequential**: 7 palettes × 60 seconds = 420 seconds
- **Concurrent (2)**: ceil(7/2) × 45 seconds = 180 seconds (faster with 2 CPUs)
- **Overhead**: ~30 seconds for coordination
- **Total**: ~210 seconds (3.5 minutes)

## Configuration Recommendations

### For Production (High Volume)

```bash
# Environment Variables
CONCEPT_PALETTE_PROCESSING_CONCURRENCY_LIMIT=2
CONCEPT_PALETTE_PROCESSING_TIMEOUT_SECONDS=180

# Cloud Function Resources
--memory=4096Mi
--cpu=2
--timeout=600s
```

### For Development (Faster Testing)

```bash
# Environment Variables
CONCEPT_PALETTE_PROCESSING_CONCURRENCY_LIMIT=3
CONCEPT_PALETTE_PROCESSING_TIMEOUT_SECONDS=120

# Cloud Function Resources
--memory=2048Mi
--cpu=1
--timeout=540s
```

### For High-Memory Instances

```bash
# Environment Variables
CONCEPT_PALETTE_PROCESSING_CONCURRENCY_LIMIT=4
CONCEPT_PALETTE_PROCESSING_TIMEOUT_SECONDS=90

# Cloud Function Resources
--memory=8192Mi
--cpu=4
--timeout=480s
```

## Cloud Run Resource Recommendations

### CPU and Memory

- **Current**: 1 CPU, 2GB RAM
- **Recommended**: 2 CPU, 4GB RAM (for production)
- **Budget Alternative**: 1 CPU, 4GB RAM with concurrency limit of 2

### Timeout Settings

- **Current**: 540 seconds
- **Recommended**: 600 seconds (10 minutes for safety margin)

### Concurrency

- **Current**: 1 (one request per instance)
- **Recommended**: Keep at 1 (image processing is resource-intensive)

## Monitoring and Alerts

Add monitoring for:

1. **Function Duration**: Should be consistently under 5 minutes
2. **Individual Palette Timeouts**: Should be rare
3. **Memory Usage**: Should stay under 80% of allocated
4. **CPU Usage**: Should have breathing room

## Future Optimizations

1. **Image Size Optimization**: Reduce base image resolution before processing
2. **Chunked Processing**: Break large palette sets into smaller batches
3. **External Processing**: Use specialized image processing services
4. **Caching**: Cache processed variations for similar palettes

## Testing Strategy

1. **Load Test**: Process concepts with 7+ palettes
2. **Resource Monitoring**: Monitor CPU/memory during processing
3. **Timeout Testing**: Verify individual timeouts work correctly
4. **Error Recovery**: Test partial failures handle gracefully

## Implementation Notes

- The fix is backward compatible
- Configuration defaults preserve existing behavior
- Logging provides visibility into performance
- Graceful degradation for individual palette failures
