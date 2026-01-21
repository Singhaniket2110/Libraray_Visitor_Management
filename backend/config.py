import os
from dotenv import load_dotenv
from datetime import timedelta

# LOAD ENVIRONMENT VARIABLES FIRST
load_dotenv()

class Config:
    # ==================== FLASK CONFIG ====================
    SECRET_KEY = os.getenv("SECRET_KEY", "")
    DEBUG = os.getenv("FLASK_ENV", "production") == "development"
    
    # ==================== JWT CONFIG ====================
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=12)
    
    # ==================== SESSION CONFIG ====================
    SESSION_TYPE = None
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = 43200
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_NAME = 'library_session'
    
    # ==================== SUPABASE CONFIG ====================
    SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
    SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    DATABASE_URL = os.getenv("DATABASE_URL", "")
    
    # ==================== VALIDATION METHOD ====================
    @classmethod
    def validate_config(cls):
        """Check if all required configs are present"""
        # Clean values
        cls.SUPABASE_URL = cls.SUPABASE_URL.strip('"\' ')
        cls.SUPABASE_SERVICE_KEY = cls.SUPABASE_SERVICE_KEY.strip('"\' ')
        
        # Check required
        required = ['SUPABASE_URL', 'SUPABASE_SERVICE_KEY', 'SECRET_KEY']
        missing = [key for key in required if not getattr(cls, key)]
        
        if missing:
            print(f"❌ MISSING in .env: {missing}")
            return False
        
        # Validate URL
        if not cls.SUPABASE_URL.startswith("https://"):
            print(f"❌ Invalid SUPABASE_URL format")
            return False
        
        print(f"✅ Config validated")
        print(f"   Project: {cls.SUPABASE_URL.split('//')[1].split('.')[0]}")
        return True
