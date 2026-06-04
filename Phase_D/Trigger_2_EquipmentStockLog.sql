-- =====================================================
-- Phase D - Trigger 2
-- File: Trigger_2_EquipmentStockLog.sql
-- Purpose: Log every update of equipment.totalinstock
-- =====================================================


-- Trigger function:
-- This function inserts a row into equipment_stock_log
-- whenever the stock amount of equipment changes.

CREATE OR REPLACE FUNCTION public.log_equipment_stock_update()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    -- Insert to log only if the stock really changed
    IF OLD.totalinstock IS DISTINCT FROM NEW.totalinstock THEN
        INSERT INTO public.equipment_stock_log (
            equipmentid,
            old_totalinstock,
            new_totalinstock,
            quantity_changed,
            changed_at,
            changed_by
        )
        VALUES (
            NEW.equipmentid,
            OLD.totalinstock,
            NEW.totalinstock,
            NEW.totalinstock - OLD.totalinstock,
            CURRENT_TIMESTAMP,
            CURRENT_USER
        );

        RAISE NOTICE 'Equipment % stock changed from % to %',
            NEW.equipmentid,
            OLD.totalinstock,
            NEW.totalinstock;
    END IF;

    RETURN NEW;

EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error in log_equipment_stock_update trigger: %', SQLERRM;
END;
$$;


-- Drop old trigger if it already exists, so the file can be run again safely

DROP TRIGGER IF EXISTS trg_log_equipment_stock_update ON public.equipment;


-- Create trigger:
-- Runs automatically after UPDATE of totalinstock on equipment

CREATE TRIGGER trg_log_equipment_stock_update
AFTER UPDATE OF totalinstock ON public.equipment
FOR EACH ROW
EXECUTE FUNCTION public.log_equipment_stock_update();