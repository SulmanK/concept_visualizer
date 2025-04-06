-- For the concept-images bucket
CREATE POLICY "Users can select their own images" 
ON storage.objects FOR SELECT 
USING (bucket_id = 'concept-images' AND ((auth.jwt() ->> 'session_id')::text = (storage.foldername(name))[1]));

CREATE POLICY "Users can insert their own images" 
ON storage.objects FOR INSERT 
WITH CHECK (bucket_id = 'concept-images' AND 
           ((auth.jwt() ->> 'session_id')::text = (storage.foldername(name))[1]));

CREATE POLICY "Users can update their own images" 
ON storage.objects FOR UPDATE 
USING (bucket_id = 'concept-images' AND 
      ((auth.jwt() ->> 'session_id')::text = (storage.foldername(name))[1]));

CREATE POLICY "Users can delete their own images" 
ON storage.objects FOR DELETE 
USING (bucket_id = 'concept-images' AND 
      ((auth.jwt() ->> 'session_id')::text = (storage.foldername(name))[1]));

-- Similar policies for palette-images bucket
CREATE POLICY "Users can select their own palette images" 
ON storage.objects FOR SELECT 
USING (bucket_id = 'palette-images' AND ((auth.jwt() ->> 'session_id')::text = (storage.foldername(name))[1]));

CREATE POLICY "Users can insert their own palette images" 
ON storage.objects FOR INSERT 
WITH CHECK (bucket_id = 'palette-images' AND 
           ((auth.jwt() ->> 'session_id')::text = (storage.foldername(name))[1]));

CREATE POLICY "Users can update their own palette images" 
ON storage.objects FOR UPDATE 
USING (bucket_id = 'palette-images' AND 
      ((auth.jwt() ->> 'session_id')::text = (storage.foldername(name))[1]));

CREATE POLICY "Users can delete their own palette images" 
ON storage.objects FOR DELETE 
USING (bucket_id = 'palette-images' AND 
      ((auth.jwt() ->> 'session_id')::text = (storage.foldername(name))[1]));