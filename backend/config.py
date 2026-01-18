import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask Configuration
    SECRET_KEY = os.getenv("SECRET_KEY", "library-secret-key-2024")
    DEBUG = False  # MUST BE FALSE FOR VERCEL
    
    # 🚀 VERCEL-SPECIFIC SESSION CONFIG
    # Use 'null' session type for serverless environment
    SESSION_TYPE = 'null'  # Changed from 'filesystem' to 'null'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = False
    PERMANENT_SESSION_LIFETIME = 1800  # 30 minutes
    
    # Cookie settings for production
    SESSION_COOKIE_SECURE = True  # Set to True for HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_NAME = 'library_session'
    
    # Remove file session settings
    # SESSION_FILE_DIR = 'flask_session'  # REMOVE THIS
    # SESSION_FILE_THRESHOLD = 100        # REMOVE THIS
    SESSION_REFRESH_EACH_REQUEST = True
