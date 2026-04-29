\copy routes(route_name, region, distance_km, duration_hours, difficulty_level) FROM '/tmp/data/routes.csv' DELIMITER ',' CSV HEADER;
\copy transport_types(transport_type_name) FROM '/tmp/data/transport_types.csv' DELIMITER ',' CSV HEADER;
\copy participants(first_name, last_name, phone, email, birth_date) FROM '/tmp/data/participants.csv' DELIMITER ',' CSV HEADER;
\copy trips(trip_name, start_date, end_date, group_size, status, route_id, transport_type_id) FROM '/tmp/data/trips.csv' DELIMITER ',' CSV HEADER;
\copy guides(participant_id, license_number, experience_years) FROM '/tmp/data/guides.csv' DELIMITER ',' CSV HEADER;
\copy schedules(trip_id, order_num, start_time, end_time, description, sch_date) FROM '/tmp/data/schedules.csv' DELIMITER ',' CSV HEADER;
\copy events(event_name, event_date, start_hour, end_hour, cost, status, trip_id, order_num) FROM '/tmp/data/events.csv' DELIMITER ',' CSV HEADER;
\copy actions(address, action_type, action_name, event_id) FROM '/tmp/data/actions.csv' DELIMITER ',' CSV HEADER;
\copy trip_participants(trip_id, participant_id) FROM '/tmp/data/trip_participants.csv' DELIMITER ',' CSV HEADER;