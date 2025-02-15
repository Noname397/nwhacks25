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
    GET /schedules/next-class
    Returns the next upcoming class for today (the first class whose start time >= now),
    including a 'building_address' field if the building code is found in LOC_ABB.
    """
    try:
        db = current_app.config['DB']
        schedule_collection = db["schedules"]

        now = datetime.now()
        # e.g. "2025-01-21"
        today_date = now.strftime("%Y-%m-%d")
        # e.g. "Mon", "Tue", etc.
        today_weekday = now.strftime("%a")

        # Query for schedules happening today
        query = {
            "start_date": {"$lte": today_date},
            "end_date":   {"$gte": today_date},
            "days":       today_weekday
        }
        docs = list(schedule_collection.find(query))

        # Helper to parse the first part of 'class_time' as a 12-hour time
        def parse_first_time(time_str):
            """
            e.g. "3:00 p.m. - 4:00 p.m." => parse "3:00 p.m." -> a datetime.time object
            """
            try:
                first_part = time_str.split('-')[0].strip()  # "3:00 p.m."
                # remove extra '.' and uppercase => "3:00 PM"
                cleaned = first_part.replace('.', '').upper()
                dt_obj = datetime.strptime(cleaned, "%I:%M %p")
                return dt_obj.time()
            except:
                # If parsing fails, return earliest possible time so it sorts first
                return datetime.min.time()

        # Sort schedules by their start time
        docs_sorted = sorted(docs, key=lambda d: parse_first_time(d.get("class_time", "")))

        # Find the first class whose start time >= current time
        now_time = now.time()
        for doc in docs_sorted:
            start_t = parse_first_time(doc.get("class_time", ""))
            if start_t >= now_time:
                # This is the next upcoming class
                doc["_id"] = str(doc["_id"])  # Convert ObjectId to string

                # Parse building code from location, e.g. "ESB-Floor 1-Room 1012" => "ESB"
                location_str = doc.get("location", "")
                building_code = location_str.split('-')[0].strip()
                # Lookup the address from LOC_ABB
                doc["building_address"] = LOC_ABB.get(building_code, "Unknown Address")

                return jsonify(doc), 200

        # If we get here, there's no upcoming class for today
        return jsonify({"message": "No more classes today"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@schedule_blueprint.route('/today', methods=['GET'])
def today_schedule():
    """
    GET /schedules/today
    Returns all classes scheduled for today, sorted by time.
    """
    try:
        db = current_app.config['DB']
        schedule_collection = db["schedules"]

        # 1. Determine today's date (YYYY-MM-DD) and weekday (e.g. "Mon")
        today = datetime.now()
        today_date = today.strftime("%Y-%m-%d")      # e.g. "2025-01-21"
        today_weekday = today.strftime("%a")         # e.g. "Mon", "Tue", etc.

        # 2. Query for schedules where:
        #    start_date <= today_date <= end_date
        #    AND the 'days' array includes today's weekday
        query = {
            "start_date": {"$lte": today_date},
            "end_date": {"$gte": today_date},
            "days": today_weekday
        }
        docs = list(schedule_collection.find(query))

        # 3. Sort the resulting documents by the start time in 'class_time' (e.g. "3:00 p.m. - 4:00 p.m.")
        #    We'll parse only the first segment "3:00 p.m." into a 24-hour datetime, then sort by that.

        def parse_first_time(time_str):
            """
            Given a string like "3:00 p.m. - 4:00 p.m.",
            parse the first time ("3:00 p.m.") into a datetime.time object for sorting.
            """
            try:
                # Example: "3:00 p.m." -> remove extra periods, uppercase to "3:00 PM"
                first_part = time_str.split('-')[0].strip()  # "3:00 p.m."
                cleaned = first_part.replace('.', '').upper()  # "3:00 PM"

                # Parse as 12-hour time
                dt_obj = datetime.strptime(cleaned, "%I:%M %p")
                return dt_obj.time()  # We only need a time object for sorting
            except:
                # If parsing fails for some reason, return a default or early time
                return datetime.min.time()

        docs_sorted = sorted(docs, key=lambda d: parse_first_time(d.get("class_time", "")))

        # 4. Convert ObjectIds to strings for JSON
        for d in docs_sorted:
            d["_id"] = str(d["_id"])

        return jsonify(docs_sorted), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



def parse_meeting_pattern(chunk, start_date, end_date):
    """
    Parses a single meeting pattern into structured data.
    """
    parts = chunk.split('|')
    if len(parts) < 4:
        return None  # Skip invalid rows

    days_str = parts[1].strip()
    class_time = parts[2].strip()
    location = parts[3].strip()

    # Extract location and room safely
    loc_match = re.match(r"([^-]+)-Floor (\d+)-Room (\S+)", location.strip())
    if loc_match:
        loc = loc_match.group(1)
        room = loc_match.group(3)
        location_noti = f"Room {room} - {loc}"
    else:
        loc = location  # Fallback if regex fails
        room = "Unknown"
        location_noti = location  # Use full location as fallback

    days_list = [d.strip() for d in days_str.split()]

    try:
        # Extract start and end time
        start_time_str, end_time_str = class_time.split('-')
        start_time_str = re.sub(r'\.', '', start_time_str.strip()).upper()
        end_time_str = re.sub(r'\.', '', end_time_str.strip()).upper()

        start_time_obj = datetime.strptime(start_time_str, "%I:%M %p")
        end_time_obj = datetime.strptime(end_time_str, "%I:%M %p")

        formatted_start_time = start_time_obj.strftime("%H:%M")
        formatted_end_time = end_time_obj.strftime("%H:%M")
    except ValueError:
        return None  # Skip invalid time formats

    schedule_data = {
        "start_date": start_date,
        "end_date": end_date,
        "days": days_list,
        "start_time": formatted_start_time,
        "end_time": formatted_end_time,
        "location": location_noti,
        "address": LOC_ABB.get(loc, "Unknown Address"),
        "room": room,
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
