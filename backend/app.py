from flask import Flask
from pymongo import MongoClient

def create_app():
    app = Flask(__name__)

    # ---------------------------------------------------------------
    # 1. MongoDB Connection (moved from model.py to app.py)
    # ---------------------------------------------------------------
    MONGO_URI = "mongodb+srv://jackydo1974:JanDongHackCamp113@nwhack.9mwg2.mongodb.net/test"
    client = MongoClient(MONGO_URI)
    db = client.my_database
    app.config['DB'] = db  # store db in app config (or globally)

    # ---------------------------------------------------------------
    # 2. Register controllers/blueprints here (example only)
    # ---------------------------------------------------------------
    from controllers.scheduleController import schedule_blueprint
    app.register_blueprint(schedule_blueprint, url_prefix='/schedules')

    return app


if __name__ == "__main__":
    application = create_app()
    application.run(debug=True, port=5000)
