from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # 👈 ADD THIS
from dotenv import load_dotenv
import os

db = SQLAlchemy()
migrate = Migrate()  # 👈 ADD THIS

def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY")
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)  # 👈 ADD THIS LINE

    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")

    return app
