-- =====================================================
-- Phase B - RollbackCommit.sql
-- System: Group Trips Management
-- =====================================================


-- =====================================================
-- ROLLBACK EXAMPLE
-- =====================================================

BEGIN;

-- Before update
SELECT
    trip_id,
    trip_name,
    status
FROM trips
WHERE trip_id = 1;

-- Update
UPDATE trips
SET status = 'cancelled'
WHERE trip_id = 1;

-- After update
SELECT
    trip_id,
    trip_name,
    status
FROM trips
WHERE trip_id = 1;

-- Rollback
ROLLBACK;

-- After rollback
SELECT
    trip_id,
    trip_name,
    status
FROM trips
WHERE trip_id = 1;



-- =====================================================
-- COMMIT EXAMPLE
-- =====================================================

BEGIN;

-- Before update
SELECT
    route_id,
    route_name,
    difficulty_level
FROM routes
WHERE route_id = 1;

-- Update
UPDATE routes
SET difficulty_level = 'Medium'
WHERE route_id = 1;

-- After update
SELECT
    route_id,
    route_name,
    difficulty_level
FROM routes
WHERE route_id = 1;

-- Commit
COMMIT;

-- After commit
SELECT
    route_id,
    route_name,
    difficulty_level
FROM routes
WHERE route_id = 1;