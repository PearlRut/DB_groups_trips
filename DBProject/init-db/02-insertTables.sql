-- =========================
-- ROUTES
-- =========================
INSERT INTO routes (route_name, region, distance_km, duration_hours, difficulty_level)
VALUES 
('Desert Trail', 'South', 15, 5, 'Medium'),
('Mountain Path', 'North', 8, 3, 'Hard');

-- =========================
-- TRANSPORT TYPES
-- =========================
INSERT INTO transport_types (transport_type_name)
VALUES 
('Bus'),
('Jeep');

-- =========================
-- TRIPS
-- =========================
INSERT INTO trips (trip_name, start_date, end_date, group_size, status, route_id, transport_type_id)
VALUES 
('Spring Trip', '2026-04-01', '2026-04-03', 20, 'Planned', 1, 1),
('Adventure Trip', '2026-05-10', '2026-05-12', 10, 'Open', 2, 2);

-- =========================
-- PARTICIPANTS
-- =========================
INSERT INTO participants (first_name, last_name, phone, email, birth_date)
VALUES
('Ruth', 'Gold', '0501234567', 'ruth@example.com', '1998-01-01'),
('Noa', 'Levi', '0507654321', 'noa@example.com', '2000-05-10');

-- =========================
-- GUIDES
-- =========================
INSERT INTO guides (participant_id, license_number, experience_years)
VALUES
(1, 'LIC123', 5);

-- =========================
-- TRIP PARTICIPANTS
-- =========================
INSERT INTO trip_participants (trip_id, participant_id)
VALUES
(1, 1),
(1, 2);

-- =========================
-- SCHEDULES
-- =========================
INSERT INTO schedules (trip_id, order_num, start_time, end_time, description, sch_date)
VALUES
(1, 1, '08:00', '10:00', 'Arrival and setup', '2026-04-01'),
(1, 2, '10:30', '13:00', 'Hiking', '2026-04-01');

-- =========================
-- EVENTS
-- =========================
INSERT INTO events (event_name, event_date, start_hour, end_hour, cost, status, trip_id, order_num)
VALUES
('Morning Briefing', '2026-04-01', '08:00', '09:00', 0, 'Scheduled', 1, 1);

-- =========================
-- ACTIONS
-- =========================
INSERT INTO actions (address, action_type, action_name, event_id)
VALUES
('Base Camp', 'Info', 'Introduction', 1);