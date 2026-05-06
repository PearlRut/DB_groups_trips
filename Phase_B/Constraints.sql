-- =====================================================
-- Phase B - Constraints.sql
-- System: Group Trips Management
-- =====================================================

-- Constraint 1: group_size must be positive
ALTER TABLE trips
ADD CONSTRAINT chk_trips_group_size_positive
CHECK (group_size > 0);

-- Test violation for Constraint 1
INSERT INTO trips (
    trip_id,
    trip_name,
    start_date,
    end_date,
    group_size,
    status,
    route_id,
    transport_type_id
)
VALUES (
    999001,
    'Invalid Trip',
    CURRENT_DATE,
    CURRENT_DATE + INTERVAL '1 day',
    -5,
    'planned',
    1,
    1
);


-- Constraint 2: event cost must be non-negative
ALTER TABLE events
ADD CONSTRAINT chk_events_cost_non_negative
CHECK (cost >= 0);

-- Test violation for Constraint 2
INSERT INTO events (
    event_id,
    event_name,
    event_date,
    start_hour,
    end_hour,
    cost,
    status,
    trip_id,
    order_num
)
VALUES (
    999002,
    'Invalid Event',
    CURRENT_DATE,
    '10:00',
    '12:00',
    -100,
    'planned',
    1,
    1
);


-- Constraint 3: guide experience years must be non-negative
ALTER TABLE guides
ADD CONSTRAINT chk_guides_experience_years_non_negative
CHECK (experience_years >= 0);

-- Test violation for Constraint 3
INSERT INTO guides (
    participant_id,
    license_number,
    experience_years
)
VALUES (
    1,
    'INVALID-LICENSE',
    -3
);