-- Migration: Move custom auth functions from auth schema to public schema
-- Date: 2024-01-XX
-- Reason: Supabase deprecating custom objects in internal schemas

-- Drop existing functions from auth schema (if they exist)
DROP FUNCTION IF EXISTS auth.get_jwt_from_url();
DROP FUNCTION IF EXISTS auth.get_jwt();

-- Create functions in public schema
CREATE OR REPLACE FUNCTION public.get_jwt_from_url()
RETURNS text
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  _token text;
BEGIN
  -- Extract the token from query string
  _token := split_part(split_part(current_setting('request.url.query', true), 'token=', 2), '&', 1);

  -- Return the token if found, otherwise return NULL
  RETURN NULLIF(_token, '');
END;
$$;

-- Function to get JWT from header or URL
CREATE OR REPLACE FUNCTION public.get_jwt()
RETURNS text
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  _token text;
BEGIN
  -- Try to get token from Authorization header first
  _token := coalesce(
    current_setting('request.headers', true)::json->>'authorization',
    current_setting('request.headers', true)::json->>'Authorization'
  );

  -- Extract Bearer token if present
  IF _token IS NOT NULL AND _token LIKE 'Bearer %' THEN
    _token := replace(_token, 'Bearer ', '');
  ELSE
    -- Try to get token from URL query parameter
    _token := public.get_jwt_from_url();
  END IF;

  -- Return the token if found, otherwise return NULL
  RETURN _token;
END;
$$;

-- Update RLS policies to use new function location
-- Note: You'll need to update any existing RLS policies that reference auth.get_jwt_from_url() or auth.get_jwt()
-- to use public.get_jwt_from_url() and public.get_jwt() instead

-- Grant execute permissions
GRANT EXECUTE ON FUNCTION public.get_jwt_from_url() TO anon, authenticated;
GRANT EXECUTE ON FUNCTION public.get_jwt() TO anon, authenticated;

-- Add comment for documentation
COMMENT ON FUNCTION public.get_jwt_from_url() IS 'Extracts JWT token from URL query parameters for storage RLS policies';
COMMENT ON FUNCTION public.get_jwt() IS 'Gets JWT token from Authorization header or URL query parameter for storage RLS policies';
