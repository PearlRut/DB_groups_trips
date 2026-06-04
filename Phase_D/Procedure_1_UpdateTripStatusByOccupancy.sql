-- =====================================================
-- Phase D - Procedure 1
-- File: Procedure_1_UpdateTripStatusByOccupancy.sql
-- Purpose: Update trips.status according to occupancy
-- =====================================================

/*
contain:
Procedure
Cursor implicit
FOR LOOP
IF / ELSIF / ELSE
UPDATE
RAISE NOTICE
EXCEPTION
RECORD
*/

CREATE OR REPLACE PROCEDURE public.update_trip_status_by_occupancy()
LANGUAGE plpgsql
AS $$
DECLARE
    trip_rec RECORD;
    participants_count BIGINT;
    new_status VARCHAR(50);
BEGIN
    /*
        This implicit cursor goes over all trips.
        For each trip, the procedure counts registered participants
        and updates the trip status according to the occupancy.
    */

    FOR trip_rec IN
        SELECT
            t.trip_id,
            t.trip_name,
            t.group_size,
            t.status
        FROM public.trips t
        ORDER BY t.trip_id
    LOOP
        -- Count registered participants for the current trip
        SELECT COUNT(*)
        INTO participants_count
        FROM public.trip_participants tp
        WHERE tp.trip_id = trip_rec.trip_id;

        -- Decide the new status
        IF trip_rec.group_size IS NULL OR trip_rec.group_size <= 0 THEN
            RAISE NOTICE 'Trip % has invalid group_size: %',
                trip_rec.trip_id, trip_rec.group_size;
            CONTINUE;

        ELSIF participants_count > trip_rec.group_size THEN
            new_status := 'OVERBOOKED';

        ELSIF participants_count = trip_rec.group_size THEN
            new_status := 'FULL';

        ELSE
            new_status := 'AVAILABLE';
        END IF;

        -- Update only if the status actually changed
        IF trip_rec.status IS DISTINCT FROM new_status THEN
            UPDATE public.trips
            SET status = new_status
            WHERE trip_id = trip_rec.trip_id;

            RAISE NOTICE 'Trip % (%) status changed from % to %. Participants: %, Group size: %',
                trip_rec.trip_id,
                trip_rec.trip_name,
                trip_rec.status,
                new_status,
                participants_count,
                trip_rec.group_size;
        ELSE
            RAISE NOTICE 'Trip % (%) already has status %. Participants: %, Group size: %',
                trip_rec.trip_id,
                trip_rec.trip_name,
                trip_rec.status,
                participants_count,
                trip_rec.group_size;
        END IF;
    END LOOP;

EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error in update_trip_status_by_occupancy: %', SQLERRM;
END;
$$;