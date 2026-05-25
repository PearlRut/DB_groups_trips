-- =====================================================
-- Phase C - Views.sql
-- Systems: Group Trips & Logistics Unified Database
-- =====================================================

-- -----------------------------------------------------
-- VIEW 1: trip_planning_summary_view
-- Description:
-- Designed from the perspective of our original department (Group Trips).
-- Provides an administrative summary of each trip, including route details,
-- start/end dates, group limits, registered counts, occupancy rates, and statuses.
-- -----------------------------------------------------
CREATE OR REPLACE VIEW public.trip_planning_summary_view AS
SELECT
    t.trip_id,
    t.trip_name,
    t.trip_type,
    r.route_name,
    r.region,
    r.difficulty_level,
    t.start_date,
    t.end_date,
    t.group_size,
    COUNT(tp.participant_id) AS registered_participants,
    t.group_size - COUNT(tp.participant_id) AS available_places,
    ROUND((COUNT(tp.participant_id)::numeric / NULLIF(t.group_size, 0)) * 100, 2) AS occupancy_percentage,
    t.status
FROM public.trips t
JOIN public.routes r ON t.route_id = r.route_id
LEFT JOIN public.trip_participants tp ON t.trip_id = tp.trip_id
GROUP BY
    t.trip_id,
    t.trip_name,
    t.trip_type,
    r.route_name,
    r.region,
    r.difficulty_level,
    t.start_date,
    t.end_date,
    t.group_size,
    t.status;


-- -----------------------------------------------------
-- VIEW 2: trip_logistics_operations_view
-- Description:
-- Designed from the perspective of the logistics department (the other group).
-- Merges geographical locations, specific transport vehicles, allocated equipment,
-- and the suppliers providing them, linked directly to the unified trips.
-- -----------------------------------------------------
CREATE OR REPLACE VIEW public.trip_logistics_operations_view AS
SELECT
    t.trip_id,
    t.trip_name,
    t.trip_type,
    t.start_date,
    -- Transportation details
    tr.transportid AS specific_vehicle_id,
    tt.transport_type_name AS vehicle_category,
    tr.capacity AS vehicle_capacity,
    s_trans.company_name AS transport_supplier,
    -- Equipment details
    eq.equipmentid,
    eq.itemname AS equipment_name,
    te.quantityallocated AS equipment_quantity,
    s_eq.company_name AS equipment_supplier,
    -- Location details
    loc.locationid,
    loc.locationname,
    loc.region AS location_region,
    loc.address AS location_address
FROM public.trips t
LEFT JOIN public.trip_transportation tt_map ON t.trip_id = tt_map.trip_id
LEFT JOIN public.transportation tr ON tt_map.transportid = tr.transportid
LEFT JOIN public.transport_types tt ON tr.transport_type_id = tt.transport_type_id
LEFT JOIN public.supplier s_trans ON tr.supplierid = s_trans.supplierid
LEFT JOIN public.trip_equipment te ON t.trip_id = te.trip_id
LEFT JOIN public.equipment eq ON te.equipmentid = eq.equipmentid
LEFT JOIN public.supplier s_eq ON eq.supplierid = s_eq.supplierid
LEFT JOIN public.location_trip lt ON t.trip_id = lt.trip_id
LEFT JOIN public.location loc ON lt.locationid = loc.locationid;


-- =====================================================
-- QUERIES ON VIEW 1 (Group Trips Perspective)
-- =====================================================

-- -----------------------------------------------------
-- QUERY 1.1: Identify highly occupied hard trips
-- Description:
-- Find trips on difficult routes ('Hard') with an occupancy
-- percentage of 75% or higher, sorted by highest occupancy.
-- -----------------------------------------------------
SELECT 
    trip_id,
    trip_name,
    route_name,
    difficulty_level,
    group_size,
    registered_participants,
    occupancy_percentage,
    status
FROM public.trip_planning_summary_view
WHERE LOWER(difficulty_level) = 'hard'
  AND occupancy_percentage >= 75.00
ORDER BY occupancy_percentage DESC;


-- -----------------------------------------------------
-- QUERY 1.2: Monthly regional planning statistics
-- Description:
-- Calculate total group slots, total actual registrations,
-- total empty slots, and trip counts grouped by region and month.
-- -----------------------------------------------------
SELECT 
    region,
    EXTRACT(YEAR FROM start_date) AS plan_year,
    EXTRACT(MONTH FROM start_date) AS plan_month,
    COUNT(trip_id) AS total_trips,
    SUM(group_size) AS total_max_capacity,
    SUM(registered_participants) AS total_registrations,
    SUM(available_places) AS total_empty_seats
FROM public.trip_planning_summary_view
GROUP BY 
    region, 
    EXTRACT(YEAR FROM start_date), 
    EXTRACT(MONTH FROM start_date)
ORDER BY plan_year, plan_month, total_trips DESC;


-- =====================================================
-- QUERIES ON VIEW 2 (Logistics Perspective)
-- =====================================================

-- -----------------------------------------------------
-- QUERY 2.1: Equipment and Transport Supplier allocation summary
-- Description:
-- Calculate the total quantity of equipment allocated and total vehicles booked
-- from each supplier to verify operational load on external partners.
-- -----------------------------------------------------
SELECT 
    COALESCE(transport_supplier, equipment_supplier) AS supplier_company,
    COUNT(DISTINCT specific_vehicle_id) AS total_vehicles_booked,
    COALESCE(SUM(equipment_quantity), 0) AS total_equipment_items_allocated,
    COUNT(DISTINCT trip_id) AS active_trips_supported
FROM public.trip_logistics_operations_view
WHERE transport_supplier IS NOT NULL OR equipment_supplier IS NOT NULL
GROUP BY COALESCE(transport_supplier, equipment_supplier)
ORDER BY total_equipment_items_allocated DESC, total_vehicles_booked DESC;


-- -----------------------------------------------------
-- QUERY 2.2: Vehicle capacity checking by location region
-- Description:
-- Show trips passing through specific location regions (e.g. 'South') 
-- that have booked vehicles with capacity greater than 15, to ensure 
-- large transport safety compliance.
-- -----------------------------------------------------
SELECT DISTINCT
    trip_id,
    trip_name,
    location_region,
    locationname,
    vehicle_category,
    vehicle_capacity,
    transport_supplier
FROM public.trip_logistics_operations_view
WHERE location_region = 'South'
  AND vehicle_capacity > 15
ORDER BY vehicle_capacity DESC, trip_name;
