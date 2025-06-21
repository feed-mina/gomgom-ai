-- Advanced spatial indexes with earthdistance extension
-- This file includes the earthdistance extension for advanced spatial queries
-- Use this if you need distance calculations and advanced spatial operations

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS earthdistance;
CREATE EXTENSION IF NOT EXISTS cube;

CREATE INDEX IF NOT EXISTS idx_recipes_name_description ON recipes USING gin (to_tsvector('english', name || ' ' || COALESCE(description, '')));
CREATE INDEX IF NOT EXISTS idx_recipes_difficulty ON recipes(difficulty);
CREATE INDEX IF NOT EXISTS idx_recipes_cooking_time ON recipes(cooking_time);

CREATE INDEX IF NOT EXISTS idx_ingredients_name_price ON ingredients(name, price);
CREATE INDEX IF NOT EXISTS idx_ingredients_ko_name_ingredient_id ON ingredients_ko(name, ingredient_id);

-- Advanced spatial index for locations using earthdistance
CREATE INDEX IF NOT EXISTS idx_locations_coordinates ON locations USING gist (ll_to_earth(latitude, longitude));
CREATE INDEX IF NOT EXISTS idx_locations_address ON locations USING gin (to_tsvector('english', COALESCE(address, '')));

CREATE INDEX IF NOT EXISTS idx_recommendations_user_score ON recommendations(user_id, score DESC);
CREATE INDEX IF NOT EXISTS idx_recommendations_recipe_score ON recommendations(recipe_id, score DESC);

CREATE INDEX IF NOT EXISTS idx_recipes_created_updated ON recipes(created_at, updated_at);
CREATE INDEX IF NOT EXISTS idx_ingredients_created_updated ON ingredients(created_at, updated_at);
CREATE INDEX IF NOT EXISTS idx_locations_created_updated ON locations(created_at, updated_at);
CREATE INDEX IF NOT EXISTS idx_recommendations_created_updated ON recommendations(created_at, updated_at);

CREATE INDEX IF NOT EXISTS idx_active_users ON users(email) WHERE is_active = true;

CREATE INDEX IF NOT EXISTS idx_recipes_name_created ON recipes(name, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_ingredients_name_created ON ingredients(name, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_locations_name_created ON locations(name, created_at DESC); 