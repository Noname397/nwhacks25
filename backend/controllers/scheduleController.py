import re

from flask import Blueprint, request, jsonify, current_app
from bson import ObjectId
# from backend.models.schedule import schedule_schema, schedules_schema

import pandas as pd
from datetime import datetime

LOC_ABB = {
  "ALRD": "1822 East Mall",
  "ANSO": "6303 North West Marine Drive",
  "AERL": "2202 Main Mall",
  "ACEN": "1871 West Mall",
  "AUDX": "1924 West Mall",
  "BINN": "6373 University Boulevard",
  "BIOL": "6270 University Boulevard",
  "BUCH": "1866 Main Mall",
  "BUTO": "1873 East Mall",
  "CCM": "4145 Wesbrook Mall",
  "CIRS": "2260 West Mall",
  "CHAN": "6265 Crescent Road",
  "GUNN": "2553 Wesbrook Mall",
  "CHBE": "2360 East Mall V6T 1Z3",
  "CHEM": "2036 Main Mall",
  "CEME": "6250 Applied Science Lane",
  "MINL": "2332 West Mall",
  "COPP": "2146 Health Sciences Mall",
  "DLAM": "2033 Main Mall V6T 1Z2",
  "DSOM": "6361 University Blvd",
  "KENN": "2136 West Mall",
  "EOS": "6339 Stores Road",
  "ESB": "2207 Main Mall",
  "ESC": "2335 Engineering Road",
  "FNH": "2205 East Mall",
  "FSC": "2424 Main Mall",
  "FORW": "6350 Stores Road",
  "LASR": "6333 Memorial Road",
  "FRWO": "6354 Crescent Road",
  "FRDM": "2177 Wesbrook Mall V6T 1Z3",
  "GEOG": "1984 West Mall",
  "CUNN": "2146 East Mall",
  "HEBB": "2045 East Mall",
  "HENN": "6224 Agricultural Road",
  "ANGU": "2053 Main Mall",
  "DMP": "6245 Agronomy Road V6T 1Z4",
  "IRSC": "1985 Learners' Walk",
  "ICCS": "2366 Main Mall",
  "IBLC": "1961 East Mall V6T 1Z1",
  "MCDN": "2199 West Mall",
  "SOWK": "2080 West Mall",
  "LAX": "2371 Main Mall",
  "LSK": "6356 Agricultural Road",
  "PARC": "6049 Nurseries Road",
  "LSC": "2350 Health Sciences Mall",
  "MCLD": "2356 Main Mall",
  "MCML": "2357 Main Mall",
  "MATH": "1984 Mathematics Road",
  "MATX": "1986 Mathematics Road",
  "MEDC": "2176 Health Sciences Mall",
  "MSL": "2185 East Mall",
  "MUSC": "6361 Memorial Road",
  "SCRF": "2125 Main Mall",
  "AUDI": "6344 Memorial Road",
  "IRC": "2194 Health Sciences Mall",
  "PHRM": "2405 Wesbrook Mall",
  "PONE": "2034 Lower Mall",
  "PONF": "2008 Lower Mall",
  "OSB2": "6108 Thunderbird Boulevard",
  "SRC": "6000 Student Union Blvd",
  "BRIM": "2355 East Mall",
  "UCEN": "6331 Crescent Road V6T 1Z1",
  "TFPB": "6358 University Blvd, V6T 1Z4",
  "YURT": "3465 Ross Drive",
  "KPAV": "2211 Wesbrook Mall",
  "MGYM": "6081 University Blvd",
  "EDC": "2345 East Mall",
  "WESB": "6174 University Boulevard",
  "WMAX": "1933 West Mall",
  "SWNG": "2175 West Mall V6T 1Z4"
}
# Create a Blueprint for schedule routes
schedule_blueprint = Blueprint('schedules', __name__)

def serialize_doc(document):
    """
    Convert a MongoDB document into a JSON-serializable dict,
    converting the ObjectId to a string.
    """
    document['_id'] = str(document['_id'])
    return document

@schedule_blueprint.route('/excel', methods=['POST'])
def upload_excel():
    """
    POST /schedules/excel
    
    This endpoint expects a file input named 'excel_file' in the form-data.
    Example form-data (using Postman or similar):
       Key:   excel_file
       Type:  File
       Value: [Select your .xlsx or .xls file]

    We only validate that the file is provided and that its extension looks like an Excel file.
    Actual file processing (parsing, saving to DB, etc.) should go in a separate helper function.
    """
    # 1. Check if 'excel_file' is in the request
    if 'excel_file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['excel_file']

    # 2. Validate the file name
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # 3. (Optional) Basic extension check for .xls or .xlsx
    if not (file.filename.endswith('.xls') or file.filename.endswith('.xlsx')):
        return jsonify({"error": "File does not appear to be an Excel file"}), 400

    # 4. Pass the file to a helper function for further processing (to be implemented later)
    parse_excel_file(file)

    return jsonify({"message": "File received. Processing will happen in a helper function."}), 200


@schedule_blueprint.route('/next-class', methods=['GET'])
def next_class():
    """
    GET schedules/next-class
    Returns the next upcoming class based on the current time.
    """
    classes_list = next_class_helper()
    if classes_list == "error":
        return jsonify({"error": str(e)}), 500
    elif classes_list:
        return jsonify(classes_list), 200
    else:
        return jsonify({"message": "No classes scheduled for today"}), 200

def next_class_helper():
    """
    GET schedules/next-class
    Returns the next upcoming class based on the current time.
    """
    try:
        db = current_app.config['DB']  # Get MongoDB database instance
        schedule_collection = db["schedules"]  # Access schedule collection

        # Get today's date and weekday
        today_date = datetime.now().strftime("%Y-%m-%d")  # YYYY-MM-DD format
        today_weekday = datetime.now().strftime("%a")  # Short weekday format (Mon, Tue, etc.)

        # Query: Find classes where today is within the date range AND today is in the "days" list
        classes_today = schedule_collection.find_one(
            {
                "start_date": {"$lte": today_date},  # start_date <= today
                "end_date": {"$gte": today_date},  # end_date >= today
                "days": today_weekday  # Check if today is in the list of scheduled days
            },
            sort=[("class_time", 1)]  # Sort by class_time (earliest first)
        )

        classes_list = [{
            "class_name": c["class_name"],
            "class_time": c["class_time"],
            "location": c["location"],
            "address": c["address"],
            "room": c["room"]
        } for c in classes_today]

        return classes_list

    except Exception as e:
        return f"error: {e}"

@schedule_blueprint.route('/today', methods=['GET'])
def today_schedule():
    """
    GET /schedules/today
    Returns all classes scheduled for today, sorted by time.
    """
    try:
        db = current_app.config['DB']  # Get MongoDB database instance
        schedule_collection = db["schedules"]  # Access schedule collection

        # Get today's date and weekday
        today = datetime.now()
        today_date = today.strftime("%Y-%m-%d")  # YYYY-MM-DD format
        today_weekday = today.now().strftime("%a")  # Short weekday format (Mon, Tue, etc.)

        # Query: Find classes where today is within the date range AND today is in the "days" list
        classes_today = schedule_collection.find(
            {
                "start_date": {"$lte": today_date},  # start_date <= today
                "end_date": {"$gte": today_date},    # end_date >= today
                "days": today_weekday                # Check if today is in the list of scheduled days
            },
            sort=[("class_time", 1)]  # Sort by class_time (earliest first)
        )

        classes_list = [{
            "class_name": c["class_name"],
            "class_time": c["class_time"],
            "location": c["location"],
            "address": c["address"],
            "room": c["room"]
        } for c in classes_today]

        if classes_list:
            return jsonify(classes_list), 200
        return jsonify({"message": "No classes scheduled for today"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def parse_meeting_pattern(pattern_chunk):
    """
    Given one chunk of meeting pattern text, e.g.:
      "2025-01-06 - 2025-02-14 | Mon Wed Fri | 3:00 p.m. - 4:00 p.m. | ESB-Floor 1-Room 1012"
    parse out the individual fields (start_date, end_date, days, class_time, location, room).
    
    Returns a dict that can be inserted into the Schedule schema.
    """

    # Example of a chunk:
    # "2025-01-06 - 2025-02-14 | Mon Wed Fri | 3:00 p.m. - 4:00 p.m. | ESB-Floor 1-Room 1012"
    parts = pattern_chunk.split('|')
    # Expecting 4 parts: date-range, days, time, location/room
    # e.g. parts[0] -> "2025-01-06 - 2025-02-14"
    #      parts[1] -> "Mon Wed Fri"
    #      parts[2] -> "3:00 p.m. - 4:00 p.m."
    #      parts[3] -> "ESB-Floor 1-Room 1012"

    if len(parts) < 4:
        # If the format doesn't match, handle gracefully
        return None

    date_range = parts[0].strip()
    days_str = parts[1].strip()
    class_time = parts[2].strip()
    location_room = parts[3].strip()

    # Parse the date range: "2025-01-06 - 2025-02-14"
    start_str, end_str = date_range.split('-')
    start_date_str = start_str.strip()
    end_date_str = end_str.strip()

    # Convert them to YYYY-MM-DD or DateTime objects
    # (You can handle errors or different formats as needed)
    # For example, "2025-01-06"
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
    except ValueError:
        # If the date format is different (like "1/6/2025"), adjust accordingly
        # We'll try an alternate parse
        try:
            start_date = datetime.strptime(start_date_str, '%m/%d/%Y')
            end_date = datetime.strptime(end_date_str, '%m/%d/%Y')
        except ValueError:
            # fallback if all parsing fails
            return None

    # Days might be "Mon Wed Fri" => we want ["Mon", "Wed", "Fri"]
    days_list = [d.strip() for d in days_str.split()]

    # If your schema expects an array of days, this is good.
    # If your schema expects a single string, you'd do `days = days_str` instead.

    # If you want to parse location vs. room, you can try:
    # Example: "ESB-Floor 1-Room 1012" => location="ESB-Floor 1", room="Room 1012"
    # For simplicity, store entire string in 'location' or do minimal splitting.
    # We'll do a minimal approach here:
    location = location_room
    room = ""

    schedule_data = {
        "start_date": start_date.isoformat(),  # or store the datetime object directly
        "end_date": end_date.isoformat(),
        "days": days_list,             # or a string if your schema wants a string
        "class_time": class_time,
        "location": location,
        "room": room
    }

    return schedule_data


def parse_meeting_pattern(chunk, start_date, end_date):
    """
    Given a single chunk of text from the 'Meeting Patterns' column, e.g.:
      "2025-01-06 - 2025-02-14 | Mon Wed Fri | 3:00 p.m. - 4:00 p.m. | ESB-Floor 1-Room 1012"
    we IGNORE the first piece (the date range), because we already have a
    'Start Date' and 'End Date' from separate columns.

    Instead we parse:
      - 2nd piece -> days (string like "Mon Wed Fri", which we convert to ["Mon","Wed","Fri"])
      - 3rd piece -> class_time (e.g. "3:00 p.m. - 4:00 p.m.")
      - 4th piece -> location (e.g. "ESB-Floor 1-Room 1012")

    We then build a dictionary with start_date, end_date, days, class_time, location, room, etc.
    """

    parts = chunk.split('|')
    # Example:
    # parts[0] => "2025-01-06 - 2025-02-14"  (ignored)
    # parts[1] => "Mon Wed Fri"
    # parts[2] => "3:00 p.m. - 4:00 p.m."
    # parts[3] => "ESB-Floor 1-Room 1012"

    # We need at least 4 parts; if fewer, skip this chunk
    if len(parts) < 4:
        return None

    days_str = parts[1].strip()
    class_time = parts[2].strip()
    location = parts[3].strip()

    loc_match = re.match(r"([^-]+)-Floor (\d+)-Room (\S+)", location.strip())
    loc = loc_match.group(1)
    room = loc_match.group(3)
    location_noti = f"Room {room} - {loc}"
    # Convert the days string ("Mon Wed Fri") into a list ["Mon","Wed","Fri"]
    days_list = [d.strip() for d in days_str.split()]

    # Build the schedule data dict
    schedule_data = {
        "start_date": start_date,     # from the 'Start Date' column
        "end_date": end_date,         # from the 'End Date' column
        "days": days_list,
        "class_time": class_time,
        "location": location_noti,
        "address": LOC_ABB[loc] + ", Vancouver, BC",
        "room": room,                   # optional, or parse further if needed
    }
    print(schedule_data)
    return schedule_data


def parse_excel_file(file):
    """
    Reads the Excel file, skipping the first two rows (so the third row is columns),
    extracts:
      - 'Section' (for class_name),
      - 'Start Date' and 'End Date' from separate columns,
      - 'Meeting Patterns' for days/time/location,
    then inserts them into MongoDB 'schedules'.
    """

    db = current_app.config['DB']  # or however you're accessing your DB

    # 1. Read the Excel file into a DataFrame, skipping the first 2 rows
    df = pd.read_excel(file, skiprows=2)

    # 2. For each row, get class name, start/end date, and meeting pattern text
    for _, row in df.iterrows():
        class_name = str(row.get("Section", "Unknown Class")).strip()

        # We assume there are columns named "Start Date" and "End Date" containing actual date strings
        start_date_str = str(row.get("Start Date", "")).strip()
        end_date_str = str(row.get("End Date", "")).strip()

        # Optionally parse them to a datetime or store them as strings
        start_date = start_date_str  # or parse to datetime if you prefer
        end_date = end_date_str      # or parse to datetime if you prefer

        # This is the multiline cell we’ll split on newlines
        meeting_patterns_text = str(row.get("Meeting Patterns", "")).strip()

        # 3. Each line is a separate pattern chunk
        pattern_chunks = [chunk for chunk in meeting_patterns_text.split('\n') if chunk.strip()]

        # 4. For each chunk, parse the days/time/location
        for chunk in pattern_chunks:
            parsed_data = parse_meeting_pattern(chunk, start_date, end_date)
            if not parsed_data:
                continue

            # Add the class_name (from "Section" column)
            parsed_data["class_name"] = class_name

            # 5. Insert into MongoDB
            try:
                db.schedules.insert_one(parsed_data)
            except Exception as e:
                print(f"Error inserting schedule data: {e}")

    return {
        "status": "success",
        "message": "Excel file parsed and schedules inserted into DB."
    }


@schedule_blueprint.route('/clear', methods=['DELETE'])
def clear_schedules():
    """
    DELETE /schedules/clear
    Deletes *all* documents in the schedules collection.
    """
    try:
        db = current_app.config['DB']
        delete_result = db.schedules.delete_many({})  # Delete all schedules
        return jsonify({
            "message": "All schedules cleared",
            "deleted_count": delete_result.deleted_count
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
# ------------------------------------------------------------------------------
# READ: Get all schedules
# ------------------------------------------------------------------------------
@schedule_blueprint.route('', methods=['GET'])
def get_schedules():
    """
    GET /schedules
    Returns a list of all schedules in the collection.
    """
    try:
        db = current_app.config['DB']
        schedules_list = list(db.schedules.find())
        # Serialize each document for JSON output
        return jsonify([serialize_doc(schedule) for schedule in schedules_list]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ------------------------------------------------------------------------------
# READ: Get a single schedule by ID
# ------------------------------------------------------------------------------
@schedule_blueprint.route('/<string:schedule_id>', methods=['GET'])
def get_schedule(schedule_id):
    """
    GET /schedules/<schedule_id>
    Returns a single schedule by its ObjectId.
    """
    try:
        db = current_app.config['DB']
        schedule_doc = db.schedules.find_one({"_id": ObjectId(schedule_id)})
        if schedule_doc:
            return jsonify(serialize_doc(schedule_doc)), 200
        else:
            return jsonify({"error": "Schedule not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ------------------------------------------------------------------------------
# UPDATE: Update a single schedule by ID
# ------------------------------------------------------------------------------
@schedule_blueprint.route('/<string:schedule_id>', methods=['PUT'])
def update_schedule(schedule_id):
    """
    PUT /schedules/<schedule_id>
    Body JSON example for updates (any subset of fields):
    {
      "class_time": "2:00 PM - 3:30 PM",
      "room": "Room 202"
    }
    """
    try:
        data = request.get_json()
        db = current_app.config['DB']
        update_result = db.schedules.update_one(
            {"_id": ObjectId(schedule_id)},
            {"$set": data}
        )
        if update_result.modified_count == 1:
            return jsonify({"message": "Schedule updated"}), 200
        else:
            return jsonify({"error": "Schedule not found or no changes made"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ------------------------------------------------------------------------------
# DELETE: Remove a single schedule by ID
# ------------------------------------------------------------------------------
@schedule_blueprint.route('/<string:schedule_id>', methods=['DELETE'])
def delete_schedule(schedule_id):
    """
    DELETE /schedules/<schedule_id>
    Deletes a schedule from the collection by its ObjectId.
    """
    try:
        db = current_app.config['DB']
        delete_result = db.schedules.delete_one({"_id": ObjectId(schedule_id)})
        if delete_result.deleted_count == 1:
            return jsonify({"message": "Schedule deleted"}), 200
        else:
            return jsonify({"error": "Schedule not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
