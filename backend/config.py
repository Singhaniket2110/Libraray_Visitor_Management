import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

class Config:
    # Flask Configuration
    SECRET_KEY = os.getenv("SECRET_KEY", "cb27657c0b11c917e64c88e06f703540c44b84673dc5b1dff649c2631a9b3027")
    DEBUG = False
    
    # JWT Configuration for serverless
    JWT_SECRET_KEY = os.getenv("SECRET_KEY", "supabase-library-system-2024-aniket")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=12)
    
    # Session settings (backup)
    SESSION_TYPE = None
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = 43200  # 12 hours
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_NAME = 'library_session'

