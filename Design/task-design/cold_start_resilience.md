# Cold Start Resilience Design Document

## Problem Statement

After 20 days of service inactivity, the Concept Visualizer experiences intermittent failures due to cold start issues in the distributed architecture. The primary failure point is Cloud Functions with `min_instance_count = 0`, but secondary issues include connection timeouts that don't account for cold start delays.

## Current Architecture Analysis

### Affected Components

1. **Cloud Function Workers** (Primary Issue)

   - Default `worker_min_instances = 0`
   - Scale down to zero after inactivity
   - Cold start time: 10-30 seconds including service initialization
   - Current timeout: 540 seconds (9 minutes) - adequate but initialization fails

2. **Redis Connections** (Secondary)

   - Socket timeout: 3 seconds
   - Connect timeout: 3 seconds
   - May fail during cold start due to service initialization delays

3. **Authentication Tokens** (Secondary)

   - Supabase JWT tokens may expire
   - Anonymous sessions need refresh after long periods

4. **External API Connections** (Secondary)
   - JigsawStack API connections
   - 90-second timeout but may fail during cold start

## Design Goals

1. **Minimize Cold Start Impact**: Reduce the frequency of cold starts
2. **Improve Cold Start Resilience**: Handle cold starts gracefully when they occur
3. **Graceful Degradation**: Provide user feedback during cold start periods
4. **Cost Optimization**: Balance always-on costs vs. cold start user experience

## Proposed Solutions

### Solution 1: Minimum Instance Configuration (Recommended)

**Approach**: Set minimum instances for production environments to maintain warm instances.

**Implementation**:

```hcl
# terraform/environments/prod.tfvars
worker_min_instances = 1  # Keep 1 instance warm in prod

# terraform/environments/dev.tfvars
worker_min_instances = 0  # Dev can tolerate cold starts for cost savings
```

**Pros**:

- Eliminates cold starts in production
- Simple configuration change
- Immediate improvement for users

**Cons**:

- Increased cost (~$15-30/month for 1 always-on instance)

**Cost Analysis**:

- Cloud Function (512MB, always-on): ~$15-25/month
- Worth it for production user experience

### Solution 2: Enhanced Cold Start Resilience

**Approach**: Improve timeouts and retry logic to handle cold starts gracefully.

**Implementation**:

1. **Increase Redis Connection Timeouts for Cold Starts**:

```python
# backend/app/core/limiter/redis_store.py
def get_redis_client() -> Optional[Redis]:
    try:
        # Increase timeouts for cold start resilience
        client = cast(
            Redis,
            redis.from_url(
                redis_url,
                socket_timeout=10,  # Increased from 3
                socket_connect_timeout=10,  # Increased from 3
                retry_on_timeout=True,
                retry_on_error=[redis.ConnectionError],  # Add connection error retry
                retry=redis.Retry(redis.LinearBackoff(base=1), retries=3),
                health_check_interval=30,  # Increased from 15
                decode_responses=True,
            ),
        )
```

2. **Add Retry Logic for Service Initialization**:

```python
# backend/cloud_run/worker/main.py
SERVICES_GLOBAL = None
INITIALIZATION_RETRIES = 3
INITIALIZATION_DELAY = 2  # seconds

def initialize_services_with_retry():
    global SERVICES_GLOBAL

    for attempt in range(1, INITIALIZATION_RETRIES + 1):
        try:
            # ... existing initialization code ...
            SERVICES_GLOBAL = {
                "image_service": _image_service_global,
                # ... rest of services
            }
            logger.info(f"Global services initialized successfully on attempt {attempt}")
            return
        except Exception as e:
            logger.warning(f"Service initialization attempt {attempt} failed: {e}")
            if attempt < INITIALIZATION_RETRIES:
                time.sleep(INITIALIZATION_DELAY * attempt)  # Exponential backoff
            else:
                logger.critical(f"Failed to initialize services after {INITIALIZATION_RETRIES} attempts")
                SERVICES_GLOBAL = None
                raise
```

### Solution 3: Frontend Cold Start Awareness

**Approach**: Provide user feedback and implement retry logic for cold start scenarios.

**Implementation**:

1. **Add Cold Start Detection**:

```typescript
// frontend/src/services/apiClient.ts
const COLD_START_INDICATORS = [
  "timeout",
  "connection reset",
  "temporarily unavailable",
  "function not ready",
];

const isColdStartError = (error: any): boolean => {
  const message = error.message?.toLowerCase() || "";
  return COLD_START_INDICATORS.some((indicator) => message.includes(indicator));
};
```

2. **Enhanced Retry Logic with User Feedback**:

```typescript
// frontend/src/hooks/useConceptGeneration.ts
const useConceptGeneration = () => {
  const [isColdStart, setIsColdStart] = useState(false);

  const generateConcept = async (prompt: string) => {
    try {
      setIsColdStart(false);
      return await apiCall(prompt);
    } catch (error) {
      if (isColdStartError(error)) {
        setIsColdStart(true);
        // Show cold start message to user
        // Implement retry with exponential backoff
        return await retryWithBackoff(apiCall, prompt, {
          maxRetries: 3,
          baseDelay: 5000, // 5 seconds
          message: "Service is starting up, please wait...",
        });
      }
      throw error;
    }
  };

  return { generateConcept, isColdStart };
};
```

3. **Cold Start UI Feedback**:

```tsx
// frontend/src/components/ColdStartNotification.tsx
const ColdStartNotification = ({ isVisible }: { isVisible: boolean }) => {
  if (!isVisible) return null;

  return (
    <div className="cold-start-notification">
      <div className="spinner" />
      <h3>Service Starting Up</h3>
      <p>
        The service hasn't been used recently and is starting up. This may take
        30-60 seconds.
      </p>
      <p>Your request will be processed automatically once ready.</p>
    </div>
  );
};
```

### Solution 4: Health Check and Warmup

**Approach**: Implement warmup endpoints and proactive health checks.

**Implementation**:

1. **Add Warmup Endpoint**:

```python
# backend/app/api/routes/health/health_routes.py
@router.get("/warmup")
async def warmup():
    """Warmup endpoint to initialize services."""
    try:
        # Trigger service initialization
        from app.cloud_run.worker.main import SERVICES_GLOBAL
        if SERVICES_GLOBAL is None:
            from app.cloud_run.worker.main import initialize_services_with_retry
            initialize_services_with_retry()

        return {"status": "warmed_up", "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        logger.error(f"Warmup failed: {e}")
        raise HTTPException(status_code=503, detail="Warmup failed")
```

2. **Scheduled Warmup (Optional)**:

```yaml
# .github/workflows/warmup.yml
name: Service Warmup
on:
  schedule:
    - cron: "0 */6 * * *" # Every 6 hours
jobs:
  warmup:
    runs-on: ubuntu-latest
    steps:
      - name: Warmup Production
        run: |
          curl -f ${{ secrets.PROD_API_URL }}/api/health/warmup
      - name: Warmup Development
        run: |
          curl -f ${{ secrets.DEV_API_URL }}/api/health/warmup
```

## Implementation Phases

### Phase 1: Quick Fix (Immediate)

- [ ] Update `prod.tfvars` to set `worker_min_instances = 1`
- [ ] Apply terraform changes to production
- [ ] Monitor for improved reliability

### Phase 2: Enhanced Resilience (Week 1)

- [ ] Implement increased Redis timeouts
- [ ] Add service initialization retry logic
- [ ] Add warmup endpoint
- [ ] Test cold start scenarios

### Phase 3: User Experience (Week 2)

- [ ] Implement frontend cold start detection
- [ ] Add cold start UI notifications
- [ ] Implement retry logic with user feedback
- [ ] Add monitoring for cold start events

### Phase 4: Monitoring and Optimization (Week 3)

- [ ] Add cold start metrics to monitoring
- [ ] Implement alerting for cold start issues
- [ ] Optimize cold start performance
- [ ] Cost analysis and optimization

## Testing Strategy

### Cold Start Simulation

1. Scale function to zero instances manually
2. Wait for scale-down (5-10 minutes)
3. Trigger request and measure response time
4. Verify retry logic and user feedback

### Load Testing

1. Test concurrent requests during cold start
2. Verify service stability under load
3. Measure performance impact of changes

## Success Metrics

1. **Reliability**: 99.9% success rate for requests (up from current intermittent failures)
2. **Performance**: Cold start requests complete within 60 seconds
3. **User Experience**: Clear feedback during cold start periods
4. **Cost**: Maintain reasonable operational costs (<$50/month increase)

## Risks and Mitigation

### Risk: Increased Costs

**Mitigation**: Start with prod-only minimum instances, monitor usage patterns

### Risk: Still Some Cold Starts

**Mitigation**: Enhanced retry logic and user communication

### Risk: Complexity in Error Handling

**Mitigation**: Comprehensive testing and monitoring

## Conclusion

The recommended approach is a **hybrid solution**:

- **Phase 1**: Immediate fix with `worker_min_instances = 1` for production
- **Phases 2-3**: Enhanced resilience for remaining edge cases
- **Phase 4**: Long-term monitoring and optimization

This provides immediate user experience improvement while building robust handling for any remaining cold start scenarios.
