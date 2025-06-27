-- Migration: Ensure development storage policies are compatible with auth function migration
-- Date: 2024-01-XX
-- Reason: Update dev environment storage policies to match production setup

-- This file updates the development environment storage policies
-- to ensure consistency with production after the auth function migration

-- Drop existing storage policies to ensure clean state
DROP POLICY IF EXISTS "Users can view their own concept images" ON storage.objects;
DROP POLICY IF EXISTS "Users can insert their own concept images" ON storage.objects;
DROP POLICY IF EXISTS "Users can update their own concept images" ON storage.objects;
DROP POLICY IF EXISTS "Users can delete their own concept images" ON storage.objects;

DROP POLICY IF EXISTS "Users can view their own palette images" ON storage.objects;
DROP POLICY IF EXISTS "Users can insert their own palette images" ON storage.objects;
DROP POLICY IF EXISTS "Users can update their own palette images" ON storage.objects;
DROP POLICY IF EXISTS "Users can delete their own palette images" ON storage.objects;

-- Also drop the auth+anon versions in case they exist
DROP POLICY IF EXISTS "Users (auth+anon) can view their own concept images" ON storage.objects;
DROP POLICY IF EXISTS "Users (auth+anon) can upload their own concept images" ON storage.objects;
DROP POLICY IF EXISTS "Users (auth+anon) can update their own concept images" ON storage.objects;
DROP POLICY IF EXISTS "Users (auth+anon) can delete their own concept images" ON storage.objects;

DROP POLICY IF EXISTS "Users (auth+anon) can view their own palette images" ON storage.objects;
DROP POLICY IF EXISTS "Users (auth+anon) can upload their own palette images" ON storage.objects;
DROP POLICY IF EXISTS "Users (auth+anon) can update their own palette images" ON storage.objects;
DROP POLICY IF EXISTS "Users (auth+anon) can delete their own palette images" ON storage.objects;

-- Recreate concept images bucket policies (Development buckets)
-- Note: Using 'concept-images' for dev environment (without -prod suffix)
CREATE POLICY "Users (auth+anon) can view their own concept images"
ON storage.objects FOR SELECT
TO authenticated, anon
USING (
  bucket_id = 'concept-images' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

CREATE POLICY "Users (auth+anon) can upload their own concept images"
ON storage.objects FOR INSERT
TO authenticated, anon
WITH CHECK (
  bucket_id = 'concept-images' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

CREATE POLICY "Users (auth+anon) can update their own concept images"
ON storage.objects FOR UPDATE
TO authenticated, anon
USING (
  bucket_id = 'concept-images' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

CREATE POLICY "Users (auth+anon) can delete their own concept images"
ON storage.objects FOR DELETE
TO authenticated, anon
USING (
  bucket_id = 'concept-images' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

-- Recreate palette images bucket policies (Development buckets)
-- Note: Using 'palette-images' for dev environment (without -prod suffix)
CREATE POLICY "Users (auth+anon) can view their own palette images"
ON storage.objects FOR SELECT
TO authenticated, anon
USING (
  bucket_id = 'palette-images' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

CREATE POLICY "Users (auth+anon) can upload their own palette images"
ON storage.objects FOR INSERT
TO authenticated, anon
WITH CHECK (
  bucket_id = 'palette-images' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

CREATE POLICY "Users (auth+anon) can update their own palette images"
ON storage.objects FOR UPDATE
TO authenticated, anon
USING (
  bucket_id = 'palette-images' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

CREATE POLICY "Users (auth+anon) can delete their own palette images"
ON storage.objects FOR DELETE
TO authenticated, anon
USING (
  bucket_id = 'palette-images' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

-- Note: These policies use auth.uid() which is unaffected by the auth function migration
-- Development environment typically uses buckets without -prod suffix

-- Verify policies are working correctly with this query:
-- SELECT schemaname, tablename, policyname, definition
-- FROM pg_policies
-- WHERE tablename = 'objects' AND schemaname = 'storage';
