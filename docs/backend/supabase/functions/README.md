# Supabase Edge Functions

## Overview

Edge Functions in Supabase allow you to write and deploy serverless functions that run on Supabase's infrastructure. These functions can be used for a variety of use cases, such as:

- Custom API endpoints
- Scheduled background jobs
- Webhook handlers
- Data processing and transformation

## Available Functions

| Function                              | Description                                                    |
| ------------------------------------- | -------------------------------------------------------------- |
| [cleanup-old-data](cleanup-old-data/) | Automatically cleans up old concepts, tasks, and storage files |

## Function Structure

Each Edge Function is deployed as a separate module with its own entry point. The standard structure for a function is:

```
functions/
└── function-name/
    ├── index.ts        # Main entry point
    ├── README.md       # Documentation
    └── (other files)   # Supporting modules and files
```

## Common Patterns

Functions commonly use these patterns:

1. **Database Access**: Using Supabase client to interact with the database
2. **Storage Operations**: Managing files in storage buckets
3. **Environment Variables**: Reading configuration from environment variables
4. **Error Handling**: Structured error catching and reporting
5. **Logging**: Extensive logging for debugging and monitoring

## Deployment and Testing

Functions can be deployed using the Supabase CLI:

```bash
supabase functions deploy <function-name> --project-ref <project-ref>
```

See the [testing documentation](../../../tests/supabase_edge_function/) for details on testing the functions.
