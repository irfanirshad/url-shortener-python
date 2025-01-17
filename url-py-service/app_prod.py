import os
import redis
import uuid
from flask import Flask, request, g, jsonify, redirect
from threading import Thread
from time import sleep
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
from redis.exceptions import RedisError




from db.pg_connector import get_from_database
from validations import is_valid_url

# LOGGING
logging.basicConfig(level=logging.DEBUG)
logging.debug("Debug message")


# Environment variables
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'url-shortening')
REDIS_URL = os.getenv('REDIS_URL')
REDIS_PC = os.getenv('REDIS_PC')
KAFKA_BROKER = os.getenv('KAFKA_BROKER')
DB_HOST=os.getenv('DB_HOST')
DB_NAME="yourdbname"
DB_USER="yourusername"
DB_PASSWORD="yourpassword"
DB_PORT=5432
URL_LENGTH_MAX = 8


# Configure Flask
app = Flask(__name__)



# CORS(app, resources={
#     r"/api/v1/*": {
#         "origins": ["https://www.bigshort.one", "https://bigshort.one", "http://localhost:4173"],
#         "methods": ["GET", "POST", "OPTIONS"],
#         "allow_headers": ["Content-Type", "Accept", "Accept-Language", 
#                          "Origin", "Referer", "Sec-Ch-Ua", "Sec-Ch-Ua-Mobile", 
#                          "Sec-Ch-Ua-Platform", "User-Agent"],
#         # "supports_credentials": False
#     },
#     r"/<short_url>": {
#         "origins": "*",  # Temporary for testing
#         "methods": ["GET", "OPTIONS"],
#         "allow_headers": ["Content-Type", "Authorization"],
#         "supports_credentials": False
#     }
# })


CORS(app, resources={
    r"/api/*": {
        "origins": ["https://www.bigshort.one", "https://bigshort.one", "http://localhost:4173"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# Redis Clients
redis_client_pre_gen = redis.StrictRedis(host=REDIS_URL, port=6380, db=0, decode_responses=True)  # Redis-Pre-Gen (1.5 GB)
redis_client_cache = redis.StrictRedis(host=REDIS_PC, port=6379, db=0, decode_responses=True)  # Redis-Cache (1 GB)

# Kafka Topic
producer = Producer({'bootstrap.servers': KAFKA_BROKER})


# Connect to the Postgres Database
def get_db_connection():
    return psycopg2.connect(
        dbname=DB_NAME,  # yourdbname
        user=DB_USER,    # yourusername
        password=DB_PASSWORD,  # yourpassword
        host=DB_HOST,  # localhost or the correct host
        port=DB_PORT  # 5432
    )


@dataclass
class RequestMetadata:
    # id: str =  field(default_factory=uuid.uuid4().hex)  # Generating an ID for custom URLs
    user_agent: str = ''
    ip_address: str = ''
    referrer: str = ''
    sec_ch_ua_platform: str = ''  # Capture the sec-ch-ua-platform header
    sec_ch_ua: str = ''           # Capture the sec-ch-ua header
    sec_ch_ua_mobile: str = ''    # Capture the sec-ch-ua-mobile header
    # created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())



# Middleware to set request metadata before each request
@app.before_request
def set_request_metadata():
    # if not request.is_json:
    #     return jsonify({"error": "Content-Type must be application/json"}), 415
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
    created_at: str = datetime.utcnow().isoformat()
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    referrer: Optional[str] = None
    device_info: Optional[str] = None
    sec_ch_ua_platform: Optional[str] = None
    sec_ch_ua: Optional[str] = None
    sec_ch_ua_mobile: Optional[str] = None



# Endpoint for URL shortening
@app.route('/api/v1/shorten', methods=['POST'])
def shorten_url():
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

    redis_url = redis_client_pre_gen.lpop('short_urls')
    short_url =  f"www.bigshort.one/{redis_url}"
    # return jsonify({"success": False, "message": f"Redis error: {str(e)}"}), 500

    if not redis_url:
        return jsonify({"success": False, "message": "No available short URLs left in the pool."}), 500 # TODO: Later Handle

    # redis_client_cache.set(redis_url, original_url, keepttl=False)
    redis_client_cache.set(redis_url, html.escape(original_url), keepttl=False)

    url_data.short_url = redis_url

    # def background_task(url_data_dict: dict):
    #     url_data_json = json.dumps(url_data_dict).encode('utf-8')
    #     producer.produce(KAFKA_TOPIC, url_data_json)
    #     producer.flush()  

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
                # url_data_dict
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
    
    # t = Thread(target=save_to_db, args=(url_data_dict,))
    # t = Thread(target=background_task, args=(url_data_dict,))
    # t.start()
    
    response = {"success": True, "shortUrl": short_url}
    
    return jsonify(response), 200


@app.route('/api/<short_url>', methods=['GET'])
def resolve_url(short_url):
    # First, split out the short_url from the bigshort.one/<short_url>
    short_url = short_url.split("/")[-1]

    # short_url = short_url.strip()[:50]  # Limit length
    if not re.match(r'^[a-zA-Z0-9-_]+$', short_url) or len(short_url) > URL_LENGTH_MAX:
        return jsonify({"success": False, "error": "Invalid URL format"}), 400

    
    # Second, try to get the original URL from the resolution cache (Redis-Cache)
    if redis_client_cache.exists(short_url):
        original_url = redis_client_cache.get(short_url)
        logging.info(f"Value found: {original_url}", original_url, logging.INFO)
    else:
        logging.info("Key not found!")
    original_url = redis_client_cache.get(short_url)
    
    logging.info(f"URL retrived ? short url ==> {short_url} and original url ==> {original_url}")
    
    if original_url:
        return jsonify({"success": True, "original_url": original_url}), 200
    
    # If not found in the redis cache, check the DB 
    original_url = get_from_database(short_url)
    logging.info(f"We found this !! ==> {original_url}")
    if original_url:
        # Update cache with new TTL
        try:
            redis_client_cache.setex(
                short_url,
                3600,  # 1 hour TTL
                original_url
            )
        except RedisError as e:
            logging.error(f"Cache update failed: {str(e)}")
        logging.info("Redirecting !!!!!!!!!!!! to url {}")
        return redirect(original_url, code=302)
    
    # If not found, return an error response
    return jsonify({"success": False, "error": "URL not found"}), 404



@app.route('/api/v1/urls', methods=['GET'])
def fetch_url_list():
    # fetch the last 1000 urls. No pagination
    # Will add more functionality like sort based on clicks 
    # Hit this endpoint again with the mentioened filters. Eg: Use a query to know this beforehand
    # SQL call to index to fetch last 1000 created URLs
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Query to fetch the last 1000 URLs based on creation date
        fetch_query = """
            SELECT * 
            FROM urls 
            ORDER BY created_at DESC
            LIMIT 100;
        """
        cursor.execute(fetch_query)
        rows = cursor.fetchall()
        
        urls = []
        # rows = list(rows)
        for row in rows:
            url_data = {
                'id': row[0],
                'original_url': row[1],
                'short_code': f"www.bigshort.one/{row[2]}",
                # 'display': row[3],
                'clicks': row[4],
                # 'custom_url': row[5],
                'created_at': row[6].isoformat()
            }
            urls.append(url_data)
        
        # logging.info(f"URLS fetched from DB => {urls}")
        cursor.close()
        conn.close()
        
        return jsonify({"success": True, "urls": urls}), 200
    
    except Exception as e:
        logging.info(f"Database error: {str(e)}")
        return jsonify({"success": False, "message": "Error fetching URLs."}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
