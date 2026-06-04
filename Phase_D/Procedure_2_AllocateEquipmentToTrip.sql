-- =====================================================
-- Phase D - Procedure 2
-- File: Procedure_2_AllocateEquipmentToTrip.sql
-- Purpose: Allocate equipment to a trip and update stock
-- =====================================================

/*
contain:
Procedure
Explicit Cursor
FETCH
RECORD
IF / ELSE
INSERT
UPDATE
EXCEPTION
RAISE NOTICE*/

CREATE OR REPLACE PROCEDURE public.allocate_equipment_to_trip(
    p_trip_id INT,
    p_equipmentid INT,
    p_quantity INT,
    p_checkout_date DATE DEFAULT CURRENT_DATE,
    p_return_date DATE DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
DECLARE
    trip_rec RECORD;
    equipment_rec RECORD;
    cursor_was_opened BOOLEAN := FALSE;

    -- Explicit cursor for reading and locking the equipment row
    equipment_cur CURSOR FOR
        SELECT *
        FROM public.equipment
        WHERE equipmentid = p_equipmentid
        FOR UPDATE;
BEGIN
    -- Validate quantity
    IF p_quantity IS NULL OR p_quantity <= 0 THEN
        RAISE EXCEPTION 'Quantity must be positive. Given quantity: %', p_quantity;
    END IF;

    -- Validate dates
    IF p_return_date IS NOT NULL AND p_return_date < p_checkout_date THEN
        RAISE EXCEPTION 'Return date % cannot be before checkout date %',
            p_return_date, p_checkout_date;
    END IF;

    -- Check that the trip exists
    SELECT *
    INTO trip_rec
    FROM public.trips
    WHERE trip_id = p_trip_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Trip with id % does not exist', p_trip_id;
    END IF;

    -- Open explicit cursor and fetch equipment row
    OPEN equipment_cur;
    cursor_was_opened := TRUE;

    FETCH equipment_cur INTO equipment_rec;

    IF NOT FOUND THEN
        CLOSE equipment_cur;
        cursor_was_opened := FALSE;
        RAISE EXCEPTION 'Equipment with id % does not exist', p_equipmentid;
    END IF;

    -- Check stock
    IF equipment_rec.totalinstock < p_quantity THEN
        CLOSE equipment_cur;
        cursor_was_opened := FALSE;
        RAISE EXCEPTION
            'Not enough stock for equipment %. Requested: %, Available: %',
            p_equipmentid,
            p_quantity,
            equipment_rec.totalinstock;
    END IF;

    -- If this equipment is already allocated to this trip, increase the quantity
    IF EXISTS (
        SELECT 1
        FROM public.trip_equipment
        WHERE trip_id = p_trip_id
          AND equipmentid = p_equipmentid
    ) THEN
        UPDATE public.trip_equipment
        SET quantityallocated = quantityallocated + p_quantity,
            checkout_date = p_checkout_date,
            return_date = p_return_date
        WHERE trip_id = p_trip_id
          AND equipmentid = p_equipmentid;

        RAISE NOTICE
            'Existing allocation updated. Trip %, equipment %, added quantity %',
            p_trip_id,
            p_equipmentid,
            p_quantity;
    ELSE
        INSERT INTO public.trip_equipment (
            trip_id,
            equipmentid,
            quantityallocated,
            checkout_date,
            return_date
        )
        VALUES (
            p_trip_id,
            p_equipmentid,
            p_quantity,
            p_checkout_date,
            p_return_date
        );

        RAISE NOTICE
            'New allocation created. Trip %, equipment %, quantity %',
            p_trip_id,
            p_equipmentid,
            p_quantity;
    END IF;

    -- Update equipment stock
    UPDATE public.equipment
    SET totalinstock = totalinstock - p_quantity
    WHERE equipmentid = p_equipmentid;

    RAISE NOTICE
        'Stock updated for equipment %. Old stock: %, New stock: %',
        p_equipmentid,
        equipment_rec.totalinstock,
        equipment_rec.totalinstock - p_quantity;

    CLOSE equipment_cur;
    cursor_was_opened := FALSE;

EXCEPTION
    WHEN OTHERS THEN
        IF cursor_was_opened THEN
            CLOSE equipment_cur;
        END IF;

        RAISE EXCEPTION 'Error in allocate_equipment_to_trip: %', SQLERRM;
END;
$$;