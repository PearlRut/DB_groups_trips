-- Phase C: Physical Database Integration Script
-- Target Database: unified_db

-- 1. Alter public.trips to add the trip_type column and migrate the data
ALTER TABLE public.trips ADD COLUMN trip_type VARCHAR(30);

-- Migrate the trip_type data from the temporary trip table where IDs match
UPDATE public.trips t
SET trip_type = o.trip_type
FROM public.trip o
WHERE t.trip_id = o.tripid;

-- Provide a default for any trips that did not match (since ours has 502 and theirs 500)
UPDATE public.trips SET trip_type = 'Standard' WHERE trip_type IS NULL;

-- Enforce NOT NULL constraint on trip_type
ALTER TABLE public.trips ALTER COLUMN trip_type SET NOT NULL;


-- 2. Redirect foreign keys from the singular "trip" table to our master "trips" table
-- Redirect location_trip
ALTER TABLE public.location_trip DROP CONSTRAINT location_trip_tripid_fkey;
ALTER TABLE public.location_trip RENAME COLUMN tripid TO trip_id;
ALTER TABLE public.location_trip ADD CONSTRAINT location_trip_trip_id_fkey 
  FOREIGN KEY (trip_id) REFERENCES public.trips(trip_id) ON DELETE CASCADE;

-- Redirect trip_equipment
ALTER TABLE public.trip_equipment DROP CONSTRAINT trip_equipment_tripid_fkey;
ALTER TABLE public.trip_equipment RENAME COLUMN tripid TO trip_id;
ALTER TABLE public.trip_equipment ADD CONSTRAINT trip_equipment_trip_id_fkey 
  FOREIGN KEY (trip_id) REFERENCES public.trips(trip_id) ON DELETE CASCADE;

-- Redirect trip_transportation
ALTER TABLE public.trip_transportation DROP CONSTRAINT trip_transportation_tripid_fkey;
ALTER TABLE public.trip_transportation RENAME COLUMN tripid TO trip_id;
ALTER TABLE public.trip_transportation ADD CONSTRAINT trip_transportation_trip_id_fkey 
  FOREIGN KEY (trip_id) REFERENCES public.trips(trip_id) ON DELETE CASCADE;


-- 3. Integrate transport_types and transportation (vehicle_type to FK)
-- Ensure 'Minibus' exists in our transport_types catalog
INSERT INTO public.transport_types (transport_type_name) 
SELECT 'Minibus' 
WHERE NOT EXISTS (SELECT 1 FROM public.transport_types WHERE transport_type_name = 'Minibus');

-- Add the new transport_type_id foreign key column to transportation
ALTER TABLE public.transportation ADD COLUMN transport_type_id INT;

-- Populate the transport_type_id foreign key based on vehicle_type name matching
UPDATE public.transportation t
SET transport_type_id = tt.transport_type_id
FROM public.transport_types tt
WHERE t.vehicle_type = tt.transport_type_name;

-- Fallback default in case any didn't match (for safety)
UPDATE public.transportation SET transport_type_id = 1 WHERE transport_type_id IS NULL;

-- Make it NOT NULL
ALTER TABLE public.transportation ALTER COLUMN transport_type_id SET NOT NULL;

-- Add foreign key constraint to transportation pointing to transport_types
ALTER TABLE public.transportation ADD CONSTRAINT transportation_transport_type_id_fkey
  FOREIGN KEY (transport_type_id) REFERENCES public.transport_types(transport_type_id) ON DELETE RESTRICT;

-- Drop the old redundant vehicle_type text column from transportation
ALTER TABLE public.transportation DROP COLUMN vehicle_type;


-- 4. Clean up the unused duplicate tables from the other group
DROP TABLE IF EXISTS public.registers_to CASCADE;
DROP TABLE IF EXISTS public.participant CASCADE;
DROP TABLE IF EXISTS public.trip CASCADE;

-- Rename singular tables of the other group to match a neat unified convention if needed,
-- or keep them as is (supplier -> supplier, equipment -> equipment, etc. is perfect).
