-- schema-init.sql

-- Ensure the database exists (optional if using POSTGRES_DB)
-- CREATE DATABASE yourdbname;

-- Connect to the new database
\c yourdbname;

-- Run your schema setup
CREATE TABLE urls (
    id UUID PRIMARY KEY,
    original_url TEXT NOT NULL,
    short_code VARCHAR(10) UNIQUE NOT NULL,
    display BOOLEAN DEFAULT FALSE,
    clicks INTEGER DEFAULT 0,
    custom_url BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sec_ch_ua_platform TEXT,
    sec_ch_ua TEXT,
    sec_ch_ua_mobile TEXT
);

CREATE TABLE url_clicks (
    id SERIAL PRIMARY KEY,
    url_id UUID REFERENCES urls(id) ON DELETE CASCADE,
    user_agent TEXT,
    ip_address INET,
    referrer TEXT,
    device_info TEXT,
    sec_ch_ua_platform TEXT,
    sec_ch_ua TEXT,
    sec_ch_ua_mobile TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_short_code ON urls(short_code);
CREATE INDEX idx_url_id ON url_clicks(url_id);
CREATE INDEX idx_created_at ON urls(created_at);
