from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager 
from dotenv import load_dotenv
import os
import redis

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
redis_client = None 

def create_app():
    global redis_client
    load_dotenv()
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY")

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY", "default_jwt_secret")  

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Initialize Redis
    redis_client = redis.StrictRedis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        db=0,
        decode_responses=True
    )

    # Register Blueprints
    from app.routes.auth import auth_bp
    from app.routes.maps import map_bp 

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(map_bp, url_prefix="/map") 

    return app

