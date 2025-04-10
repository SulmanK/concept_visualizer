-- Function to get concepts older than specified days
CREATE OR REPLACE FUNCTION get_old_concepts(days_threshold INT)
RETURNS TABLE (id UUID, image_path TEXT) AS $$
BEGIN
    RETURN QUERY
    SELECT c.id, c.image_path
    FROM concepts c
    WHERE c.created_at < NOW() - (days_threshold * INTERVAL '1 day');
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get color variations for specific concepts
CREATE OR REPLACE FUNCTION get_variations_for_concepts(concept_ids UUID[])
RETURNS TABLE (id UUID, image_path TEXT) AS $$
BEGIN
    RETURN QUERY
    SELECT cv.id, cv.image_path
    FROM color_variations cv
    WHERE cv.concept_id = ANY(concept_ids);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to delete color variations for specific concepts
CREATE OR REPLACE FUNCTION delete_variations_for_concepts(concept_ids UUID[])
RETURNS VOID AS $$
BEGIN
    DELETE FROM color_variations
    WHERE concept_id = ANY(concept_ids);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to delete specified concepts
CREATE OR REPLACE FUNCTION delete_concepts(concept_ids UUID[])
RETURNS VOID AS $$
BEGIN
    DELETE FROM concepts
    WHERE id = ANY(concept_ids);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get stuck tasks older than specified minutes
CREATE OR REPLACE FUNCTION get_stuck_tasks(minutes_threshold INT)
RETURNS TABLE (id UUID, status TEXT, type TEXT, updated_at TIMESTAMPTZ) AS $$
BEGIN
    RETURN QUERY
    SELECT t.id, t.status, t.type, t.updated_at
    FROM tasks t
    WHERE t.status IN ('pending', 'processing')
    AND t.updated_at < NOW() - (minutes_threshold * INTERVAL '1 minute');
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to mark tasks as failed
CREATE OR REPLACE FUNCTION mark_tasks_as_failed(task_ids UUID[], error_message TEXT)
RETURNS VOID AS $$
BEGIN
    UPDATE tasks
    SET status = 'failed',
        error_message = $2,
        updated_at = NOW()
    WHERE id = ANY(task_ids);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get active tasks for a user
CREATE OR REPLACE FUNCTION get_active_tasks_for_user(user_id_param UUID)
RETURNS TABLE (id UUID, type TEXT, status TEXT, created_at TIMESTAMPTZ, updated_at TIMESTAMPTZ) AS $$
BEGIN
    RETURN QUERY
    SELECT t.id, t.type, t.status, t.created_at, t.updated_at
    FROM tasks t
    WHERE t.user_id = user_id_param
    AND t.status IN ('pending', 'processing')
    ORDER BY t.created_at DESC;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER; 