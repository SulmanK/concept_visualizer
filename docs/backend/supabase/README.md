# Supabase Functions

This directory contains documentation for the Supabase Edge Functions used in the Concept Visualizer application.

## Overview

Supabase Edge Functions are serverless functions that run on Supabase's infrastructure. They allow us to run custom server-side logic without managing servers. In this application, edge functions are used for maintenance tasks and background processing.

## Available Functions

### [cleanup-old-data](functions/cleanup-old-data/)

This function performs automated cleanup of old data in the database and storage, helping to manage storage costs and maintain application performance. It:

- Deletes concepts and associated data older than 30 days
- Cleans up stuck tasks that have been in processing or pending state for too long
- Removes associated files from Supabase storage buckets

## Deployment

Edge functions are deployed directly to Supabase using the Supabase CLI:

```bash
supabase functions deploy cleanup-old-data --project-ref your-project-ref
```

## Environment Variables

Edge functions use the following environment variables:

- `SUPABASE_URL`: The URL of your Supabase project
- `SUPABASE_SERVICE_ROLE_KEY`: The service role key for Supabase admin operations
- `APP_ENVIRONMENT`: The environment (dev or prod) determining which tables to use
- `STORAGE_BUCKET_CONCEPT`: The name of the concept images storage bucket
- `STORAGE_BUCKET_PALETTE`: The name of the palette images storage bucket

## Testing

Edge functions can be tested locally or remotely. See the [test script](../../tests/supabase_edge_function/test_cleanup_function.py) for an example of testing the cleanup function.
