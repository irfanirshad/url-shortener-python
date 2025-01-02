from flask import Flask, request, jsonify
from flask_cors import CORS
import redis
import psycopg2
import os
import logging
from gevent import monkey
from gevent.pywsgi import WSGIServer

# Apply monkey patching for gevent
monkey.patch_all()

# Flask App Initialization
app = Flask(__name__)
CORS(app)

# Logger Configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Environment Variables for Redis and PostgreSQL
REDIS_1_HOST = os.getenv('REDIS1_HOST', 'redis1')
REDIS_2_HOST = os.getenv('REDIS2_HOST', 'redis2')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'postgres')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'url_db')
POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'password')
POSTGRES_PORT = int(os.getenv('POSTGRES_PORT', 5432))

# Redis Connections
redis_1 = redis.Redis(host=REDIS_1_HOST, port=REDIS_PORT, db=1)
redis_2 = redis.Redis(host=REDIS_2_HOST, port=REDIS_PORT, db=2)

# PostgreSQL Connection
def get_postgres_connection():
    return psycopg2.connect(
        host=POSTGRES_HOST,
        database=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        port=POSTGRES_PORT
    )

# Routes
@app.route('/shorten', methods=['POST'])
def shorten_url():
    data = request.json
    original_url = data.get('original_url')
    custom_url = data.get('custom_url')

    if not original_url:
        return jsonify({'error': 'Original URL is required.'}), 400

    # Custom URL Logic
    if custom_url:
        if len(custom_url) < 8 or len(custom_url) > 16:
            return jsonify({'error': 'Custom URLs must be between 8 and 16 characters long.'}), 400
        if redis_1.exists(custom_url) or redis_2.exists(custom_url):
            return jsonify({'error': 'Custom URL already exists.'}), 409

        # Store custom URL in DB and cache in Redis-1
        save_url_to_db(original_url, custom_url, True)
        redis_1.set(custom_url, original_url)
        logger.info(f"Custom URL created: {custom_url} -> {original_url}")
        return jsonify({'short_url': custom_url}), 201

    # Default URL Logic (7 chars)
    short_url = generate_default_short_url()
    if not short_url:
        return jsonify({'error': 'No pre-generated URLs available.'}), 503
    redis_2.delete(short_url)  # Evict from Redis-2 after use
    redis_1.set(short_url, original_url)  # Cache in Redis-1
    save_url_to_db(original_url, short_url, False)
    logger.info(f"Pre-generated URL used: {short_url} -> {original_url}")
    return jsonify({'short_url': short_url}), 201

@app.route('/<short_url>', methods=['GET'])
def resolve_url(short_url):
    # Check in Redis-1
    original_url = redis_1.get(short_url)
    if original_url:
        update_clicks_in_db(short_url)
        return jsonify({'original_url': original_url.decode()}), 200

    # Check in PostgreSQL
    try:
        with get_postgres_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT original_url FROM urls WHERE short_url = %s", (short_url,))
                result = cursor.fetchone()
                if result:
                    original_url = result[0]
                    redis_1.set(short_url, original_url)  # Cache in Redis-1
                    update_clicks_in_db(short_url)
                    return jsonify({'original_url': original_url}), 200
    except Exception as e:
        logger.error(f"Error querying PostgreSQL: {e}")
        return jsonify({'error': 'Internal server error.'}), 500

    logger.warning(f"URL not found: {short_url}")
    return jsonify({'error': 'URL not found.'}), 404

def generate_default_short_url():
    # Generate a 7-character default short URL
    short_url = ''.join(random.choices(string.ascii_letters + string.digits, k=7))
    return short_url

def save_url_to_db(original_url, short_url, is_custom):
    try:
        with get_postgres_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO urls (short_url, original_url, is_custom) 
                    VALUES (%s, %s, %s)
                """, (short_url, original_url, is_custom))
                conn.commit()
    except Exception as e:
        logger.error(f"Error saving URL to DB: {e}")

def update_clicks_in_db(short_url):
    try:
        with get_postgres_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id FROM urls WHERE short_url = %s", (short_url,))
                result = cursor.fetchone()
                if result:
                    url_id = result[0]
                    cursor.execute("SELECT clicks FROM url_analytics WHERE url_id = %s", (url_id,))
                    clicks = cursor.fetchone()
                    if clicks:
                        cursor.execute("UPDATE url_analytics SET clicks = clicks + 1, last_clicked_at = CURRENT_TIMESTAMP WHERE url_id = %s", (url_id,))
                    else:
                        cursor.execute("INSERT INTO url_analytics (url_id, clicks) VALUES (%s, 1)", (url_id,))
                    conn.commit()
    except Exception as e:
        logger.error(f"Error updating click count in DB: {e}")

if __name__ == '__main__':
    http_server = WSGIServer(('0.0.0.0', 5000), app)
    logger.info("Starting Gevent WSGI Server on port 5000...")
    http_server.serve_forever()
