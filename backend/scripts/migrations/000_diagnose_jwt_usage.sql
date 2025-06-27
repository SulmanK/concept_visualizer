-- Diagnostic script: Find what's using auth.get_jwt functions
-- Run this in your Supabase SQL Editor to identify usage

-- 1. Check if the functions actually exist
SELECT
    routine_name,
    routine_schema,
    routine_definition
FROM information_schema.routines
WHERE routine_name IN ('get_jwt_from_url', 'get_jwt')
AND routine_schema = 'auth';

-- 2. Find any RLS policies that reference these functions
SELECT
    schemaname,
    tablename,
    policyname,
    definition
FROM pg_policies
WHERE definition LIKE '%auth.get_jwt%';

-- 3. Check for any policies that use session_id extraction patterns
SELECT
    schemaname,
    tablename,
    policyname,
    definition
FROM pg_policies
WHERE definition LIKE '%session_id%';

-- 4. Look for any views that might use these functions
SELECT
    table_schema,
    table_name,
    view_definition
FROM information_schema.views
WHERE view_definition LIKE '%auth.get_jwt%';

-- 5. Check for any stored procedures/functions that reference them
SELECT
    routine_name,
    routine_schema,
    routine_definition
FROM information_schema.routines
WHERE routine_definition LIKE '%auth.get_jwt%'
AND routine_schema != 'auth';

-- 6. Look for any triggers that might use these functions
SELECT
    trigger_name,
    event_object_table,
    action_statement
FROM information_schema.triggers
WHERE action_statement LIKE '%auth.get_jwt%';

-- 7. Show all current storage policies for reference
SELECT
    schemaname,
    tablename,
    policyname,
    definition
FROM pg_policies
WHERE tablename = 'objects'
AND schemaname = 'storage'
ORDER BY policyname;
