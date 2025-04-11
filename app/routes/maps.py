import os
import requests
import redis
import json
from flask import Blueprint, request, jsonify
from dotenv import load_dotenv

load_dotenv()

map_bp = Blueprint("map", __name__)

GOMAPS_API_BASE = "https://maps.gomaps.pro/maps/api"
GOMAPS_API_KEY = os.getenv("GOOGLE_API_KEY")

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=0,
    decode_responses=True
)

@map_bp.route("/search_place_details", methods=["GET"])
def search_place_details():
    input_text = request.args.get("query")

    if not input_text:
        return jsonify({"error": "query param is required"}), 400

    cache_key = f"place_details:{input_text.lower()}"

    # Step 0: Check Redis cache
    cached_data = redis_client.get(cache_key)
    if cached_data:
        return jsonify(json.loads(cached_data)), 200

    try:
        # Step 1: Get place_id
        find_place_url = f"{GOMAPS_API_BASE}/place/findplacefromtext/json"
        find_place_params = {
            "input": input_text,
            "inputtype": "textquery",
            "key": GOMAPS_API_KEY,
        }
        place_response = requests.get(find_place_url, params=find_place_params, timeout=5)
        place_data = place_response.json()

        if place_data.get("status") != "OK" or not place_data.get("candidates"):
            return jsonify({"error": "No place found"}), 404

        place_id = place_data["candidates"][0]["place_id"]

        # Step 2: Get full details using place_id
        details_url = f"{GOMAPS_API_BASE}/place/details/json"
        details_params = {
            "place_id": place_id,
            "key": GOMAPS_API_KEY,
        }
        details_response = requests.get(details_url, params=details_params, timeout=5)
        details_data = details_response.json()

        # Step 3: Store in Redis cache (set expiry 1 hour = 3600 sec)
        redis_client.set(cache_key, json.dumps(details_data), ex=3600)

        return jsonify(details_data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
