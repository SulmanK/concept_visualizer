-- Concepts table with user_id instead of session_id
CREATE TABLE concepts (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  task_id UUID,
  status TEXT,
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

-- Create indexes for performance
CREATE INDEX concepts_user_id_idx ON concepts(user_id);
CREATE INDEX color_variations_concept_id_idx ON color_variations(concept_id);
CREATE INDEX concepts_task_id_idx ON concepts(task_id);


