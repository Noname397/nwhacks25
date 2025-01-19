from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from backend.schedule import schedule_bp



def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'LONMEMAY'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///school_bud.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    UPLOAD_FOLDER = "uploads"
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    db = SQLAlchemy(app)
    db.init_app(app)  # ✅ Properly initialize it with Flask app

    with app.app_context():
        db.create_all()  # Ensure tables are created

    return app


# Initialize db with the app
app = create_app()
app.register_blueprint(schedule_bp,url_prefix='/schedule')


if __name__ == '__main__':
    app.run(debug=True)