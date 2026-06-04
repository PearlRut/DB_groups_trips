-- =====================================================
-- Phase D - Main Program 1
-- File: Main_1_TripOccupancy.sql
-- Purpose: Run Function 1 and Procedure 1
-- =====================================================


-- 1. Function call:
-- Show occupancy summary for trip 1

SELECT *
FROM public.get_trip_occupancy_summary(1);


-- 2. Procedure call:
-- Update all trip statuses according to occupancy

CALL public.update_trip_status_by_occupancy();


-- 3. Show updated trips after the procedure

SELECT 
    t.trip_id,
    t.trip_name,
    t.group_size,
    COUNT(tp.participant_id) AS registered_participants,
    t.status
FROM public.trips t
LEFT JOIN public.trip_participants tp
    ON t.trip_id = tp.trip_id
GROUP BY 
    t.trip_id,
    t.trip_name,
    t.group_size,
    t.status
ORDER BY t.trip_id
LIMIT 10;


-- 4. Show status changes written by the trigger

SELECT *
FROM public.trip_status_log
ORDER BY changed_at DESC
LIMIT 10;