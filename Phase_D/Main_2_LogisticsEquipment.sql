-- =====================================================
-- Phase D - Main Program 2
-- File: Main_2_LogisticsEquipment.sql
-- Purpose: Run Function 2 and Procedure 2
-- =====================================================


-- =====================================================
-- 1. Function call:
-- Open Ref Cursor with logistics data by region
-- =====================================================

BEGIN;

SELECT public.get_logistics_by_region_cursor('North');

FETCH ALL FROM logistics_cursor;

COMMIT;


-- =====================================================
-- 2. Show data before procedure
-- Notice:
-- The example uses trip_id = 1 and equipmentid = 124.
-- If these IDs do not exist in your database, replace them.
-- =====================================================

SELECT *
FROM public.trip_equipment
WHERE trip_id = 1
  AND equipmentid = 124;

SELECT 
    equipmentid,
    itemname,
    totalinstock
FROM public.equipment
WHERE equipmentid = 124;


-- =====================================================
-- 3. Procedure call:
-- Allocate equipment to trip and update stock
-- =====================================================

CALL public.allocate_equipment_to_trip(
    1,
    124,
    1,
    CURRENT_DATE,
    CURRENT_DATE + 3
);


-- =====================================================
-- 4. Show data after procedure
-- =====================================================

SELECT *
FROM public.trip_equipment
WHERE trip_id = 1
  AND equipmentid = 124;

SELECT 
    equipmentid,
    itemname,
    totalinstock
FROM public.equipment
WHERE equipmentid = 124;


-- =====================================================
-- 5. Show stock log written by trigger
-- =====================================================

SELECT *
FROM public.equipment_stock_log
WHERE equipmentid = 124
ORDER BY changed_at DESC
LIMIT 10;