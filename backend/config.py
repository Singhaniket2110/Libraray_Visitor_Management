import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    # Flask Configuration
    SECRET_KEY = os.getenv("SECRET_KEY", "supabase-library-system-2024-aniket")
    DEBUG = False
    
    # ✅ VERCEL FIX: Disable Flask-Session completely
    SESSION_TYPE = None  # Don't use Flask-Session in serverless
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = 1800  # 30 minutes
    
    # Use standard Flask sessions (cookie-based)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_NAME = 'library_session'
