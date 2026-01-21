import os
from dotenv import load_dotenv
from datetime import timedelta

# LOAD ENVIRONMENT VARIABLES FIRST
load_dotenv()

class Config:
    # ==================== FLASK CONFIG ====================
    SECRET_KEY = os.getenv("SECRET_KEY")
    DEBUG = os.getenv("FLASK_ENV") == "development"
    
    # ==================== JWT CONFIG ====================
    # JWT_SECRET_KEY alag rakhna better hai
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", os.getenv("SECRET_KEY"))
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
    # YEH SAB .env FILE SE AAYENGE
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    # ==================== VALIDATION METHOD ====================
    @classmethod
    def validate_config(cls):
        """Check if all required configs are present"""
        required = {
            'SECRET_KEY': cls.SECRET_KEY,
            'SUPABASE_URL': cls.SUPABASE_URL,
            'SUPABASE_SERVICE_KEY': cls.SUPABASE_SERVICE_KEY,
            'DATABASE_URL': cls.DATABASE_URL
        }
        
        missing = [key for key, value in required.items() if not value]
        
        if missing:
            print(f"❌ MISSING in .env: {missing}")
            return False
        
        print("✅ All configurations loaded from .env")
        return True
