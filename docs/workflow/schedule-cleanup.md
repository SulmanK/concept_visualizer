# Schedule Data Cleanup Workflow

## Overview

The `Schedule Data Cleanup` workflow automates regular data maintenance tasks by triggering a serverless function deployed on Supabase. This workflow helps manage database growth, remove outdated information, and ensure optimal application performance.

## Triggers

This workflow runs:

- Hourly on a schedule (cron: `0 * * * *`)
- Manually via GitHub Actions interface (workflow_dispatch) for testing or ad-hoc cleanup

## Workflow Structure

### Call Cleanup Function

**Job name**: `call-cleanup-function`

This job is responsible for:

1. Determining the environment (dev or prod) based on the current branch
2. Setting appropriate environment variables for the target Supabase endpoint
3. Making an HTTP POST request to the cleanup function endpoint
4. Logging the completion status

#### Environment Selection

The workflow dynamically selects the environment configuration:

- If running on the `main` branch, it uses production environment variables
- Otherwise, it defaults to development environment variables

#### Cleanup Function Call

The cleanup is performed by sending a POST request to a Supabase Edge Function:

- Uses the appropriate Supabase URL for the environment
- Authenticates with the environment-specific Supabase anonymous key
- Sets the proper Content-Type header

#### Logging

The workflow provides clear logging:

- Success message when the function executes successfully
- Failure message if the function call fails

## Function Behavior

The Supabase Edge Function that gets called is responsible for:

- Removing stale or expired data
- Cleaning up temporary resources
- Archiving old records
- Maintaining database size and performance

## Configuration Requirements

This workflow requires the following repository secrets:

- `PROD_SUPABASE_ANON_KEY`: The anonymous API key for the production Supabase instance
- `DEV_SUPABASE_ANON_KEY`: The anonymous API key for the development Supabase instance

## Error Handling

The workflow includes basic error handling:

- The curl command will return a non-zero exit code if it fails
- The failure step will only execute if the previous step fails
- Success and failure states are clearly reported in the workflow logs

## Customization

To customize this workflow:

1. Change the cron schedule to adjust frequency
2. Modify the Supabase function URL endpoints
3. Add additional parameters to the Supabase function call
4. Implement more sophisticated error handling or notifications
