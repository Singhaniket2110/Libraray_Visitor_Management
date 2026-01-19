import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask Configuration
    SECRET_KEY = os.getenv("SECRET_KEY", "supabase-library-system-2024-aniket")
    DEBUG = False  # Production me False rakho
    
    # ✅ VERCEL FIX: Use null session for serverless
    SESSION_TYPE = 'null'  # Changed from 'filesystem' to 'null'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True  # Enable for security
    PERMANENT_SESSION_LIFETIME = 1800  # 30 minutes
    
    # Cookie settings for Vercel
    SESSION_COOKIE_SECURE = True  # Enable in production
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_NAME = 'library_session'
    
    # Disable filesystem session for Vercel
    SESSION_FILE_DIR = None
    SESSION_FILE_THRESHOLD = 0
    SESSION_REFRESH_EACH_REQUEST = True
