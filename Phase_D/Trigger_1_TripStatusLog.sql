-- =====================================================
-- Phase D - Trigger 1
-- File: Trigger_1_TripStatusLog.sql
-- Purpose: Log every update of trips.status
-- =====================================================


-- Trigger function:
-- This function inserts a row into trip_status_log
-- whenever the status of a trip changes.

/*
contain:
Trigger
UPDATE trigger
OLD
NEW
INSERT
IF
EXCEPTION
RAISE NOTICE
*/

CREATE OR REPLACE FUNCTION public.log_trip_status_update()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    -- Insert to log only if the status really changed
    IF OLD.status IS DISTINCT FROM NEW.status THEN
        INSERT INTO public.trip_status_log (
            trip_id,
            old_status,
            new_status,
            changed_at,
            changed_by
        )
        VALUES (
            NEW.trip_id,
            OLD.status,
            NEW.status,
            CURRENT_TIMESTAMP,
            CURRENT_USER
        );

        RAISE NOTICE 'Trip % status changed from % to %',
            NEW.trip_id,
            OLD.status,
            NEW.status;
    END IF;

    RETURN NEW;

EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error in log_trip_status_update trigger: %', SQLERRM;
END;
$$;


-- Drop old trigger if it already exists, so the file can be run again safely

DROP TRIGGER IF EXISTS trg_log_trip_status_update ON public.trips;


-- Create trigger:
-- Runs automatically after UPDATE of status on trips

CREATE TRIGGER trg_log_trip_status_update
AFTER UPDATE OF status ON public.trips
FOR EACH ROW
EXECUTE FUNCTION public.log_trip_status_update();