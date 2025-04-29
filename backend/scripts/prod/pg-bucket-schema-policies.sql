-- Concepts table with user_id instead of session_id
CREATE TABLE concepts_prod (
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
CREATE TABLE color_variations_prod (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  concept_id UUID REFERENCES concepts_prod(id) NOT NULL,
  palette_name TEXT NOT NULL,
  colors JSONB NOT NULL, -- Array of hex codes
  description TEXT,
  image_path TEXT NOT NULL, -- Path to image in Supabase Storage
  image_url TEXT
);

-- Tasks table
CREATE TABLE tasks_prod (
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
CREATE INDEX concepts_prod_user_id_idx ON concepts_prod(user_id);
CREATE INDEX color_variations_prod_concept_id_idx ON color_variations_prod(concept_id);
CREATE INDEX tasks_prod_user_id_idx ON tasks_prod(user_id);
CREATE INDEX tasks_prod_status_idx ON tasks_prod(status);
CREATE INDEX tasks_prod_type_idx ON tasks_prod(type);
CREATE INDEX tasks_prod_result_id_idx ON tasks_prod(result_id);


-- Enable RLS on tables
ALTER TABLE concepts_prod ENABLE ROW LEVEL SECURITY;
ALTER TABLE color_variations_prod ENABLE ROW LEVEL SECURITY;
ALTER TABLE tasks_prod ENABLE ROW LEVEL SECURITY;

-- Concepts table policies (Adjusted for authenticated AND anon)
-- Drop existing policies first if necessary, e.g.:
-- DROP POLICY "Users can view their own concepts" ON concepts_prod;
-- ... repeat for all policies you are replacing ...

CREATE POLICY "Users (auth+anon) can view their own concepts"
ON concepts_prod FOR SELECT
TO authenticated, anon  -- Apply to both roles
USING (user_id = auth.uid());

CREATE POLICY "Users (auth+anon) can create their own concepts"
ON concepts_prod FOR INSERT
TO authenticated, anon  -- Apply to both roles
WITH CHECK (user_id = auth.uid());

CREATE POLICY "Users (auth+anon) can update their own concepts"
ON concepts_prod FOR UPDATE
TO authenticated, anon  -- Apply to both roles
USING (user_id = auth.uid());

CREATE POLICY "Users (auth+anon) can delete their own concepts"
ON concepts_prod FOR DELETE
TO authenticated, anon  -- Apply to both roles
USING (user_id = auth.uid());

-- Color variations policies (Adjusted for authenticated AND anon)
CREATE POLICY "Users (auth+anon) can view their own color variations"
ON color_variations_prod FOR SELECT
TO authenticated, anon  -- Apply to both roles
USING (
  concept_id IN (
    SELECT id FROM concepts_prod WHERE user_id = auth.uid()
  )
);

CREATE POLICY "Users (auth+anon) can create their own color variations"
ON color_variations_prod FOR INSERT
TO authenticated, anon  -- Apply to both roles
WITH CHECK (
  concept_id IN (
    SELECT id FROM concepts_prod WHERE user_id = auth.uid()
  )
);

CREATE POLICY "Users (auth+anon) can update their own color variations"
ON color_variations_prod FOR UPDATE
TO authenticated, anon  -- Apply to both roles
USING (
  concept_id IN (
    SELECT id FROM concepts_prod WHERE user_id = auth.uid()
  )
);

CREATE POLICY "Users (auth+anon) can delete their own color variations"
ON color_variations_prod FOR DELETE
TO authenticated, anon  -- Apply to both roles
USING (
  concept_id IN (
    SELECT id FROM concepts_prod WHERE user_id = auth.uid()
  )
);


-- Tasks table policies (for both authenticated and anon users)
CREATE POLICY "Users (auth+anon) can view their own tasks"
ON tasks_prod FOR SELECT
TO authenticated, anon
USING (user_id = auth.uid());

CREATE POLICY "Users (auth+anon) can create their own tasks"
ON tasks_prod FOR INSERT
TO authenticated, anon
WITH CHECK (user_id = auth.uid());

CREATE POLICY "Users (auth+anon) can update their own tasks"
ON tasks_prod FOR UPDATE
TO authenticated, anon
USING (user_id = auth.uid());

CREATE POLICY "Users (auth+anon) can delete their own tasks"
ON tasks_prod FOR DELETE
TO authenticated, anon
USING (user_id = auth.uid());



-- Concept images bucket policies (Adjusted for authenticated AND anon)
CREATE POLICY "Users (auth+anon) can view their own concept images"
ON storage.objects FOR SELECT
TO authenticated, anon  -- Apply to both roles
USING (
  bucket_id = 'concept-images-prod' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

CREATE POLICY "Users (auth+anon) can upload their own concept images"
ON storage.objects FOR INSERT
TO authenticated, anon  -- Apply to both roles
WITH CHECK (
  bucket_id = 'concept-images-prod' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

CREATE POLICY "Users (auth+anon) can update their own concept images"
ON storage.objects FOR UPDATE
TO authenticated, anon  -- Apply to both roles
USING (
  bucket_id = 'concept-images-prod' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

CREATE POLICY "Users (auth+anon) can delete their own concept images"
ON storage.objects FOR DELETE
TO authenticated, anon  -- Apply to both roles
USING (
  bucket_id = 'concept-images-prod' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

-- Color variation images bucket policies (Adjusted for authenticated AND anon)
CREATE POLICY "Users (auth+anon) can view their own palette images"
ON storage.objects FOR SELECT
TO authenticated, anon  -- Apply to both roles
USING (
  bucket_id = 'palette-images-prod' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

CREATE POLICY "Users (auth+anon) can upload their own palette images"
ON storage.objects FOR INSERT
TO authenticated, anon  -- Apply to both roles
WITH CHECK (
  bucket_id = 'palette-images-prod' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

CREATE POLICY "Users (auth+anon) can update their own palette images"
ON storage.objects FOR UPDATE
TO authenticated, anon  -- Apply to both roles
USING (
  bucket_id = 'palette-images-prod' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

CREATE POLICY "Users (auth+anon) can delete their own palette images"
ON storage.objects FOR DELETE
TO authenticated, anon  -- Apply to both roles
USING (
  bucket_id = 'palette-images-prod' AND
  (storage.foldername(name))[1] = auth.uid()::text
);
