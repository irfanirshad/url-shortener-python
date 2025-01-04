-- Table to store URL metadata
CREATE TABLE url_metadata (
    id SERIAL PRIMARY KEY,
    short_url VARCHAR(6) NOT NULL UNIQUE,
    long_url TEXT NOT NULL,
    click_count INT DEFAULT 0,
    display_on_dashboard BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table to store click logs for URLs
CREATE TABLE click_logs (
    id SERIAL PRIMARY KEY,
    short_url VARCHAR(6) NOT NULL,
    clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (short_url) REFERENCES url_metadata (short_url)
);

-- Index for the most recent URLs (optional)
CREATE INDEX idx_recent_urls ON url_metadata (created_at DESC);
