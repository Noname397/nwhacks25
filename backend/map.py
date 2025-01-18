from flask import Blueprint, request, jsonify
import requests
import os

# Create a Blueprint for additional endpoints
additional_endpoints = Blueprint('additional_endpoints', __name__)

# Load Google API key from environment variable
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise RuntimeError("Google API key is not set. Please set the GOOGLE_API_KEY environment variable.")

# Base URL for Google Maps Directions API
GOOGLE_MAPS_API_URL = "https://maps.googleapis.com/maps/api/directions/json"

@additional_endpoints.route("/fastest-route", methods=["POST"])
def get_fastest_route():
    try:
        data = request.get_json()
        origin = data.get("origin")
        destination = data.get("destination")

        if not origin or not destination:
            return jsonify({"error": "Both 'origin' and 'destination' are required."}), 400

        modes = ["driving", "walking", "transit", "bicycling"]
        results = {}

        for mode in modes:
            response = requests.get(
                GOOGLE_MAPS_API_URL,
                params={
                    "origin": origin,
                    "destination": destination,
                    "mode": mode,
                    "key": GOOGLE_API_KEY,
                },
            )

            if response.status_code != 200:
                return jsonify({"error": f"Error fetching directions for mode {mode}: {response.text}"}), response.status_code

            data = response.json()
            if "routes" in data and data["routes"]:
                duration = data["routes"][0]["legs"][0]["duration"]["text"]
                results[mode] = duration
            else:
                results[mode] = "No route found"

        return jsonify({
            "car": results.get("driving", "No route found"),
            "walk": results.get("walking", "No route found"),
            "public_transport": results.get("transit", "No route found"),
            "bike": results.get("bicycling", "No route found"),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
