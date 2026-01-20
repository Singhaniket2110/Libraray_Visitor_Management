import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

class Config:
    # Flask Configuration
    SECRET_KEY = os.getenv("SECRET_KEY", "cb27657c0b11c917e64c88e06f703540c44b84673dc5b1dff649c2631a9b3027")
    DEBUG = False
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv("SECRET_KEY", "supabase-library-system-2024-aniket")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=12)
    
    # Session settings
    SESSION_TYPE = None
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = 43200
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_NAME = 'library_session'
    
    # Supabase Configuration - IMPORTANT!
    SUPABASE_URL = os.getenv("SUPABASE_URL", "https://wboxcfmizfkapdslzkks.supabase.co")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY", "sb_publishable_E-NsrmHADXLuAND0raA1-g_wwSGLx1t")
    SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "sb_secret_DOYTKlg3bE2znm4AWQgxxQ_-vPzBOAO")
    
    # Direct database URL
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:pqjEH49+W*-3RfJ@db.wboxcfmizfkapdslzkks.supabase.co:5432/postgres?sslmode=require")
