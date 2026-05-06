-- =====================================================
-- Phase B - Index.sql
-- System: Group Trips Management
-- =====================================================


-- =====================================================
-- INDEX 1
-- Speed up searches by trip_id in trip_participants
-- =====================================================

-- Before index:
EXPLAIN ANALYZE
SELECT *
FROM trip_participants
WHERE trip_id = 1;

-- Create index:
CREATE INDEX idx_trip_participants_trip_id
ON trip_participants(trip_id);

-- After index:
EXPLAIN ANALYZE
SELECT *
FROM trip_participants
WHERE trip_id = 1;



-- =====================================================
-- INDEX 2
-- Speed up searches by event_date in events
-- =====================================================

-- Before index:
EXPLAIN ANALYZE
SELECT *
FROM events
WHERE event_date >= CURRENT_DATE;

-- Create index:
CREATE INDEX idx_events_event_date
ON events(event_date);

-- After index:
EXPLAIN ANALYZE
SELECT *
FROM events
WHERE event_date >= CURRENT_DATE;



-- =====================================================
-- INDEX 3
-- Speed up searches by difficulty_level in routes
-- =====================================================

-- Before index:
EXPLAIN ANALYZE
SELECT *
FROM routes
WHERE difficulty_level = 'Hard';

-- Create index:
CREATE INDEX idx_routes_difficulty_level
ON routes(difficulty_level);

-- After index:
EXPLAIN ANALYZE
SELECT *
FROM routes
WHERE difficulty_level = 'Hard';