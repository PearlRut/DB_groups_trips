-- =====================================================
-- Phase D - AlterTable.sql
-- System: Group Trips & Logistics Unified Database
-- Purpose: Add log tables for triggers and procedures
-- =====================================================


-- =====================================================
-- 1. Log table for trip status changes
-- This table will be filled automatically by an UPDATE trigger on trips.status
-- =====================================================

CREATE TABLE IF NOT EXISTS public.trip_status_log (
    log_id SERIAL PRIMARY KEY,
    trip_id INT NOT NULL,
    old_status VARCHAR(50),
    new_status VARCHAR(50),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    changed_by VARCHAR(100) DEFAULT CURRENT_USER,

    CONSTRAINT fk_trip_status_log_trip
        FOREIGN KEY (trip_id)
        REFERENCES public.trips(trip_id)
        ON DELETE CASCADE
);


-- =====================================================
-- 2. Log table for equipment stock changes
-- This table will be filled automatically by an UPDATE trigger on equipment.totalinstock
-- =====================================================

CREATE TABLE IF NOT EXISTS public.equipment_stock_log (
    log_id SERIAL PRIMARY KEY,
    equipmentid INT NOT NULL,
    old_totalinstock INT,
    new_totalinstock INT,
    quantity_changed INT,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    changed_by VARCHAR(100) DEFAULT CURRENT_USER,

    CONSTRAINT fk_equipment_stock_log_equipment
        FOREIGN KEY (equipmentid)
        REFERENCES public.equipment(equipmentid)
        ON DELETE CASCADE
);