from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    days = db.Column(db.String(100), nullable=False)
    class_name = db.Column(db.String(100), nullable=False)
    class_time = db.Column(db.Time, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    room = db.Column(db.String(200), nullable=False)

class Reminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reminder_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default="pending")  # "pending", "done", "snoozed"

# class Achievement(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     name = db.Column(db.String(100), nullable=False)
#     unlocked_at = db.Column(db.DateTime, nullable=False)

class BusTracking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bus_eta = db.Column(db.Integer, nullable=False)  # Minutes until arrival