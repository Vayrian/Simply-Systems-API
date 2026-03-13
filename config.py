# config.py
import os
from datetime import timedelta

# Load environment variables from .env file (for local dev)
from dotenv import load_dotenv
load_dotenv()

class Config:
    # Secret keys (use strong random values in production!)
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-me-immediately')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-change-me')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)

    # Database – use PostgreSQL on Railway, fallback to SQLite for local
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'sqlite:///simply.db'  # fallback for local development
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Other settings
    DEBUG = os.getenv('FLASK_DEBUG', 'False') == 'True'