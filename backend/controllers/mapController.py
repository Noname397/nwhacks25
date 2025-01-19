from flask import Blueprint, request, jsonify
import requests
import re

# Create a Blueprint for map endpoints
map_endpoints = Blueprint('map_endpoints', __name__)

# Google API Key (replace with your actual key)
GOOGLE_API_KEY = "AIzaSyCPtlKAn2duBP35t1xGaB2UCYU7AvD4p-o"

# Base URL for Google Maps Directions API
GOOGLE_MAPS_API_URL = "https://maps.googleapis.com/maps/api/directions/json"
GOOGLE_GEOLOCATION_API_URL = "https://www.googleapis.com/geolocation/v1/geolocate"

@map_endpoints.route("/transit-route", methods=["POST"])
def get_transit_route():
    return get_route("transit")

@map_endpoints.route("/car-route", methods=["POST"])
def get_car_route():
    return get_route("driving")

@map_endpoints.route("/walk-route", methods=["POST"])
def get_walk_route():
    return get_route("walking")

@map_endpoints.route("/fastest-route", methods=["POST"])
def get_fastest_route():
    try:
        # Get JSON input from the frontend
        data = request.get_json()
        origin = data.get("origin")
        destination = data.get("destination")

        # Validate input
        if not origin or not destination:
            return jsonify({"error": "Both 'origin' and 'destination' are required."}), 400

        modes = ["driving", "walking", "transit"]
        routes = []

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
                continue

            data = response.json()
            if "routes" in data and len(data["routes"]) > 0:
                route = data["routes"][0]
                duration_value = route["legs"][0]["duration"]["value"]  # In seconds
                steps = route["legs"][0]["steps"]

                routes.append({
                    "mode": mode,
                    "duration": route["legs"][0]["duration"]["text"],
                    "duration_value": duration_value,
                    "steps": format_shortened_steps(mode, steps)
                })

        # Sort routes by duration_value (fastest first)
        routes = sorted(routes, key=lambda x: x["duration_value"])

        if routes:
            return jsonify({
                "status": "success",
                "message": "Routes sorted by fastest to slowest.",
                "routes": routes
            }), 200

        return jsonify({"error": "No route found."}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def get_route(mode):
    try:
        # Get JSON input from the frontend
        data = request.get_json()
        origin = data.get("origin")
        destination = data.get("destination")

        # Validate input
        if not origin or not destination:
            return jsonify({"error": "Both 'origin' and 'destination' are required."}), 400

        # Make a request to Google Maps Directions API
        response = requests.get(
            GOOGLE_MAPS_API_URL,
            params={
                "origin": origin,
                "destination": destination,
                "mode": mode,
                "key": GOOGLE_API_KEY,
            },
        )

        # Check for API response
        if response.status_code != 200:
            return jsonify({"error": f"Failed to fetch route. {response.text}"}), response.status_code

        # Parse the response data
        data = response.json()
        if "routes" in data and len(data["routes"]) > 0:
            route = data["routes"][0]
            duration = route["legs"][0]["duration"]["text"]
            steps = route["legs"][0]["steps"]

            return jsonify({
                "status": "success",
                "message": f"{mode.capitalize()} route retrieved successfully.",
                "duration": duration,
                "steps": steps
            }), 200

        return jsonify({"error": "No route found."}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@map_endpoints.route("/polyline/<mode>", methods=["POST"])
def get_polyline(mode):
    try:
        # Get JSON input from the frontend
        data = request.get_json()
        origin = data.get("origin")
        destination = data.get("destination")

        # Validate input
        if not origin or not destination:
            return jsonify({"error": "Both 'origin' and 'destination' are required."}), 400

        # Make a request to Google Maps Directions API
        response = requests.get(
            GOOGLE_MAPS_API_URL,
            params={
                "origin": origin,
                "destination": destination,
                "mode": mode,
                "key": GOOGLE_API_KEY,
            },
        )

        # Check for API response
        if response.status_code != 200:
            return jsonify({"error": f"Failed to fetch route. {response.text}"}), response.status_code

        # Parse the response data
        data = response.json()
        if "routes" in data and len(data["routes"]) > 0:
            route = data["routes"][0]
            polyline = route["overview_polyline"]["points"]

            return jsonify({
                "status": "success",
                "message": f"Polyline for {mode} route retrieved successfully.",
                "polyline": polyline
            }), 200

        return jsonify({"error": "No route found."}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@map_endpoints.route("/my-location", methods=["POST"])
def get_my_location():
    try:
        # Make a request to Google Geolocation API
        response = requests.post(
            f"{GOOGLE_GEOLOCATION_API_URL}?key={GOOGLE_API_KEY}",
            json={"considerIp": True},
            headers={"Content-Type": "application/json"}
        )

        if response.status_code != 200:
            return jsonify({"error": f"Failed to fetch location. {response.text}"}), response.status_code

        # Return the geolocation data
        return jsonify(response.json()), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
def get_bold_tags_content(input_string):
    # Extract the first, second, and third <b> tag content
    matches = re.findall(r'<b>(.*?)</b>', input_string)
    direction = matches[0] if len(matches) > 0 else None
    from_road = matches[1] if len(matches) > 1 else None
    to_road = matches[2] if len(matches) > 2 else None
    return {
        "direction": direction,
        "from_road": from_road,
        "to_road": to_road
    }

def get_first_with_three_bold(input_string):
    # Match substrings with exactly three <b>...</b> tags
    matches = re.findall(r'(?:<b>.*?</b>.*?){3}', input_string)
    return matches[0] if matches else None

def format_shortened_steps(mode, steps):
    if mode == "transit":
        summary = []
    
        for step in steps:
            travel_mode = step.get("travel_mode", "").upper()
            if travel_mode == "WALKING":
                # Add walking duration
                duration_text = step.get("duration", {}).get("text", "")
                summary.append(f"walking: {duration_text}")
            elif travel_mode == "TRANSIT":
                # Add transit details
                transit_details = step.get("transit_details", {})
                line_info = transit_details.get("line", {})
                # Determine if short_name or name is used
                short_name = line_info.get("short_name")
                name = line_info.get("name", "unknown line")
                
                if short_name:
                    line_name = f"bus ({short_name})"
                else:
                    line_name = f"train ({name})"
                
                duration_text = step.get("duration", {}).get("text", "")
                summary.append(f"{line_name}: {duration_text}")
        return summary

    elif mode in ["driving", "walking"]:
        for step in steps:
            # Get the first step with three bold tags
            html_instructions = step.get("html_instructions", "")
            first_with_three_bold = get_first_with_three_bold(html_instructions)
            if first_with_three_bold:
                return get_bold_tags_content(first_with_three_bold)
    return []
