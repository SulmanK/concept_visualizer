# Setting Up GitHub Actions for Data Cleanup

This document explains how to set up GitHub Actions to automatically trigger the Supabase Edge Function for cleaning up old concepts and color variations.

## GitHub Secret Setup

To ensure secure access to your Supabase Edge Function, you need to add your Supabase anon key as a GitHub secret:

1. Go to your GitHub repository
2. Click on "Settings" tab
3. In the left sidebar, click on "Secrets and variables" > "Actions"
4. Click on "New repository secret"
5. Enter the following information:
   - Name: `SUPABASE_ANON_KEY`
   - Value: ``
6. Click "Add secret"

## Understanding the Workflow

The GitHub Actions workflow `.github/workflows/schedule-cleanup.yml` does the following:

1. Runs at midnight UTC every day (`0 0 * * *`)
2. Makes an HTTP POST request to your Supabase Edge Function
3. Uses the Supabase anon key for authentication
4. Logs the success or failure of the function call

## Testing the Workflow

You can manually trigger this workflow to test it:

1. Go to your GitHub repository
2. Click on the "Actions" tab
3. In the left sidebar, select "Schedule Data Cleanup" workflow
4. Click on "Run workflow" > "Run workflow"

This will immediately trigger the workflow, which will call your Edge Function.

## Monitoring

To check if your scheduled cleanup is working:

1. Look at the GitHub Actions logs for the "Schedule Data Cleanup" workflow
2. Check your Supabase Edge Function logs in the Supabase dashboard
3. Query your database to ensure old concepts are being removed:
   ```sql
   SELECT COUNT(*) FROM concepts WHERE created_at < NOW() - INTERVAL '3 days';
   ```

## Troubleshooting

If the workflow fails:

1. Check if your Edge Function is deployed correctly and accessible
2. Ensure the SUPABASE_ANON_KEY secret is properly set in GitHub
3. Verify that your Edge Function doesn't require additional authorization headers
4. Look at the Edge Function logs in Supabase for any errors
