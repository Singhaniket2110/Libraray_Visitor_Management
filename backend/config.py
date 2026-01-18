import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "library-secret-key-2024")
    
    # ⚠️ VERCEL-SPECIFIC FIX: Use null session for serverless
    SESSION_TYPE = 'null'  # Changed from 'filesystem' to 'null'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = False
    PERMANENT_SESSION_LIFETIME = 1800
    
    # Cookie settings
    SESSION_COOKIE_SECURE = True  # Set to True for HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_NAME = 'library_session'
    
    DEBUG = False  # Must be False for production
