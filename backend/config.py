import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask Configuration
    SECRET_KEY = os.getenv("SECRET_KEY", "library-secret-key-2024")
    DEBUG = os.getenv("FLASK_ENV") == "development"
    
    # Session Configuration
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = False
    PERMANENT_SESSION_LIFETIME = 1800  # 30 minutes
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_NAME = 'library_session'
    
    # Session file settings
    SESSION_FILE_DIR = 'flask_session'
    SESSION_FILE_THRESHOLD = 100
    SESSION_REFRESH_EACH_REQUEST = True