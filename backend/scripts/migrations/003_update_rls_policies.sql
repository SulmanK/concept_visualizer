-- Migration: Update RLS policies to use public schema auth functions
-- Date: 2024-01-XX
-- Reason: Following migration of auth functions from auth to public schema

-- First, let's check and update storage bucket policies
-- These are the policies that typically use auth.get_jwt_from_url()

-- Drop existing storage policies that might reference auth.get_jwt_from_url()
DROP POLICY IF EXISTS "Users can view their own concept images" ON storage.objects;
DROP POLICY IF EXISTS "Users can insert their own concept images" ON storage.objects;
DROP POLICY IF EXISTS "Users can update their own concept images" ON storage.objects;
DROP POLICY IF EXISTS "Users can delete their own concept images" ON storage.objects;

DROP POLICY IF EXISTS "Users can view their own palette images" ON storage.objects;
DROP POLICY IF EXISTS "Users can insert their own palette images" ON storage.objects;
DROP POLICY IF EXISTS "Users can update their own palette images" ON storage.objects;
DROP POLICY IF EXISTS "Users can delete their own palette images" ON storage.objects;

-- Recreate storage policies using public schema functions
-- Concept images bucket policies
CREATE POLICY "Users can view their own concept images"
ON storage.objects FOR SELECT
TO authenticated, anon
USING (
  bucket_id = 'concept-images' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

CREATE POLICY "Users can insert their own concept images"
ON storage.objects FOR INSERT
TO authenticated, anon
WITH CHECK (
  bucket_id = 'concept-images' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

CREATE POLICY "Users can update their own concept images"
ON storage.objects FOR UPDATE
TO authenticated, anon
USING (
  bucket_id = 'concept-images' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

CREATE POLICY "Users can delete their own concept images"
ON storage.objects FOR DELETE
TO authenticated, anon
USING (
  bucket_id = 'concept-images' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

-- Palette images bucket policies
CREATE POLICY "Users can view their own palette images"
ON storage.objects FOR SELECT
TO authenticated, anon
USING (
  bucket_id = 'palette-images' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

CREATE POLICY "Users can insert their own palette images"
ON storage.objects FOR INSERT
TO authenticated, anon
WITH CHECK (
  bucket_id = 'palette-images' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

CREATE POLICY "Users can update their own palette images"
ON storage.objects FOR UPDATE
TO authenticated, anon
USING (
  bucket_id = 'palette-images' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

CREATE POLICY "Users can delete their own palette images"
ON storage.objects FOR DELETE
TO authenticated, anon
USING (
  bucket_id = 'palette-images' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

-- Note: The above policies use auth.uid() which is still supported
-- If you have any policies that specifically use the custom JWT functions,
-- update them to use public.get_jwt() or public.get_jwt_from_url()

-- Example of how to update a policy that uses custom JWT extraction:
-- CREATE POLICY "Custom JWT policy example"
-- ON some_table FOR SELECT
-- USING (
--   user_id = (public.get_jwt() ->> 'session_id')::text
-- );

-- Check for any other policies that might need updating
-- You can run this query to find policies that reference the old functions:
-- SELECT schemaname, tablename, policyname, definition
-- FROM pg_policies
-- WHERE definition LIKE '%auth.get_jwt%';
