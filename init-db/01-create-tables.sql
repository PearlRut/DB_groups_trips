-- =========================
-- ROUTES
-- =========================
CREATE TABLE routes (
    route_id SERIAL PRIMARY KEY,
    route_name VARCHAR(100),
    region VARCHAR(100),
    distance_km NUMERIC,
    duration_hours NUMERIC,
    difficulty_level VARCHAR(50)
);

-- =========================
-- TRANSPORT TYPES
-- =========================
CREATE TABLE transport_types (
    transport_type_id SERIAL PRIMARY KEY,
    transport_type_name VARCHAR(100)
);

-- =========================
-- TRIPS
-- =========================
CREATE TABLE trips (
    trip_id SERIAL PRIMARY KEY,
    trip_name VARCHAR(100),
    start_date DATE,
    end_date DATE,
    group_size INT,
    status VARCHAR(50),

    route_id INT,
    transport_type_id INT,

    FOREIGN KEY (route_id) REFERENCES routes(route_id),
    FOREIGN KEY (transport_type_id) REFERENCES transport_types(transport_type_id)
);

-- =========================
-- PARTICIPANTS
-- =========================
CREATE TABLE participants (
    participant_id SERIAL PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone VARCHAR(50),
    email VARCHAR(100),
    birth_date DATE
);

-- =========================
-- GUIDES (IS-A PARTICIPANT)
-- =========================
CREATE TABLE guides (
    participant_id INT PRIMARY KEY,
    license_number VARCHAR(100),
    experience_years INT,

    FOREIGN KEY (participant_id) REFERENCES participants(participant_id)
);

-- =========================
-- TRIP PARTICIPANTS (N:M)
-- =========================
CREATE TABLE trip_participants (
    trip_id INT,
    participant_id INT,

    PRIMARY KEY (trip_id, participant_id),

    FOREIGN KEY (trip_id) REFERENCES trips(trip_id),
    FOREIGN KEY (participant_id) REFERENCES participants(participant_id)
);

-- =========================
-- SCHEDULES (Composite PK)
-- =========================
CREATE TABLE schedules (
    trip_id INT,
    order_num INT,
    start_time TIME,
    end_time TIME,
    description TEXT,
    sch_date DATE,

    PRIMARY KEY (trip_id, order_num),

    FOREIGN KEY (trip_id) REFERENCES trips(trip_id)
);

-- =========================
-- EVENTS
-- =========================
CREATE TABLE events (
    event_id SERIAL PRIMARY KEY,
    event_name VARCHAR(100),
    event_date DATE,
    start_hour TIME,
    end_hour TIME,
    cost NUMERIC,
    status VARCHAR(50),

    trip_id INT,
    order_num INT,

    FOREIGN KEY (trip_id, order_num)
        REFERENCES schedules(trip_id, order_num)
);

-- =========================
-- ACTIONS
-- =========================
CREATE TABLE actions (
    action_id SERIAL PRIMARY KEY,
    address VARCHAR(255),
    action_type VARCHAR(100),
    action_name VARCHAR(100),

    event_id INT,
    FOREIGN KEY (event_id) REFERENCES events(event_id)
);