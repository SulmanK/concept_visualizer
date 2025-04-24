-- Enable RLS on sessions table
ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;

-- Create policy for sessions table
CREATE POLICY "Users can only access their own sessions"
ON sessions
USING (id = (auth.jwt() -> 'app_metadata' ->> 'session_id')::uuid);

-- Enable RLS on concepts table
ALTER TABLE concepts ENABLE ROW LEVEL SECURITY;

-- Create policy for concepts table
CREATE POLICY "Users can only access their own concepts"
ON concepts
USING (session_id = (auth.jwt() -> 'app_metadata' ->> 'session_id')::uuid);

-- Enable RLS on color_variations table
ALTER TABLE color_variations ENABLE ROW LEVEL SECURITY;

-- Create policy for color_variations table
CREATE POLICY "Users can only access their own color variations"
ON color_variations
USING (concept_id IN (
  SELECT id FROM concepts
  WHERE session_id = (auth.jwt() -> 'app_metadata' ->> 'session_id')::uuid
));
```
