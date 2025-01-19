from flask import Flask
from pymongo import MongoClient
from controllers.scheduleController import schedule_blueprint
from controllers.mapController import map_endpoints  # Import map_endpoints
from flask_cors import CORS
  # Allow all origins, or specify your frontend URL

import my_secrets

def create_app():
    app = Flask(__name__)
    CORS(app)

    # ---------------------------------------------------------------
    # 1. MongoDB Connection (moved from model.py to app.py)
    # ---------------------------------------------------------------
    MONGO_URI = my_secrets.MONGO_URI
    client = MongoClient(MONGO_URI)
    db = client.my_database
    app.config['DB'] = db  # store db in app config (or globally)

    # ---------------------------------------------------------------
    # 2. Register controllers/blueprints here (example only)
    # ---------------------------------------------------------------
    app.register_blueprint(schedule_blueprint, url_prefix='/schedules')
    app.register_blueprint(map_endpoints, url_prefix='/map')
    return app


if __name__ == "__main__":
    application = create_app()
    application.run(debug=True, port=5000)
