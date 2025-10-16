-- Enums
CREATE TYPE gender_enum AS ENUM (
    'male',
    'female'
);

CREATE TYPE activity_level_enum AS ENUM (
    'sedentary',
    'light',
    'moderate',
    'active',
    'very_active'
);

CREATE TYPE calorie_goal_enum AS ENUM (
    'maintain',
    'mild_loss',
    'loss',
    'extreme_loss',
    'mild_gain',
    'gain'
);

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    surname VARCHAR NOT NULL,
    login VARCHAR UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS user_auth (
    user_id INTEGER PRIMARY KEY REFERENCES users(id), 
    password VARCHAR NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    last_login TIMESTAMP WITH TIME ZONE
);

CREATE TABLE IF NOT EXISTS oauth2_accounts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    provider VARCHAR NOT NULL,
    provider_id VARCHAR NOT NULL,
    provider_email VARCHAR,
    access_token VARCHAR,
    refresh_token VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS health_forms (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    age INTEGER,
    gender gender_enum,
    activity_level activity_level_enum,
    calorie_goal calorie_goal_enum,
    height INTEGER,
    weight INTEGER,
    number_of_meals_per_day INTEGER,
    diet_preferences JSON,
    intolerances JSON,
    medicament_usage JSON
);

CREATE TABLE IF NOT EXISTS plans (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    day_start DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS meals (
    id SERIAL PRIMARY KEY,
    plan_id INTEGER NOT NULL REFERENCES plans(id) ON DELETE CASCADE,
    meal_type VARCHAR,
    time TIME NOT NULL,
    description VARCHAR,
    spoonacular_recipe_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    eaten BOOLEAN DEFAULT FALSE NOT NULL,
    comment VARCHAR
);

CREATE TABLE IF NOT EXISTS diet_intolerances (
    id SERIAL PRIMARY KEY,
    intolerance VARCHAR
);

CREATE TABLE IF NOT EXISTS diet_preferences (
    id SERIAL PRIMARY KEY,
    preference VARCHAR
);
CREATE INDEX IF NOT EXISTS idx_users_login ON users(login);
CREATE INDEX IF NOT EXISTS idx_user_auth_user_id ON user_auth(user_id);
CREATE INDEX IF NOT EXISTS idx_user_auth_email ON user_auth(email);
CREATE INDEX IF NOT EXISTS idx_oauth2_accounts_user_id ON oauth2_accounts(user_id);
CREATE INDEX IF NOT EXISTS idx_health_forms_user_id ON health_forms(user_id);
CREATE INDEX IF NOT EXISTS idx_plans_user_id ON plans(user_id);
CREATE INDEX IF NOT EXISTS idx_meals_plan_id ON meals(plan_id);

-- Użytkownicy
INSERT INTO users (name, surname, login) VALUES
('Jan', 'Kowalski', 'janek'),
('Anna', 'Nowak', 'ania'),
('Piotr', 'Wiśniewski', 'piotrw');

-- Dane logowania
INSERT INTO user_auth (user_id, password, email, last_login) VALUES
(1, 'hashed_pass_jan', 'jan.kowalski@example.com', NULL),
(2, 'hashed_pass_ania', 'anna.nowak@example.com', NULL),
(3, 'hashed_pass_piotr', 'piotr.w@example.com', NULL);

-- Konta OAuth2
INSERT INTO oauth2_accounts (user_id, provider, provider_id, provider_email, access_token, refresh_token)
VALUES
(1, 'google', 'g123', 'jan.kowalski@gmail.com', 'access_tok_jan', 'refresh_tok_jan'),
(2, 'github', 'gh456', 'anna.nowak@github.com', 'access_tok_ania', 'refresh_tok_ania');

-- Formularze zdrowotne
INSERT INTO health_forms (user_id, height, weight, number_of_meals_per_day, diet_preferences, intolerances, medicament_usage)
VALUES
(1, 180, 80, 3, '["vegetarian"]', '["gluten"]', '["ibuprofen"]'),
(2, 165, 60, 4, '["low_carb"]', '[]', '[]'),
(3, 175, 75, 5, '["balanced"]', '["lactose"]', '["paracetamol"]');

-- Plany dietetyczne (maj)
INSERT INTO plans (user_id, created_by, day_start) VALUES
(1, 2, '2025-05-01'),
(2, 1, '2025-05-01'),
(3, 1, '2025-05-01');

-- Posiłki w planach
INSERT INTO meals (plan_id, meal_type, time, description, eaten, comment) VALUES
(1, 'BREAKFAST', '08:00', 'Owsianka z owocami', FALSE, NULL),
(1, 'LUNCH', '13:00', 'Kurczak z ryżem i warzywami', FALSE, NULL),
(1, 'DINNER', '19:00', 'Sałatka grecka', FALSE, NULL),

(2, 'BREAKFAST', '07:30', 'Jajecznica z pomidorami', FALSE, NULL),
(2, 'LUNCH', '12:30', 'Makaron pełnoziarnisty z pesto', FALSE, NULL),
(2, 'DINNER', '18:30', 'Zupa krem z dyni', FALSE, NULL),

(3, 'BREAKFAST', '09:00', 'Smoothie bananowo-truskawkowe', FALSE, NULL),
(3, 'LUNCH', '14:00', 'Filet z łososia + kasza jaglana', FALSE, NULL),
(3, 'DINNER', '20:00', 'Kanapki pełnoziarniste z hummusem', FALSE, NULL);

INSERT INTO diet_preferences (preference) VALUES
('Vegetarian'), ('Vegan'), ('Keto'),
('Low Carb'), ('Mediterranean'), ('Paleo');

INSERT INTO diet_intolerances (intolerance) VALUES
('Lactose'), ('Gluten'), ('Nuts'),
('Shellfish'), ('Eggs'), ('Soy');