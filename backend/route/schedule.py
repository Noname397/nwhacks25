import datetime
import re
from datetime import datetime, date, time


import pandas as pd

import os
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename

from backend.database import Schedule, db

schedule_bp = Blueprint('schedule', __name__)  # Create Blueprint

ALLOWED_EXTENSIONS = {'xls', 'xlsx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@schedule_bp.route('/schedule/upload-xls', methods=['POST'])
def upload_schedule():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    # Parse XLS file
    return file_extract(file)


def file_extract(file):
    df = pd.read_excel(file)
    for _, row in df.iterrows():
        meeting_pattern = parse_meeting_pattern(row['Meeting Patterns'])
        building = meeting_pattern["location"]
        location = building_dict[building] + " Vancouver, BC"

        new_class = Schedule(
            class_name=row['Section'],
            start_Date=meeting_pattern["start_date"],
            end_date=meeting_pattern["end_date"],
            days=meeting_pattern["days"],
            class_time=meeting_pattern["time"],
            location=location,
            room=meeting_pattern["room"],
        )
        db.session.add(new_class)
    db.session.commit()
    return jsonify({"message": "Schedule uploaded successfully"}), 200


def parse_meeting_pattern(pattern):
    match = re.match(
        r"(\d{4}-\d{2}-\d{2}) - (\d{4}-\d{2}-\d{2}) \| ([^|]+) \| ([^|]+) \| ([^-]+)-Floor (\d+)-Room (\S+)",
        pattern.strip()
    )
    if match:
        return {
            "start_date": match.group(1),  # Ngày bắt đầu
            "end_date": match.group(2),    # Ngày kết thúc
            "days": match.group(3),        # Các ngày trong tuần
            "time": match.group(4),        # Khung giờ
            "location": match.group(5).strip(),  # Tòa nhà
            "room": match.group(7)         # Phòng
        }
    return None

file_path = "./resource/UBC Abb.xlsx"  # Change this to the correct path if needed
df = pd.read_excel(file_path)

# Create dictionary mapping Building Code to Address
building_dict = dict(zip(df["Building Code"], df["Address"]))

@schedule_bp.route('/schedule/next-class', methods=['GET'])
def next_class():
    now = datetime.now().time()
    next_class = Schedule.query.filter(Schedule.class_time > now).order_by(Schedule.class_time).first()
    if next_class:
        return jsonify({
            "class_name": next_class.class_name,
            "class_time": next_class.class_time.strftime("%H:%M"),
            "location": next_class.location
        })
    return jsonify({"message": "No upcoming classes"})

@schedule_bp.route('/schedule/today', methods=['GET'])
def today_schedule():
    today = datetime.now().date()
    classes_today = Schedule.query.filter(
        Schedule.class_time >= datetime.combine(today, datetime.min.time()),
        Schedule.class_time <= datetime.combine(today, datetime.max.time())
    ).order_by(Schedule.class_time).all()

    if classes_today:
        result = [
            {
                "class_name": c.class_name,
                "class_time": c.class_time.strftime("%H:%M"),
                "location": c.location
            }
            for c in classes_today
        ]
        return jsonify(result), 200
    return jsonify({"message": "No classes scheduled for today"}), 404
