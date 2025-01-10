import os
import redis
import json
import uuid
from flask import Flask, request, g, jsonify
from threading import Thread
# from kafka import KafkaProducer
from time import sleep
from dataclasses import dataclass, field
from dataclass_wizard import JSONSerializable
from typing import Optional
from datetime import datetime
from confluent_kafka import Producer

# Configure Flask
app = Flask(__name__)

# Redis Clients
redis_client_pre_gen = redis.StrictRedis(host='redis', port=6379, db=0, decode_responses=True)  # Redis-Pre-Gen (1.5 GB)
redis_client_cache = redis.StrictRedis(host='redis', port=6379, db=1, decode_responses=True)  # Redis-Cache (1 GB)


KAFKA_BROKER = 'kafka:9092'  # Replace with your Kafka broker address
KAFKA_TOPIC = 'url_shortening_topic'  # Replace with your Kafka topic

# Initialize Kafka Producer
producer = Producer({'bootstrap.servers': KAFKA_BROKER})


# Kafka producer
# producer = KafkaProducer(bootstrap_servers=os.getenv('KAFKA_BROKER'),
#                           value_serializer=lambda v: json.dumps(v).encode('utf-8'))

# Kafka Topic
# KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'url-shortening')


@dataclass
class RequestMetadata:
    id: str = uuid.uuid4().hex  # Generating an ID for custom URLs
    user_agent: str = ''
    ip_address: str = ''
    referrer: str = ''
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

# Middleware to set request metadata before each request
@app.before_request
def set_request_metadata():
    forwarded_for = request.headers.get('X-Forwarded-For', '')
    g.request_metadata = RequestMetadata(
        user_agent=request.headers.get('User-Agent', ''),
        ip_address=forwarded_for.split(',')[0].strip() if forwarded_for else request.remote_addr,
        referrer=request.headers.get('Referer', '')
    )

@dataclass
class URLData(JSONSerializable):
    original_url: str 
    id: str = uuid.uuid4().hex  # Generating an ID for custom URLs
    display: bool = False
    clicks: int = 0
    custom_url: bool = False
    timestamp: str = datetime.utcnow().isoformat()  # ISO format timestamp
    user_agent: Optional[str] = None  # Capture the user agent string
    ip_address: Optional[str] = None  # Capture the IP address of the request
    referrer: Optional[str] = None  # Capture the referrer URL
    device_info: Optional[str] = None  # Device info extracted from headers or other methods

# Endpoint for URL shortening
@app.route('/api/shorten', methods=['POST'])
def shorten_url():
    # user_details = request.headers
    print("ENTERED !!!!!!!!!!!!!!!!")
    data = request.json
    # url_data: URLData = URLData.from_dict(data,[
    #     "user_agent": g.request_metadata.user_agent,
    #     "ip_address": g.request_metadata.ip_address,
    #     "referrer": g.request_metadata.referrer
    #    ]   )
    url_data = URLData(
    original_url=data.get('original_url'),
    display=data.get('display', False),
    user_agent=g.request_metadata.user_agent,
    ip_address=g.request_metadata.ip_address,
    referrer=g.request_metadata.referrer,
    timestamp=datetime.utcnow().isoformat(),
    device_info=data.get('device_info', '')
)
    if not url_data:
        return jsonify({"success": False, "message": "Invalid URL data"}), 400

    
    original_url = url_data.original_url
    if not original_url:
        return jsonify({"success": False, "message": "original_url is required"}), 400

    # Custom URL validation (minimum 8 characters)
    if url_data.custom_url:
        if len(original_url) < 8:
            return jsonify({"success": False, "message": "Custom URLs must be at least 8 characters long."}), 400

    # Get a pre-generated short URL from Redis-Pre-Gen (Redis-1)
    short_url = redis_client_pre_gen.spop('available_short_urls')

    if not short_url:
        return jsonify({"success": False, "message": "No available short URLs left in the pool."}), 500

    # Store the short URL in Redis Cache (Redis-2)
    redis_client_cache.set(short_url, original_url, keepttl=False)


    def background_task(url_data: URLData):
        producer.produce(KAFKA_TOPIC, url_data.to_dict())
        producer.flush()  # Ensure the message is delivered

    # Run the background task in a separate thread
    Thread(target=background_task, args=(url_data)).start()

    # Return the short URL to the user immediately . Ideally before DB save 
    response = {"success": True, "short_url": short_url}
    
    return jsonify(response), 200


# Endpoint to resolve short URLs
@app.route('/api/<short_url>', methods=['GET'])
def resolve_url(short_url):
    # First, try to get the original URL from the resolution cache (Redis-Cache)
    original_url = redis_client_cache.get(short_url)
    
    if original_url:
        return jsonify({"success": True, "original_url": original_url}), 200
    
    # If not found in the resolution cache, check Pre-Gen Redis
    original_url = redis_client_pre_gen.get(short_url)
    
    if original_url:
        return jsonify({"success": True, "original_url": original_url}), 200
    
    # If not found, return an error response
    return jsonify({"success": False, "error": "URL not found"}), 404

if __name__ == '__main__':
    print("KAFKA_BROKER:", os.getenv('KAFKA_BROKER'))
    app.run(host='0.0.0.0', port=5000, threaded=True)
