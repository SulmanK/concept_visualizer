-- Migration: Add task_id and status fields to concepts table
-- This migration adds fields to track background task status

-- Add task_id column to concepts table
ALTER TABLE concepts ADD COLUMN task_id UUID;

-- Add status column to concepts table
ALTER TABLE concepts ADD COLUMN status TEXT;

-- Create index for task_id for efficient lookups
CREATE INDEX concepts_task_id_idx ON concepts(task_id);

-- Comment the new columns
COMMENT ON COLUMN concepts.task_id IS 'UUID of the background task that created this concept';
COMMENT ON COLUMN concepts.status IS 'Status of the concept generation process (processing, completed, failed, etc.)';
