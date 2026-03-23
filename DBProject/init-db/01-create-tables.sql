-- =========================
-- ROUTES
-- =========================
CREATE TABLE routes (
    route_id SERIAL PRIMARY KEY,
    route_name VARCHAR(100) NOT NULL,
    region VARCHAR(100) NOT NULL,
    distance_km NUMERIC NOT NULL CHECK (distance_km > 0),
    duration_hours NUMERIC NOT NULL CHECK (duration_hours > 0),
    difficulty_level VARCHAR(50) NOT NULL
);

-- =========================
-- TRANSPORT TYPES
-- =========================
CREATE TABLE transport_types (
    transport_type_id SERIAL PRIMARY KEY,
    transport_type_name VARCHAR(100) NOT NULL UNIQUE
);

-- =========================
-- TRIPS
-- =========================
CREATE TABLE trips (
    trip_id SERIAL PRIMARY KEY,
    trip_name VARCHAR(100) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    group_size INT NOT NULL CHECK (group_size > 0),
    status VARCHAR(50) NOT NULL,
    route_id INT NOT NULL,
    transport_type_id INT NOT NULL,

    CHECK (end_date >= start_date),

    FOREIGN KEY (route_id) REFERENCES routes(route_id),
    FOREIGN KEY (transport_type_id) REFERENCES transport_types(transport_type_id)
);

-- =========================
-- PARTICIPANTS
-- =========================
CREATE TABLE participants (
    participant_id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    birth_date DATE NOT NULL
);

-- =========================
-- GUIDES (IS-A PARTICIPANT)
-- =========================
CREATE TABLE guides (
    participant_id INT PRIMARY KEY,
    license_number VARCHAR(100) NOT NULL UNIQUE,
    experience_years INT NOT NULL CHECK (experience_years >= 0),

    FOREIGN KEY (participant_id) REFERENCES participants(participant_id)
);

-- =========================
-- TRIP PARTICIPANTS (N:M)
-- =========================
CREATE TABLE trip_participants (
    trip_id INT NOT NULL,
    participant_id INT NOT NULL,

    PRIMARY KEY (trip_id, participant_id),

    FOREIGN KEY (trip_id) REFERENCES trips(trip_id),
    FOREIGN KEY (participant_id) REFERENCES participants(participant_id)
);

-- =========================
-- SCHEDULES (Composite PK)
-- =========================
CREATE TABLE schedules (
    trip_id INT NOT NULL,
    order_num INT NOT NULL CHECK (order_num > 0),
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    description TEXT NOT NULL,
    sch_date DATE NOT NULL,

    PRIMARY KEY (trip_id, order_num),

    CHECK (end_time > start_time),

    FOREIGN KEY (trip_id) REFERENCES trips(trip_id)
);

-- =========================
-- EVENTS
-- =========================
CREATE TABLE events (
    event_id SERIAL PRIMARY KEY,
    event_name VARCHAR(100) NOT NULL,
    event_date DATE NOT NULL,
    start_hour TIME NOT NULL,
    end_hour TIME NOT NULL,
    cost NUMERIC NOT NULL CHECK (cost >= 0),
    status VARCHAR(50) NOT NULL,
    trip_id INT NOT NULL,
    order_num INT NOT NULL,

    CHECK (end_hour > start_hour),

    FOREIGN KEY (trip_id, order_num)
        REFERENCES schedules(trip_id, order_num)
);

-- =========================
-- ACTIONS
-- =========================
CREATE TABLE actions (
    action_id SERIAL PRIMARY KEY,
    address VARCHAR(255) NOT NULL,
    action_type VARCHAR(100) NOT NULL,
    action_name VARCHAR(100) NOT NULL,
    event_id INT NOT NULL,

    FOREIGN KEY (event_id) REFERENCES events(event_id)
);