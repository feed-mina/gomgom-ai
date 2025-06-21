-- Add missing columns to locations table
ALTER TABLE locations 
ADD COLUMN IF NOT EXISTS phone VARCHAR,
ADD COLUMN IF NOT EXISTS website VARCHAR,
ADD COLUMN IF NOT EXISTS description TEXT; 