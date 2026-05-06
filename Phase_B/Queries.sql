-- =====================================================
-- Phase B - Queries.sql
-- System: Group Trips Management
-- =====================================================


-- =====================================================
-- SELECT QUERY 1A
-- Description:
-- Show trip summary: route, region, transport type,
-- number of registered participants and available places.
-- Method: JOIN + GROUP BY
-- =====================================================
SELECT
    t.trip_id,
    t.trip_name,
    r.route_name,
    r.region,
    tt.transport_type_name,
    t.group_size,
    COUNT(tp.participant_id) AS registered_participants,
    t.group_size - COUNT(tp.participant_id) AS available_places,
    t.status
FROM trips t
JOIN routes r ON t.route_id = r.route_id
JOIN transport_types tt ON t.transport_type_id = tt.transport_type_id
LEFT JOIN trip_participants tp ON t.trip_id = tp.trip_id
GROUP BY
    t.trip_id,
    t.trip_name,
    r.route_name,
    r.region,
    tt.transport_type_name,
    t.group_size,
    t.status
ORDER BY registered_participants DESC, t.trip_name;


-- =====================================================
-- SELECT QUERY 1B
-- Description:
-- Same result as Query 1A, but using correlated subqueries.
-- Method: Subqueries
-- =====================================================
SELECT
    t.trip_id,
    t.trip_name,
    (
        SELECT r.route_name
        FROM routes r
        WHERE r.route_id = t.route_id
    ) AS route_name,
    (
        SELECT r.region
        FROM routes r
        WHERE r.route_id = t.route_id
    ) AS region,
    (
        SELECT tt.transport_type_name
        FROM transport_types tt
        WHERE tt.transport_type_id = t.transport_type_id
    ) AS transport_type_name,
    t.group_size,
    (
        SELECT COUNT(*)
        FROM trip_participants tp
        WHERE tp.trip_id = t.trip_id
    ) AS registered_participants,
    t.group_size - (
        SELECT COUNT(*)
        FROM trip_participants tp
        WHERE tp.trip_id = t.trip_id
    ) AS available_places,
    t.status
FROM trips t
ORDER BY registered_participants DESC, t.trip_name;


-- =====================================================
-- SELECT QUERY 2A
-- Description:
-- Calculate monthly event cost per trip, including date parts.
-- Method: JOIN + GROUP BY + EXTRACT
-- =====================================================
SELECT
    t.trip_id,
    t.trip_name,
    EXTRACT(YEAR FROM e.event_date) AS event_year,
    EXTRACT(MONTH FROM e.event_date) AS event_month,
    COUNT(e.event_id) AS number_of_events,
    SUM(e.cost) AS total_cost,
    ROUND(AVG(e.cost), 2) AS average_event_cost,
    MIN(e.cost) AS cheapest_event,
    MAX(e.cost) AS most_expensive_event
FROM trips t
JOIN events e ON t.trip_id = e.trip_id
GROUP BY
    t.trip_id,
    t.trip_name,
    EXTRACT(YEAR FROM e.event_date),
    EXTRACT(MONTH FROM e.event_date)
ORDER BY event_year, event_month, total_cost DESC;


-- =====================================================
-- SELECT QUERY 2B
-- Description:
-- Same business question as Query 2A, but using a subquery
-- that first summarizes event costs.
-- Method: Derived table subquery
-- =====================================================
SELECT
    monthly_costs.trip_id,
    t.trip_name,
    monthly_costs.event_year,
    monthly_costs.event_month,
    monthly_costs.number_of_events,
    monthly_costs.total_cost,
    monthly_costs.average_event_cost,
    monthly_costs.cheapest_event,
    monthly_costs.most_expensive_event
FROM trips t
JOIN (
    SELECT
        e.trip_id,
        EXTRACT(YEAR FROM e.event_date) AS event_year,
        EXTRACT(MONTH FROM e.event_date) AS event_month,
        COUNT(e.event_id) AS number_of_events,
        SUM(e.cost) AS total_cost,
        ROUND(AVG(e.cost), 2) AS average_event_cost,
        MIN(e.cost) AS cheapest_event,
        MAX(e.cost) AS most_expensive_event
    FROM events e
    GROUP BY
        e.trip_id,
        EXTRACT(YEAR FROM e.event_date),
        EXTRACT(MONTH FROM e.event_date)
) AS monthly_costs
ON t.trip_id = monthly_costs.trip_id
ORDER BY monthly_costs.event_year, monthly_costs.event_month, monthly_costs.total_cost DESC;


-- =====================================================
-- SELECT QUERY 3A
-- Description:
-- Show experienced guides who participate in hard/long trips.
-- Method: JOIN
-- =====================================================
SELECT
    g.participant_id,
    p.first_name,
    p.last_name,
    g.license_number,
    g.experience_years,
    t.trip_id,
    t.trip_name,
    r.route_name,
    r.region,
    r.distance_km,
    r.difficulty_level,
    t.start_date,
    t.end_date
FROM guides g
JOIN participants p ON g.participant_id = p.participant_id
JOIN trip_participants tp ON g.participant_id = tp.participant_id
JOIN trips t ON tp.trip_id = t.trip_id
JOIN routes r ON t.route_id = r.route_id
WHERE g.experience_years >= 3
  AND (
        LOWER(r.difficulty_level) = 'hard'
        OR r.distance_km >= 10
      )
ORDER BY g.experience_years DESC, r.distance_km DESC;


-- =====================================================
-- SELECT QUERY 3B
-- Description:
-- Same business question as Query 3A,
-- but using EXISTS instead of joining trip_participants directly.
-- Method: EXISTS
-- =====================================================
SELECT
    g.participant_id,
    p.first_name,
    p.last_name,
    g.license_number,
    g.experience_years
FROM guides g
JOIN participants p ON g.participant_id = p.participant_id
WHERE g.experience_years >= 3
  AND EXISTS (
      SELECT 1
      FROM trip_participants tp
      JOIN trips t ON tp.trip_id = t.trip_id
      JOIN routes r ON t.route_id = r.route_id
      WHERE tp.participant_id = g.participant_id
        AND (
            LOWER(r.difficulty_level) = 'hard'
            OR r.distance_km >= 10
        )
  )
ORDER BY g.experience_years DESC;


-- =====================================================
-- SELECT QUERY 4A
-- Description:
-- Show daily trip schedule with related events and actions.
-- Method: LEFT JOIN
-- =====================================================
SELECT
    t.trip_id,
    t.trip_name,
    s.sch_date,
    EXTRACT(DAY FROM s.sch_date) AS schedule_day,
    EXTRACT(MONTH FROM s.sch_date) AS schedule_month,
    EXTRACT(YEAR FROM s.sch_date) AS schedule_year,
    s.order_num,
    s.start_time,
    s.end_time,
    s.description,
    e.event_name,
    e.status AS event_status,
    a.action_name,
    a.action_type,
    a.address
FROM schedules s
JOIN trips t ON s.trip_id = t.trip_id
LEFT JOIN events e
    ON s.trip_id = e.trip_id
   AND s.order_num = e.order_num
LEFT JOIN actions a
    ON e.event_id = a.event_id
ORDER BY s.sch_date, s.start_time, s.order_num;


-- =====================================================
-- SELECT QUERY 4B
-- Description:
-- Show schedule rows that have at least one related action.
-- Method: EXISTS
-- =====================================================
SELECT
    s.trip_id,
    t.trip_name,
    s.sch_date,
    EXTRACT(DAY FROM s.sch_date) AS schedule_day,
    EXTRACT(MONTH FROM s.sch_date) AS schedule_month,
    EXTRACT(YEAR FROM s.sch_date) AS schedule_year,
    s.order_num,
    s.start_time,
    s.end_time,
    s.description
FROM schedules s
JOIN trips t ON s.trip_id = t.trip_id
WHERE EXISTS (
    SELECT 1
    FROM events e
    JOIN actions a ON e.event_id = a.event_id
    WHERE e.trip_id = s.trip_id
      AND e.order_num = s.order_num
)
ORDER BY s.sch_date, s.start_time, s.order_num;


-- =====================================================
-- SELECT QUERY 5
-- Description:
-- Participants registered to more than one trip.
-- =====================================================
SELECT
    p.participant_id,
    p.first_name,
    p.last_name,
    p.phone,
    p.email,
    COUNT(tp.trip_id) AS number_of_trips,
    MIN(t.start_date) AS first_trip_date,
    MAX(t.end_date) AS last_trip_date
FROM participants p
JOIN trip_participants tp ON p.participant_id = tp.participant_id
JOIN trips t ON tp.trip_id = t.trip_id
GROUP BY
    p.participant_id,
    p.first_name,
    p.last_name,
    p.phone,
    p.email
HAVING COUNT(tp.trip_id) > 1
ORDER BY number_of_trips DESC, p.last_name;


-- =====================================================
-- SELECT QUERY 6
-- Description:
-- Popular routes by number of participants and trips.
-- =====================================================
SELECT
    r.route_id,
    r.route_name,
    r.region,
    r.distance_km,
    r.duration_hours,
    r.difficulty_level,
    COUNT(DISTINCT t.trip_id) AS number_of_trips,
    COUNT(tp.participant_id) AS total_registered_participants,
    ROUND(AVG(t.group_size), 2) AS average_group_size
FROM routes r
JOIN trips t ON r.route_id = t.route_id
LEFT JOIN trip_participants tp ON t.trip_id = tp.trip_id
GROUP BY
    r.route_id,
    r.route_name,
    r.region,
    r.distance_km,
    r.duration_hours,
    r.difficulty_level
ORDER BY total_registered_participants DESC, number_of_trips DESC;


-- =====================================================
-- SELECT QUERY 7
-- Description:
-- Trips with more registered participants than the average.
-- =====================================================
SELECT
    t.trip_id,
    t.trip_name,
    t.group_size,
    t.status,
    COUNT(tp.participant_id) AS registered_participants,
    ROUND(
        COUNT(tp.participant_id)::numeric / NULLIF(t.group_size, 0) * 100,
        2
    ) AS occupancy_percent
FROM trips t
JOIN trip_participants tp ON t.trip_id = tp.trip_id
GROUP BY
    t.trip_id,
    t.trip_name,
    t.group_size,
    t.status
HAVING COUNT(tp.participant_id) > (
    SELECT AVG(participant_count)
    FROM (
        SELECT COUNT(*) AS participant_count
        FROM trip_participants
        GROUP BY trip_id
    ) AS trip_counts
)
ORDER BY registered_participants DESC;


-- =====================================================
-- SELECT QUERY 8
-- Description:
-- Actions and events analysis by action type and month.
-- =====================================================
SELECT
    a.action_type,
    EXTRACT(YEAR FROM e.event_date) AS event_year,
    EXTRACT(MONTH FROM e.event_date) AS event_month,
    COUNT(a.action_id) AS number_of_actions,
    COUNT(DISTINCT e.event_id) AS number_of_events,
    COUNT(DISTINCT e.trip_id) AS number_of_trips,
    SUM(e.cost) AS related_events_total_cost
FROM actions a
JOIN events e ON a.event_id = e.event_id
GROUP BY
    a.action_type,
    EXTRACT(YEAR FROM e.event_date),
    EXTRACT(MONTH FROM e.event_date)
ORDER BY event_year, event_month, number_of_actions DESC;


-- =====================================================
-- UPDATE QUERY 1
-- Description:
-- Mark trips as completed if their end date has already passed.
-- =====================================================

-- Before:
SELECT
    trip_id,
    trip_name,
    start_date,
    end_date,
    status
FROM trips
WHERE end_date < CURRENT_DATE
ORDER BY end_date;

-- Update:
UPDATE trips
SET status = 'completed'
WHERE end_date < CURRENT_DATE;

-- After:
SELECT
    trip_id,
    trip_name,
    start_date,
    end_date,
    status
FROM trips
WHERE end_date < CURRENT_DATE
ORDER BY end_date;


-- =====================================================
-- UPDATE QUERY 2
-- Description:
-- Increase future event costs by 10 percent
-- only for events that belong to long or hard routes.
-- =====================================================

-- Before:
SELECT
    e.event_id,
    e.event_name,
    e.event_date,
    e.cost,
    t.trip_name,
    r.route_name,
    r.distance_km,
    r.difficulty_level
FROM events e
JOIN trips t ON e.trip_id = t.trip_id
JOIN routes r ON t.route_id = r.route_id
WHERE e.event_date > CURRENT_DATE
  AND (
        r.distance_km >= 10
        OR LOWER(r.difficulty_level) = 'hard'
      )
ORDER BY e.event_date;

-- Update:
UPDATE events e
SET cost = cost * 1.10
FROM trips t
JOIN routes r ON t.route_id = r.route_id
WHERE e.trip_id = t.trip_id
  AND e.event_date > CURRENT_DATE
  AND (
        r.distance_km >= 10
        OR LOWER(r.difficulty_level) = 'hard'
      );

-- After:
SELECT
    e.event_id,
    e.event_name,
    e.event_date,
    e.cost,
    t.trip_name,
    r.route_name,
    r.distance_km,
    r.difficulty_level
FROM events e
JOIN trips t ON e.trip_id = t.trip_id
JOIN routes r ON t.route_id = r.route_id
WHERE e.event_date > CURRENT_DATE
  AND (
        r.distance_km >= 10
        OR LOWER(r.difficulty_level) = 'hard'
      )
ORDER BY e.event_date;


-- =====================================================
-- UPDATE QUERY 3
-- Description:
-- Change route difficulty to 'Hard' for routes whose distance
-- is higher than the average route distance.
-- =====================================================

-- Before:
SELECT
    route_id,
    route_name,
    region,
    distance_km,
    difficulty_level
FROM routes
WHERE distance_km > (
    SELECT AVG(distance_km)
    FROM routes
)
ORDER BY distance_km DESC;

-- Update:
UPDATE routes
SET difficulty_level = 'Hard'
WHERE distance_km > (
    SELECT AVG(distance_km)
    FROM routes
);

-- After:
SELECT
    route_id,
    route_name,
    region,
    distance_km,
    difficulty_level
FROM routes
WHERE distance_km > (
    SELECT AVG(distance_km)
    FROM routes
)
ORDER BY distance_km DESC;

-- =====================================================
-- DELETE QUERY 1
-- Description:
-- Delete actions of type Info.
-- =====================================================

-- Before:
SELECT
    action_id,
    action_name,
    action_type,
    address,
    event_id
FROM actions
WHERE LOWER(action_type) = 'info'
LIMIT 10;

-- Delete:
DELETE FROM actions
WHERE LOWER(action_type) = 'info';

-- After:
SELECT
    action_id,
    action_name,
    action_type,
    address,
    event_id
FROM actions
WHERE LOWER(action_type) = 'info'
LIMIT 10;


-- =====================================================
-- DELETE QUERY 2
-- Description:
-- Delete participants from trips that already ended.
-- =====================================================

-- Before:
SELECT
    tp.trip_id,
    t.trip_name,
    t.end_date,
    t.status,
    tp.participant_id,
    p.first_name,
    p.last_name
FROM trip_participants tp
JOIN trips t ON tp.trip_id = t.trip_id
JOIN participants p ON tp.participant_id = p.participant_id
WHERE t.end_date < CURRENT_DATE
ORDER BY t.end_date, t.trip_id
LIMIT 10;

-- Delete:
DELETE FROM trip_participants tp
USING trips t
WHERE tp.trip_id = t.trip_id
  AND t.end_date < CURRENT_DATE;

-- After:
SELECT
    tp.trip_id,
    t.trip_name,
    t.end_date,
    t.status,
    tp.participant_id,
    p.first_name,
    p.last_name
FROM trip_participants tp
JOIN trips t ON tp.trip_id = t.trip_id
JOIN participants p ON tp.participant_id = p.participant_id
WHERE t.end_date < CURRENT_DATE
ORDER BY t.end_date, t.trip_id
LIMIT 10;


-- =====================================================
-- DELETE QUERY 3
-- Description:
-- Delete actions that are connected to events whose cost is lower than 100.
-- =====================================================

-- Before:
SELECT
    action_id,
    action_name,
    action_type,
    event_id
FROM actions
WHERE event_id IN (
    SELECT event_id
    FROM events
    WHERE cost < 100
)
LIMIT 10;

-- Delete:
DELETE FROM actions
WHERE event_id IN (
    SELECT event_id
    FROM events
    WHERE cost < 100
);

-- After:
SELECT
    action_id,
    action_name,
    action_type,
    event_id
FROM actions
WHERE event_id IN (
    SELECT event_id
    FROM events
    WHERE cost < 100
)
LIMIT 10;