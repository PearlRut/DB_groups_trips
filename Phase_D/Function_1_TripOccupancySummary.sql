-- =====================================================
-- Phase D - Function 1
-- File: Function_1_TripOccupancySummary.sql
-- Purpose: Return occupancy summary for a specific trip
-- =====================================================

CREATE OR REPLACE FUNCTION public.get_trip_occupancy_summary(p_trip_id INT)
RETURNS TABLE (
    trip_id INT,
    trip_name VARCHAR,
    trip_type VARCHAR,
    group_size INT,
    registered_participants BIGINT,
    available_places BIGINT,
    occupancy_percentage NUMERIC,
    current_status VARCHAR,
    recommended_status VARCHAR,
    warning_message TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    trip_rec RECORD;
    participants_count BIGINT;
    calculated_available_places BIGINT;
    calculated_occupancy NUMERIC;
    calculated_status VARCHAR;
    calculated_warning TEXT;
BEGIN
    -- Get the trip row into a RECORD variable
    SELECT *
    INTO trip_rec
    FROM public.trips t
    WHERE t.trip_id = p_trip_id;

    -- If the trip does not exist, throw an exception
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Trip with id % does not exist', p_trip_id;
    END IF;

    -- Validate group size
    IF trip_rec.group_size IS NULL OR trip_rec.group_size <= 0 THEN
        RAISE EXCEPTION 'Trip % has invalid group_size: %', p_trip_id, trip_rec.group_size;
    END IF;

    -- Count how many participants are registered to this trip
    SELECT COUNT(*)
    INTO participants_count
    FROM public.trip_participants tp
    WHERE tp.trip_id = p_trip_id;

    calculated_available_places := trip_rec.group_size - participants_count;
    calculated_occupancy := ROUND((participants_count::NUMERIC / trip_rec.group_size) * 100, 2);

    -- Decide recommended status according to occupancy
    IF participants_count > trip_rec.group_size THEN
        calculated_status := 'OVERBOOKED';
        calculated_warning := 'There are more registered participants than the allowed group size';
    ELSIF participants_count = trip_rec.group_size THEN
        calculated_status := 'FULL';
        calculated_warning := 'The trip is exactly full';
    ELSE
        calculated_status := 'AVAILABLE';
        calculated_warning := 'There are still available places';
    END IF;

    RETURN QUERY
    SELECT
        trip_rec.trip_id,
        trip_rec.trip_name,
        trip_rec.trip_type,
        trip_rec.group_size,
        participants_count,
        calculated_available_places,
        calculated_occupancy,
        trip_rec.status,
        calculated_status,
        calculated_warning;

EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error in get_trip_occupancy_summary for trip %: %', p_trip_id, SQLERRM;
END;
$$;