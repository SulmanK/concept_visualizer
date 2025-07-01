# Monthly Rate-Limit Flush Workflow

This document describes the GitHub Actions workflow that resets all `ratelimit:*` keys in Upstash Redis at the start of each calendar month.

## Purpose

Some API endpoints enforce "N per month" quotas. Because the current implementation uses a sliding-window limiter, counters do not automatically return to zero on the 1st of the month. The **monthly flush** job resets every user's quota so that they start each month with a clean slate.

## Trigger

| Type                | Cron Expression | Time Zone                                          |
| ------------------- | --------------- | -------------------------------------------------- |
| `schedule`          | `0 0 1 * *`     | UTC (runs a few minutes after midnight on the 1st) |
| `workflow_dispatch` | –               | Allows manual or ad-hoc execution                  |

## Secrets

The workflow relies on the following encrypted secrets (per environment):

| Secret Name                   | Description                                                |
| ----------------------------- | ---------------------------------------------------------- |
| `PROD_UPSTASH_REDIS_ENDPOINT` | Hostname of the Upstash Redis instance (without protocol). |
| `PROD_UPSTASH_REDIS_PASSWORD` | Password for the Redis instance.                           |
| `PROD_UPSTASH_REDIS_PORT`     | (Optional) Port number; defaults to `6379` if omitted.     |
| `DEV_UPSTASH_REDIS_*`         | Same variables for the **dev** environment (optional).     |

Store these secrets under **Repository Settings → Secrets and variables → Actions**.

## Key Files

- **Workflow** ‑ `.github/workflows/flush_rate_limits.yml`
- **Script** ‑ `scripts/maintenance/flush_rate_limits.py`

## Workflow Steps

1. **Checkout** the repository.
2. **Setup Python** (version 3.11).
3. **Install Dependencies** – `pip install redis==4.6.0`.
4. **Run Flush Script** – executes `python scripts/maintenance/flush_rate_limits.py` which:
   1. Connects to Redis via `rediss://` using the secrets.
   2. Iterates with `SCAN` (batch size 1 000) over keys matching `ratelimit:*`.
   3. Deletes each batch using `UNLINK` (falls back to `DEL` if unavailable).
   4. Logs the number of keys removed and duration.

## Monitoring & Alerts

- The job's success/failure status appears in the **Actions** tab.
- GitHub sends failure notifications to users watching the repo.
- A follow-up enhancement (future work) could post Slack/Teams messages or push metrics to Cloud Monitoring.

## Manual Execution (Ad-Hoc Flush)

Navigate to **Actions → Monthly rate-limit flush → Run workflow**, select the branch, and click **Run workflow**.

## Related Design Document

See `Design/backend/rate_limit_monthly_flush.md` for rationale, implementation plan, and future considerations.
