import datetime
import re
import pandas as pd
from flask import Blueprint, request, jsonify
from backend.models import db, Schedule  # Import from models.py instead of app.py

schedule_bp = Blueprint('schedule', __name__)  # Create Blueprint

ALLOWED_EXTENSIONS = {'xls', 'xlsx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@schedule_bp.route('/upload-xls', methods=['POST'])
def upload_schedule():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    return file_extract(file)

def file_extract(file):
    df = pd.read_excel(file, header=2)
    added_classes = []

    for _, row in df.iterrows():
        if pd.isna(row.get('Meeting Patterns')):
            continue

        meeting_pattern = parse_meeting_pattern(row['Meeting Patterns'])

        if not meeting_pattern:
            continue

        new_class = Schedule(
            class_name=row['Section'],
            start_date=meeting_pattern["start_date"],
            end_date=meeting_pattern["end_date"],
            days=meeting_pattern["days"],
            class_time=meeting_pattern["time"],
            location=meeting_pattern["location"],
            room=meeting_pattern["room"],
        )
        db.session.add(new_class)
        added_classes.append(new_class)
    db.session.commit()
    return jsonify({"added_classes": [c.class_name for c in added_classes]}), 200

def parse_meeting_pattern(pattern):
    match = re.match(
        r"(\d{4}-\d{2}-\d{2}) - (\d{4}-\d{2}-\d{2}) \| ([^|]+) \| ([^|]+) \| ([^-]+)-Floor (\d+)-Room (\S+)",
        pattern.strip()
    )
    if match:
        return {
            "start_date": match.group(1),
            "end_date": match.group(2),
            "days": match.group(3),
            "time": match.group(4),
            "location": match.group(5).strip(),
            "room": match.group(7)
        }
    return None

@schedule_bp.route('/next-class', methods=['GET'])
def next_class():
    now = datetime.datetime.now().time()
    next_class = Schedule.query.filter(Schedule.class_time > now).order_by(Schedule.class_time).first()
    if next_class:
        return jsonify({
            "class_name": next_class.class_name,
            "class_time": next_class.class_time.strftime("%H:%M"),
            "location": next_class.location
        })
    return jsonify({"message": "No upcoming classes"})

@schedule_bp.route('/today', methods=['GET'])
def today_schedule():
    today = datetime.datetime.now().date()
    classes_today = Schedule.query.filter(
        Schedule.class_time >= datetime.datetime.combine(today, datetime.datetime.min.time()),
        Schedule.class_time <= datetime.datetime.combine(today, datetime.datetime.max.time())
    ).order_by(Schedule.class_time).all()

    if classes_today:
        return jsonify([{
            "class_name": c.class_name,
            "class_time": c.class_time.strftime("%H:%M"),
            "location": c.location
        } for c in classes_today]), 200
    return jsonify({"message": "No classes scheduled for today"}), 404
