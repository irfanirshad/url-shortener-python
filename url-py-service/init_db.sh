#!/bin/bash

# Run SQL queries to create tables
psql -h postgres -U postgres -d url_db <<EOF
CREATE TABLE IF NOT EXISTS urls (
    id SERIAL PRIMARY KEY,
    short_url VARCHAR(16) UNIQUE NOT NULL,
    original_url TEXT NOT NULL,
    is_custom BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS url_analytics (
    id SERIAL PRIMARY KEY,
    url_id INT NOT NULL REFERENCES urls(id),
    clicks INT DEFAULT 0,
    last_clicked_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
EOF
