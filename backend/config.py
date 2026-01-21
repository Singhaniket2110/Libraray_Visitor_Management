import os
from dotenv import load_dotenv
from datetime import timedelta

# LOAD ENVIRONMENT VARIABLES FIRST
load_dotenv()

class Config:
    # ==================== FLASK CONFIG ====================
    SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key-change-this")
    DEBUG = os.getenv("FLASK_ENV", "production") == "development"
    
    # ==================== JWT CONFIG ====================
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=12)
    
    # ==================== SESSION CONFIG ====================
    SESSION_TYPE = None
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = 43200  # 12 hours in seconds
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_NAME = 'library_session'
    
    # ==================== SUPABASE CONFIG ====================
    # Get values directly from .env (NO HARDCODED FALLBACKS)
    SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
    SUPABASE_KEY = os.getenv("SUPABASE_KEY", "").strip()
    SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
    
    # ==================== VALIDATION METHOD ====================
    @classmethod
    def validate_config(cls):
        """Check if all required configs are present and valid"""
        # Clean all values again
        cls.SUPABASE_URL = cls.SUPABASE_URL.strip().strip('"').strip("'")
        cls.SUPABASE_SERVICE_KEY = cls.SUPABASE_SERVICE_KEY.strip().strip('"').strip("'")
        
        # Check required variables
        required = {
            'SECRET_KEY': cls.SECRET_KEY,
            'SUPABASE_URL': cls.SUPABASE_URL,
            'SUPABASE_SERVICE_KEY': cls.SUPABASE_SERVICE_KEY,
        }
        
        missing = [key for key, value in required.items() if not value]
        
        if missing:
            print(f"❌ MISSING in .env: {missing}")
            return False
        
        # Validate URL format
        if not cls.SUPABASE_URL.startswith("https://"):
            print(f"❌ INVALID SUPABASE_URL: Should start with https://")
            print(f"   Got: {cls.SUPABASE_URL[:50]}")
            return False
        
        print(f"✅ Config validated")
        print(f"   Project: {cls.SUPABASE_URL.split('//')[1].split('.')[0]}")
        print(f"   Key present: {'Yes' if cls.SUPABASE_SERVICE_KEY else 'No'}")
        return True
