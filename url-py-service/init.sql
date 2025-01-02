CREATE TABLE urls (
    id SERIAL PRIMARY KEY,
    short_url VARCHAR(255) UNIQUE NOT NULL,
    original_url TEXT NOT NULL
);
