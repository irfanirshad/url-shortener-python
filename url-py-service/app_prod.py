import os
import redis
import uuid
from flask import Flask, request, g, jsonify, redirect, current_app
from threading import Thread
import time
from dataclasses import dataclass, field
from dataclass_wizard import JSONSerializable
from typing import Optional
from datetime import datetime
from confluent_kafka import Producer
import json
import logging
from flask_cors import CORS
from urllib.parse import urlparse
import psycopg2
from psycopg2 import sql
import html
import re
from redis.exceptions import ConnectionError, AuthenticationError, TimeoutError, RedisError

from flask_socketio import SocketIO, emit

from db.pg_connector import get_from_database
from validations import is_valid_url, is_valid_url_cache

# LOGGING
logging.basicConfig(level=logging.DEBUG)
logging.debug("Debug message")

# Environment variables for Redis connection
REDIS_PC = os.getenv('REDIS_PC')
REDIS_URL = os.getenv('REDIS_URL')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', 'Welcome@Inf0r')  
REDIS_PORT_CACHE = 6379
REDIS_PORT_PRE_GEN = 6379
REDIS_DB = 0

# Environment variablesW
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'url-shortening')
KAFKA_BROKER = os.getenv('KAFKA_BROKER')
DB_HOST = os.getenv('DB_HOST')
DB_NAME = "yourdbname"
DB_USER = "yourusername"
DB_PASSWORD = "yourpassword"
DB_PORT = 5432
URL_LENGTH_MAX = 8

# Redis Clients - Connection pools
redis_pool_pre_gen = redis.ConnectionPool(
    host=REDIS_URL,
    port=REDIS_PORT_PRE_GEN,
    password=REDIS_PASSWORD,
    db=REDIS_DB,
    max_connections=10,
    socket_timeout=5,
    socket_connect_timeout=5,
    decode_responses=True,
)

redis_pool_cache = redis.ConnectionPool(
    host=REDIS_PC,
    port=REDIS_PORT_CACHE,
    password=REDIS_PASSWORD,
    db=REDIS_DB,
    max_connections=10,
    socket_timeout=5,
    socket_connect_timeout=5,
    decode_responses=True,
)

# Global Redis client variables
redis_client_pre_gen = None
redis_client_cache = None

def initialize_redis_client(pool):
    """Initialize a Redis client with retries and error handling"""
    retries = 3
    delay = 2  # seconds
    
    for attempt in range(retries):
        try:
            redis_client = redis.Redis(connection_pool=pool)
            if redis_client.ping():
                print("Connected to Redis!")
                return redis_client
            else:
                print("Failed to connect to Redis.")

        except AuthenticationError:
            print("Redis authentication failed. Check your password.")
            break
        except ConnectionError:
            print(f"Redis connection failed. Retrying in {delay} seconds... (Attempt {attempt + 1}/{retries})")
            time.sleep(delay)
        except TimeoutError:
            print(f"Redis connection timed out. Retrying in {delay} seconds... (Attempt {attempt + 1}/{retries})")
            time.sleep(delay)
        except Exception as e:
            print(f"Unexpected error connecting to Redis: {e}")
            break

    print("Failed to initialize Redis after multiple attempts.")
    return None

def init_redis_clients():
    """Initialize Redis clients"""
    global redis_client_pre_gen, redis_client_cache
    
    if redis_client_pre_gen is None:
        redis_client_pre_gen = initialize_redis_client(redis_pool_pre_gen)
    
    if redis_client_cache is None:
        redis_client_cache = initialize_redis_client(redis_pool_cache)
    
    if not redis_client_pre_gen or not redis_client_cache:
        logging.error("Redis initialization failed.")
        raise RuntimeError("Redis initialization failed.")
    
    return redis_client_pre_gen, redis_client_cache

# Initialize Redis clients immediately when module loads
try:
    init_redis_clients()
    logging.info("Redis clients initialized successfully")
except Exception as e:
    logging.error(f"Failed to initialize Redis clients: {e}")
    # Don't raise here - let the app start and handle errors in endpoints

# Configure Flask
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins=["https://www.bigshort.one", "https://bigshort.one", "http://localhost:4173"])

CORS(app, resources={
    r"/*": {
        "origins": ["https://www.bigshort.one", "https://bigshort.one", "http://localhost:4173"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    },
})

# Kafka Topic
producer = Producer({'bootstrap.servers': KAFKA_BROKER}) if KAFKA_BROKER else None

# Connect to the Postgres Database
def get_db_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

@dataclass
class RequestMetadata:
    user_agent: str = ''
    ip_address: str = ''
    referrer: str = ''
    sec_ch_ua_platform: str = ''
    sec_ch_ua: str = ''
    sec_ch_ua_mobile: str = ''

# Middleware to set request metadata before each request
@app.before_request
def set_request_metadata():
    forwarded_for = request.headers.get('X-Forwarded-For', '')
    g.request_metadata = RequestMetadata(
        user_agent=request.headers.get('User-Agent', ''),
        ip_address=forwarded_for.split(',')[0].strip() if forwarded_for else request.remote_addr,
        referrer=request.headers.get('Referer', ''),
        sec_ch_ua_platform=request.headers.get('sec-ch-ua-platform', ''),
        sec_ch_ua=request.headers.get('sec-ch-ua', ''),
        sec_ch_ua_mobile=request.headers.get('sec-ch-ua-mobile', '')
    )

@dataclass
class URLData(JSONSerializable):
    url: str = ""
    short_url: str = ""
    is_public: bool = False
    clicks: int = 0
    custom_url: bool = False
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    referrer: Optional[str] = None
    device_info: Optional[str] = None
    sec_ch_ua_platform: Optional[str] = None
    sec_ch_ua: Optional[str] = None
    sec_ch_ua_mobile: Optional[str] = None

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify Redis connections"""
    try:
        # Check if Redis clients are available
        if redis_client_pre_gen is None or redis_client_cache is None:
            return jsonify({"status": "unhealthy", "error": "Redis clients not initialized"}), 503
        
        # Test Redis connections
        redis_client_pre_gen.ping()
        redis_client_cache.ping()
        
        return jsonify({"status": "healthy", "redis": "connected"}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 503

# Endpoint for URL shortening
@app.route('/api/v1/shorten', methods=['POST'])
def shorten_url():
    # Check if Redis clients are available
    if redis_client_pre_gen is None:
        logging.error("Redis pre-gen client not available")
        return jsonify({"success": False, "message": "Service temporarily unavailable"}), 503
    
    if redis_client_cache is None:
        logging.error("Redis cache client not available")
        return jsonify({"success": False, "message": "Service temporarily unavailable"}), 503
    
    data = request.json
    url_data: URLData = URLData.from_dict(data)
    
    if not url_data:
        return jsonify({"success": False, "message": "Invalid URL data"}), 400

    # Populate additional fields from request metadata
    url_data.user_agent = g.request_metadata.user_agent
    url_data.ip_address = g.request_metadata.ip_address
    url_data.referrer = g.request_metadata.referrer
    url_data.sec_ch_ua_platform = g.request_metadata.sec_ch_ua_platform
    url_data.sec_ch_ua = g.request_metadata.sec_ch_ua
    url_data.sec_ch_ua_mobile = g.request_metadata.sec_ch_ua_mobile
    
    original_url = url_data.url
    is_valid, error_message = is_valid_url(original_url)
    if not is_valid:
        return jsonify({"success": False, "message": error_message}), 400
    
    if not original_url:
        return jsonify({"success": False, "message": "original_url is required"}), 400

    if url_data.custom_url:
        if len(original_url) < 8:
            return jsonify({"success": False, "message": "Custom URLs must be at least 8 characters long."}), 400

    try:
        redis_url = redis_client_pre_gen.lpop('short_urls')
    except Exception as e:
        logging.error(f"Redis pre-gen error: {e}")
        return jsonify({"success": False, "message": "Service temporarily unavailable"}), 503

    short_url = f"www.bigshort.one/{redis_url}"

    if not redis_url:
        return jsonify({"success": False, "message": "No available short URLs left in the pool."}), 500

    # Store the mapping in Redis (defensive operation)
    try:
        redis_client_cache.set(redis_url, html.escape(original_url), keepttl=False)
    except Exception as e:
        logging.error(f"Failed to store URL mapping in Redis: {e}")
        return jsonify({"success": False, "message": "Internal server error"}), 500
    
    url_data.short_url = redis_url

    def save_to_db(url_data_dict: dict):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            insert_query = sql.SQL("""
                INSERT INTO urls (id, original_url, short_code, display, clicks, custom_url, created_at, 
                sec_ch_ua_platform, sec_ch_ua, sec_ch_ua_mobile)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """)
            cursor.execute(insert_query, (
                url_data_dict['id'],
                url_data_dict['url'],
                url_data_dict['shortUrl'],
                url_data_dict['isPublic'],
                url_data_dict['clicks'],
                url_data_dict['customUrl'],
                url_data_dict['createdAt'],
                url_data_dict['secChUaPlatform'],
                url_data_dict['secChUa'],
                url_data_dict['secChUaMobile']
            ))
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            logging.error(f"Database error: {str(e)}")
    
    url_data_dict = url_data.to_dict(skip_defaults=False)
    logging.info(f"URL INFO ==> {url_data_dict}")
    save_to_db(url_data_dict)
    
    response = {"success": True, "shortUrl": short_url}
    
    return jsonify(response), 200

@app.route('/<short_url>', methods=['GET'])
def resolve_url(short_url):
    logging.info(f"ENTERED REDIRECT +++++++++++++++++---> {short_url}")
    
    # Check if Redis cache client is available
    if redis_client_cache is None:
        logging.error("Redis cache client not available")
        return jsonify({"success": False, "message": "Service temporarily unavailable"}), 503
    
    is_valid, error_message = is_valid_url_cache(short_url)
    if not is_valid:
        return jsonify({"success": False, "message": error_message}), 400
    
    if not short_url:
        return jsonify({"success": False, "message": "short_url is required"}), 400

    # First, split out the short_url from the bigshort.one/<short_url>
    short_url_key = short_url.split("/")[-1]
    logging.info(f"Trying to get the cache --- {short_url_key}")
    
    try:
        if redis_client_cache.exists(short_url_key):
            logging.info(f"CACHE - Found")
            original_url = redis_client_cache.get(short_url_key)
            logging.info(f"Type of original_url: {type(original_url)}")
            logging.info(f"Value found: {original_url}")
        else:
            logging.info("Key not found in cache!")
            original_url = None
    except Exception as e:
        logging.error(f"Redis cache error: {e}")
        original_url = None
    
    logging.info(f"URL retrieved? short url ==> {short_url_key} and original url ==> {original_url}")
    
    if original_url:
        return redirect(html.unescape(original_url), code=302)
    
    # If not found in the redis cache, check the DB 
    original_url = get_from_database(short_url_key)
    logging.info(f"We found this from DB!! ==> {original_url}")
    
    if original_url:
        # Update cache with new TTL
        try:
            redis_client_cache.setex(short_url_key, 3600, original_url)  # 1 hour TTL
        except Exception as e:
            logging.error(f"Failed to update cache: {e}")
        
        logging.info(f"Redirecting to url {original_url}")
        return redirect(original_url, code=302)
    
    return jsonify({"success": False, "message": "URL not found"}), 404

@app.route('/api/v1/urls', methods=['GET'])
def fetch_url_list():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Query to fetch the last 100 URLs based on creation date
        fetch_query = """
            SELECT * 
            FROM urls 
            ORDER BY created_at DESC
            LIMIT 100;
        """
        cursor.execute(fetch_query)
        rows = cursor.fetchall()
        
        urls = []
        for row in rows:
            url_data = {
                'id': row[0],
                'original_url': row[1],
                'short_code': f"www.bigshort.one/{row[2]}",
                'clicks': row[4],
                'created_at': row[6].isoformat()
            }
            urls.append(url_data)
        
        cursor.close()
        conn.close()
        
        return jsonify({"success": True, "urls": urls}), 200
    
    except Exception as e:
        logging.error(f"Database error: {str(e)}")
        return jsonify({"success": False, "message": "Error fetching URLs."}), 500

def send_time_ticks():
    while True:
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        socketio.emit('push-message', {'time': current_time})
        socketio.sleep(3)
        
@socketio.on('connect')
def handle_connect():
    logging.info('Client connected')
    emit('connection-response', {'status': 'connected'})
    socketio.start_background_task(send_time_ticks)

@socketio.on('disconnect')
def handle_disconnect():
    logging.info('Client disconnected')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)