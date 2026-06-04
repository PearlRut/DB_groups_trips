-- =====================================================
-- Phase D - Function 2
-- File: Function_2_LogisticsCursor.sql
-- Purpose: Return a Ref Cursor with logistics details by region
-- =====================================================

CREATE OR REPLACE FUNCTION public.get_logistics_by_region_cursor(
    p_region VARCHAR,
    p_cursor_name REFCURSOR DEFAULT 'logistics_cursor'
)
RETURNS REFCURSOR
LANGUAGE plpgsql
AS $$
BEGIN
    -- Open a cursor for logistics information of trips in the requested region
    OPEN p_cursor_name FOR
        SELECT DISTINCT
            t.trip_id,
            t.trip_name,
            t.trip_type,
            t.start_date,
            t.end_date,
            loc.region AS location_region,
            loc.locationname,
            loc.address,
            tr.transportid,
            tt.transport_type_name,
            tr.capacity AS vehicle_capacity,
            s_trans.company_name AS transport_supplier,
            eq.equipmentid,
            eq.itemname AS equipment_name,
            te.quantityallocated,
            s_eq.company_name AS equipment_supplier
        FROM public.trips t
        LEFT JOIN public.location_trip lt
            ON t.trip_id = lt.trip_id
        LEFT JOIN public.location loc
            ON lt.locationid = loc.locationid
        LEFT JOIN public.trip_transportation ttr
            ON t.trip_id = ttr.trip_id
        LEFT JOIN public.transportation tr
            ON ttr.transportid = tr.transportid
        LEFT JOIN public.transport_types tt
            ON tr.transport_type_id = tt.transport_type_id
        LEFT JOIN public.supplier s_trans
            ON tr.supplierid = s_trans.supplierid
        LEFT JOIN public.trip_equipment te
            ON t.trip_id = te.trip_id
        LEFT JOIN public.equipment eq
            ON te.equipmentid = eq.equipmentid
        LEFT JOIN public.supplier s_eq
            ON eq.supplierid = s_eq.supplierid
        WHERE p_region IS NULL
           OR LOWER(loc.region) = LOWER(p_region)
        ORDER BY
            t.trip_id,
            loc.locationname,
            eq.itemname;

    RETURN p_cursor_name;

EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error in get_logistics_by_region_cursor for region %: %', p_region, SQLERRM;
END;
$$;