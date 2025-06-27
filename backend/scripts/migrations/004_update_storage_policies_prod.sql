-- Migration: Ensure storage policies are compatible with auth function migration
-- Date: 2024-01-XX
-- Reason: Verify storage policies don't use deprecated auth.get_jwt functions and are properly configured

-- This file ensures your storage policies continue working after the auth function migration
-- Your current policies already use auth.uid() which is not affected, but this migration
-- provides consistency and future-proofs the setup

-- Drop existing storage policies to ensure clean state
DROP POLICY IF EXISTS "Users (auth+anon) can view their own concept images" ON storage.objects;
DROP POLICY IF EXISTS "Users (auth+anon) can upload their own concept images" ON storage.objects;
DROP POLICY IF EXISTS "Users (auth+anon) can update their own concept images" ON storage.objects;
DROP POLICY IF EXISTS "Users (auth+anon) can delete their own concept images" ON storage.objects;

DROP POLICY IF EXISTS "Users (auth+anon) can view their own palette images" ON storage.objects;
DROP POLICY IF EXISTS "Users (auth+anon) can upload their own palette images" ON storage.objects;
DROP POLICY IF EXISTS "Users (auth+anon) can update their own palette images" ON storage.objects;
DROP POLICY IF EXISTS "Users (auth+anon) can delete their own palette images" ON storage.objects;

-- Recreate concept images bucket policies (Production buckets)
-- These policies use auth.uid() which is not affected by the auth function migration
CREATE POLICY "Users (auth+anon) can view their own concept images"
ON storage.objects FOR SELECT
TO authenticated, anon
USING (
  bucket_id = 'concept-images-prod' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

CREATE POLICY "Users (auth+anon) can upload their own concept images"
ON storage.objects FOR INSERT
TO authenticated, anon
WITH CHECK (
  bucket_id = 'concept-images-prod' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

CREATE POLICY "Users (auth+anon) can update their own concept images"
ON storage.objects FOR UPDATE
TO authenticated, anon
USING (
  bucket_id = 'concept-images-prod' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

CREATE POLICY "Users (auth+anon) can delete their own concept images"
ON storage.objects FOR DELETE
TO authenticated, anon
USING (
  bucket_id = 'concept-images-prod' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

-- Recreate palette images bucket policies (Production buckets)
CREATE POLICY "Users (auth+anon) can view their own palette images"
ON storage.objects FOR SELECT
TO authenticated, anon
USING (
  bucket_id = 'palette-images-prod' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

CREATE POLICY "Users (auth+anon) can upload their own palette images"
ON storage.objects FOR INSERT
TO authenticated, anon
WITH CHECK (
  bucket_id = 'palette-images-prod' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

CREATE POLICY "Users (auth+anon) can update their own palette images"
ON storage.objects FOR UPDATE
TO authenticated, anon
USING (
  bucket_id = 'palette-images-prod' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

CREATE POLICY "Users (auth+anon) can delete their own palette images"
ON storage.objects FOR DELETE
TO authenticated, anon
USING (
  bucket_id = 'palette-images-prod' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

-- Note: Your storage policies are already correctly using auth.uid() which is unaffected
-- by the Supabase auth function migration. This script ensures consistency.

-- If you had any policies using the deprecated auth.get_jwt_from_url() or auth.get_jwt()
-- functions, they would need to be updated to use public.get_jwt_from_url() and public.get_jwt()

-- Verify policies are working correctly with this query:
-- SELECT schemaname, tablename, policyname, definition
-- FROM pg_policies
-- WHERE tablename = 'objects' AND schemaname = 'storage';
