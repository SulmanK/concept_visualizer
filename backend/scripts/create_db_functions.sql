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