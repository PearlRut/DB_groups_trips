SELECT 'routes' AS table_name, COUNT(*) FROM routes
UNION ALL
SELECT 'transport_types', COUNT(*) FROM transport_types
UNION ALL
SELECT 'trips', COUNT(*) FROM trips
UNION ALL
SELECT 'participants', COUNT(*) FROM participants
UNION ALL
SELECT 'guides', COUNT(*) FROM guides
UNION ALL
SELECT 'trip_participants', COUNT(*) FROM trip_participants
UNION ALL
SELECT 'schedules', COUNT(*) FROM schedules
UNION ALL
SELECT 'events', COUNT(*) FROM events
UNION ALL
SELECT 'actions', COUNT(*) FROM actions;