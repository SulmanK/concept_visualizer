# Supabase Setup Guide for Concept Visualizer

This guide provides step-by-step instructions for setting up Supabase as the database and session management solution for the Concept Visualizer application.

## Overview

Supabase will serve as our PostgreSQL database with:

- Anonymous session tracking via cookies
- Storage of user-generated concepts and their metadata
- Storage of color palette variations
- Image storage using Supabase Storage
- RESTful API access to stored data

## Step 1: Create a Supabase Account and Project

1. Visit [supabase.com](https://supabase.com/) and sign up for an account

   - You can use GitHub, GitLab, or email for authentication
   - If using GitHub, authorize the Supabase application when prompted

2. Once logged in, click "New Project" in the dashboard

3. Enter project details:

   - **Organization:** Select or create an organization
   - **Name:** `concept-visualizer` (or your preferred name)
   - **Database Password:** Create a secure password (save this somewhere safe!)
   - **Region:** Choose a region closest to your users (lower latency)
   - **Pricing Plan:** Free tier is sufficient for development
     - Includes 500MB database, 1GB file storage, 2GB bandwidth
     - 50,000 monthly active users
     - 7-day log retention

4. Click "Create new project" and wait for initialization (approximately 2-3 minutes)

5. Note your project's URL in the dashboard (format: `https://[project-id].supabase.co`)

## Step 2: Create Storage Buckets

First, let's create the storage buckets for our images:

1. In the Supabase dashboard, navigate to the "Storage" section in the left sidebar

2. Click "Create a new bucket"

3. Create the following buckets:

   - **Name:** `concept-images` (for base images)

     - **Public/Private:** Private (we'll set up access policies later)
     - **File size limit:** 5MB (adequate for most generated images)
     - Click "Create bucket"

   - **Name:** `palette-images` (for color palette variations)
     - **Public/Private:** Private
     - **File size limit:** 5MB
     - Click "Create bucket"

4. For now, set up only basic read access:

   - Click on the bucket name
   - Go to the "Policies" tab
   - Click "Create a new policy"

   For anonymous read access:

   - Policy name: `Anonymous read access`
   - Policy definition: `true` (allows anyone to read images)
   - Operations: SELECT
   - Click "Save policy"

   > **Note:** We'll set up the write policies after creating the database schema.

## Step 3: Set Up Database Schema

```sql
-- Concepts table with user_id instead of session_id
CREATE TABLE concepts (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  logo_description TEXT NOT NULL,
  theme_description TEXT NOT NULL,
  image_path TEXT NOT NULL, -- Path to image in Supabase Storage
  image_url TEXT, -- Can be Null
  is_anonymous BOOLEAN DEFAULT TRUE -- Flag to identify concepts from anonymous users
);

-- Color variations table
CREATE TABLE color_variations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  concept_id UUID REFERENCES concepts(id) NOT NULL,
  palette_name TEXT NOT NULL,
  colors JSONB NOT NULL, -- Array of hex codes
  description TEXT,
  image_path TEXT NOT NULL, -- Path to image in Supabase Storage
  image_url TEXT
);

-- Tasks table
CREATE TABLE tasks (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  type TEXT NOT NULL, -- e.g., 'concept_generation', 'concept_refinement'
  status TEXT NOT NULL, -- 'pending', 'processing', 'completed', 'failed'
  result_id UUID, -- Reference to the result (e.g., concept_id)
  error_message TEXT, -- Error message if task failed
  metadata JSONB DEFAULT '{}'::jsonb -- Additional task-specific metadata
);


-- Create indexes for performance
CREATE INDEX concepts_user_id_idx ON concepts(user_id);
CREATE INDEX color_variations_concept_id_idx ON color_variations(concept_id);
CREATE INDEX tasks_user_id_idx ON tasks(user_id);
CREATE INDEX tasks_status_idx ON tasks(status);
CREATE INDEX tasks_type_idx ON tasks(type);
CREATE INDEX tasks_result_id_idx ON tasks(result_id);


-- Enable RLS on tables
ALTER TABLE concepts ENABLE ROW LEVEL SECURITY;
ALTER TABLE color_variations ENABLE ROW LEVEL SECURITY;
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;

-- Concepts table policies (Adjusted for authenticated AND anon)
-- Drop existing policies first if necessary, e.g.:
-- DROP POLICY "Users can view their own concepts" ON concepts;
-- ... repeat for all policies you are replacing ...

CREATE POLICY "Users (auth+anon) can view their own concepts"
ON concepts FOR SELECT
TO authenticated, anon  -- Apply to both roles
USING (user_id = auth.uid());

CREATE POLICY "Users (auth+anon) can create their own concepts"
ON concepts FOR INSERT
TO authenticated, anon  -- Apply to both roles
WITH CHECK (user_id = auth.uid());

CREATE POLICY "Users (auth+anon) can update their own concepts"
ON concepts FOR UPDATE
TO authenticated, anon  -- Apply to both roles
USING (user_id = auth.uid());

CREATE POLICY "Users (auth+anon) can delete their own concepts"
ON concepts FOR DELETE
TO authenticated, anon  -- Apply to both roles
USING (user_id = auth.uid());

-- Color variations policies (Adjusted for authenticated AND anon)
CREATE POLICY "Users (auth+anon) can view their own color variations"
ON color_variations FOR SELECT
TO authenticated, anon  -- Apply to both roles
USING (
  concept_id IN (
    SELECT id FROM concepts WHERE user_id = auth.uid()
  )
);

CREATE POLICY "Users (auth+anon) can create their own color variations"
ON color_variations FOR INSERT
TO authenticated, anon  -- Apply to both roles
WITH CHECK (
  concept_id IN (
    SELECT id FROM concepts WHERE user_id = auth.uid()
  )
);

CREATE POLICY "Users (auth+anon) can update their own color variations"
ON color_variations FOR UPDATE
TO authenticated, anon  -- Apply to both roles
USING (
  concept_id IN (
    SELECT id FROM concepts WHERE user_id = auth.uid()
  )
);

CREATE POLICY "Users (auth+anon) can delete their own color variations"
ON color_variations FOR DELETE
TO authenticated, anon  -- Apply to both roles
USING (
  concept_id IN (
    SELECT id FROM concepts WHERE user_id = auth.uid()
  )
);


-- Tasks table policies (for both authenticated and anon users)
CREATE POLICY "Users (auth+anon) can view their own tasks"
ON tasks FOR SELECT
TO authenticated, anon
USING (user_id = auth.uid());

CREATE POLICY "Users (auth+anon) can create their own tasks"
ON tasks FOR INSERT
TO authenticated, anon
WITH CHECK (user_id = auth.uid());

CREATE POLICY "Users (auth+anon) can update their own tasks"
ON tasks FOR UPDATE
TO authenticated, anon
USING (user_id = auth.uid());

CREATE POLICY "Users (auth+anon) can delete their own tasks"
ON tasks FOR DELETE
TO authenticated, anon
USING (user_id = auth.uid());



-- Concept images bucket policies (Adjusted for authenticated AND anon)
CREATE POLICY "Users (auth+anon) can view their own concept images"
ON storage.objects FOR SELECT
TO authenticated, anon  -- Apply to both roles
USING (
  bucket_id = 'concept-images' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

CREATE POLICY "Users (auth+anon) can upload their own concept images"
ON storage.objects FOR INSERT
TO authenticated, anon  -- Apply to both roles
WITH CHECK (
  bucket_id = 'concept-images' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

CREATE POLICY "Users (auth+anon) can update their own concept images"
ON storage.objects FOR UPDATE
TO authenticated, anon  -- Apply to both roles
USING (
  bucket_id = 'concept-images' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

CREATE POLICY "Users (auth+anon) can delete their own concept images"
ON storage.objects FOR DELETE
TO authenticated, anon  -- Apply to both roles
USING (
  bucket_id = 'concept-images' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

-- Color variation images bucket policies (Adjusted for authenticated AND anon)
CREATE POLICY "Users (auth+anon) can view their own palette images"
ON storage.objects FOR SELECT
TO authenticated, anon  -- Apply to both roles
USING (
  bucket_id = 'palette-images' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

CREATE POLICY "Users (auth+anon) can upload their own palette images"
ON storage.objects FOR INSERT
TO authenticated, anon  -- Apply to both roles
WITH CHECK (
  bucket_id = 'palette-images' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

CREATE POLICY "Users (auth+anon) can update their own palette images"
ON storage.objects FOR UPDATE
TO authenticated, anon  -- Apply to both roles
USING (
  bucket_id = 'palette-images' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

CREATE POLICY "Users (auth+anon) can delete their own palette images"
ON storage.objects FOR DELETE
TO authenticated, anon  -- Apply to both roles
USING (
  bucket_id = 'palette-images' AND
  (storage.foldername(name))[1] = auth.uid()::text
);
```

## Step 4: Get API Keys

To connect your application to Supabase:

1. Go to "Project Settings" → "API" in the sidebar

2. Note down two important values:

   - **Project URL:** Your Supabase project URL (e.g., `https://[project-id].supabase.co`)
   - **anon key:** The public API key for anonymous access

3. These values will be used in your application's environment variables

4. Important: Never expose the `service_role` key in client-side code; it bypasses RLS policies

## Step 5: Authentication Settings

1. Go to Authenication and under Sign In / Sign Up enable "Allow anonymouse sign-ins"
2. Go to URL Configuration and set our localhost

## Step 6: Realtime

Enable realtime in each of the database tables

## Step 6: Edge Function

## Deployment Steps

1. Create the SQL functions in Supabase
2. Create the edge function file:
   - `backend/supabase/functions/cleanup-old-data/index.ts`
3. Deploy the edge function:
   ```bash
   cd backend
   supabase functions deploy cleanup-old-data --project-ref <proj_id> --no-verify-jwt
   ```
4. Set up environment variables:
   ```bash
   supabase secrets set MY_SUPABASE_URL=<your-supabase-url>
   supabase secrets set MY_SERVICE_ROLE_KEY=<your-service-role-key>
   supabase secrets set STORAGE_BUCKET_CONCEPT=<your-concept-bucket>
   supabase secrets set STORAGE_BUCKET_PALETTE=<your-palette-bucket>
   ```
5. Schedule the function to run daily:
   GitHub Actions

   To ensure secure access to your Supabase Edge Function, you need to add your Supabase anon key as a GitHub secret:

   1. Go to your GitHub repository
   2. Click on "Settings" tab
   3. In the left sidebar, click on "Secrets and variables" > "Actions"
   4. Click on "New repository secret"
   5. Enter the following information:

   - Name: `SUPABASE_ANON_KEY`
   - Value: ``

   6. Click "Add secret"

## Step 7: Captcha
