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
    day_start DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS meals (
    id SERIAL PRIMARY KEY,
    plan_id INTEGER NOT NULL REFERENCES plans(id) ON DELETE CASCADE,
    meal_type VARCHAR,
    time TIME NOT NULL,
    description VARCHAR,
    eaten BOOLEAN DEFAULT FALSE NOT NULL,
    comment VARCHAR
);
CREATE INDEX IF NOT EXISTS idx_users_login ON users(login);
CREATE INDEX IF NOT EXISTS idx_user_auth_user_id ON user_auth(user_id);
CREATE INDEX IF NOT EXISTS idx_user_auth_email ON user_auth(email);
CREATE INDEX IF NOT EXISTS idx_oauth2_accounts_user_id ON oauth2_accounts(user_id);
CREATE INDEX IF NOT EXISTS idx_health_forms_user_id ON health_forms(user_id);
CREATE INDEX IF NOT EXISTS idx_plans_user_id ON plans(user_id);
CREATE INDEX IF NOT EXISTS idx_meals_plan_id ON meals(plan_id);