# config.py – Fixed version with auto-created instance folder
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-me'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-change-me'
    
    # === FIX: Ensure instance folder exists ===
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))           # project root
    INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')
    
    # Create the folder if it doesn't exist (safe on every run)
    os.makedirs(INSTANCE_DIR, exist_ok=True)
    
    # Now use absolute path inside instance/
    DB_PATH = os.path.join(INSTANCE_DIR, 'simply.db')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f'sqlite:///{DB_PATH}'
    )
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = os.environ.get('SQL_ECHO', 'False') == 'True'  # debug SQL