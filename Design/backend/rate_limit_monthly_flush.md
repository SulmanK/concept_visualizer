# Monthly Rate-Limit Flush Design Document

## Current Context

- The application enforces request quotas with a Redis-backed, sliding-window limiter (module `app.core.limiter`).
- Keys are stored in Upstash Redis under the pattern `ratelimit:<user|ip|token>:<endpoint>` and receive a TTL equal to the limit period (e.g. 30 days for a "10/month" rule).
- Sliding-window behaviour means that a user's counter only reaches zero after _period_ seconds of complete inactivity; this does _not_ align with calendar months.
- Product requirement: counters must reset for **all users** at 00:00 UTC on the 1st of each month so that monthly quotas are calendar-aligned.

## Requirements

### Functional Requirements

- A scheduled job must delete or otherwise invalidate all `ratelimit:*` keys once per calendar month.
- The reset must occur at 00:00 UTC on the 1st (tolerating a few minutes of drift).
- The job must succeed even if the Redis dataset is large (10⁵-10⁶ keys).
- The job must emit structured logs indicating: number of keys removed, duration, and success/failure.
- Failures must surface as Cloud Monitoring error logs and trigger existing alerting channels.

### Non-Functional Requirements

- **Performance** The flush should finish in < 5 minutes for 1 million keys.
- **Scalability** Solution must work without change if the dataset grows 10×.
- **Observability** Metrics/logs exported to Cloud Logging; optional custom metric `rate_limit_flush/keys_deleted`.
- **Security** Job runs under a dedicated service account with _only_ `roles/redis.editor` (or equivalent Upstash credentials) and logging permissions.

## Design Decisions

### 1. Execution Platform

- **Revised Choice:** GitHub Actions scheduled workflow.
  - **Rationale 1** Simplest path—no new GCP resources or Terraform; we already use Actions for CI/CD.
  - **Rationale 2** Secrets management is straightforward (`GITHUB_ACTIONS_SECRET`).
  - **Trade-offs** Slightly less precise start time (GitHub cron can drift by a few minutes) and dependency on GitHub availability.

### 2. Flush Strategy

**Chosen:** Key-pattern scan + batched `UNLINK` (non-blocking delete).

- Rationale 1 `UNLINK` frees memory asynchronously, avoiding Redis blockage.
- Rationale 2 Upstash limits to one pipeline per request; batching 1 000 keys per pipeline keeps within payload limits.
- Alternatives Renaming keys (versioning) or full DB FLUSHALL (too disruptive).

### 3. Scheduling

- GitHub Actions `schedule:` trigger with cron expression `0 0 1 * *` (runs shortly after 00:00 UTC every 1st day of the month).
- Workflow can also be executed manually (`workflow_dispatch`) for ad-hoc flushes or testing.

## Technical Design

### 1. Core Components

```python
# backend/cloud_run/worker/processors/flush_rate_limits.py
class RateLimitFlushProcessor:
    """Scans Redis for rate-limit keys and deletes them in batches."""

    BATCH_SIZE: int = 1000

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.logger = logging.getLogger(__name__)

    def run(self) -> None:
        start = time.time()
        deleted = 0
        cursor = 0
        pattern = "ratelimit:*"
        while True:
            cursor, keys = self.redis.scan(cursor=cursor, match=pattern, count=self.BATCH_SIZE)
            if keys:
                deleted += len(keys)
                # UNLINK is non-blocking; fall back to DEL if unavailable
                self.redis.unlink(*keys) if hasattr(self.redis, "unlink") else self.redis.delete(*keys)
            if cursor == 0:
                break
        self.logger.info("Monthly rate-limit flush complete", extra={"keys_deleted": deleted, "duration": time.time() - start})
```

### 2. Data Models

No new persistent data models.

### 3. Integration Points

- **Redis** Upstash instance already used by the limiter.
- **GitHub Actions** Workflow `flush_rate_limits.yml` (runs in GitHub-hosted runner) connects to Redis over TLS using secrets.

## Implementation Plan

1. **Phase 1 Script**

   - Add `scripts/maintenance/flush_rate_limits.py` containing the batched `SCAN` → `UNLINK` logic (see example in discussion).

2. **Phase 2 Workflow**

   - Create `.github/workflows/flush_rate_limits.yml` with:
     - `schedule:` cron `0 0 1 * *` and `workflow_dispatch`.
     - Steps: checkout, setup-python, `pip install redis`, run the script.
     - Secrets: `PROD_UPSTASH_REDIS_ENDPOINT`, `PROD_UPSTASH_REDIS_PASSWORD`, `PROD_UPSTASH_REDIS_PORT` (and equivalents for `dev` if needed).

3. **Phase 3 Monitoring**
   - Rely on GitHub job status (failure e-mails) plus log output.
   - Optional: add a step to post summary to Slack/Teams if the run fails or deletes zero keys.

## Testing Strategy

### Unit Tests

- Mock Redis client and assert that `scan` + `unlink` are called with correct batch sizes.

### Integration Tests

- Stage environment with seeded keys; run job manually and verify keys are gone and logs are correct.

## Observability

- **Logging** Structured `info` log summarising deletion stats.
- **Metrics** Custom metric `rate_limit_flush/keys_deleted`.

## Future Considerations

- Replace monthly flush with calendar-aware key naming (e.g. `ratelimit:<...>:<YYYYMM>`) to avoid deletion overhead.
- Automate ad-hoc flush on demand via authenticated HTTP trigger.

## Dependencies

- `redis>=4.6` (already in requirements).

## Security Considerations

- Redis credentials stored as GitHub Actions encrypted secrets; least-privilege principle (read/write access only). No GCP IAM changes required.

## Rollout Strategy

1. Commit script + workflow to a feature branch.
2. Run workflow manually (`workflow_dispatch`) in **dev** to verify correct deletion and logging.
3. Merge to `main`; the scheduled trigger will run on the next 1st of the month.

## References

- Upstash docs: https://docs.upstash.com/redis/commands/scan
- Cloud Run Jobs: https://cloud.google.com/run/docs/jobs
