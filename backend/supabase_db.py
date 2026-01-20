import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import time

load_dotenv()

class SupabaseDatabase:
    # ❌ Don't use connection pooling in serverless
    # Each function invocation should create/close its own connection
    
    @classmethod
    def get_connection_string(cls):
        """Get connection string with proper URL encoding"""
        database_url = os.getenv('DATABASE_URL')
        
        if database_url:
            return database_url
        
        # Build from components
        supabase_url = os.getenv('SUPABASE_URL', '').replace('https://', '')
        password = os.getenv('SUPABASE_DB_PASSWORD', '')
        
        # URL encode special characters in password
        import urllib.parse
        encoded_password = urllib.parse.quote(password, safe='')
        
        return f"postgresql://postgres:{encoded_password}@db.{supabase_url}:5432/postgres"
    
    @classmethod
    def get_connection(cls):
        """Get a fresh database connection (serverless-friendly)"""
        try:
            conn_string = cls.get_connection_string()
            conn = psycopg2.connect(conn_string, cursor_factory=RealDictCursor)
            return conn
        except Exception as e:
            print(f"❌ Connection failed: {str(e)[:100]}")
            raise
    
    @classmethod
    def execute_query(cls, query, params=None, fetch=False, fetch_all=False, commit=True):
        """Execute query with automatic connection management"""
        connection = None
        cursor = None
        try:
            connection = cls.get_connection()
            cursor = connection.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if fetch:
                result = cursor.fetchone()
            elif fetch_all:
                result = cursor.fetchall()
            else:
                if commit:
                    connection.commit()
                result = cursor.rowcount
            
            return result
            
        except Exception as e:
            print(f"❌ Database error: {str(e)}")
            print(f"Query: {query[:100]}...")
            if connection:
                connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()  # Always close in serverless
    
    @classmethod
    def init_database(cls):
        """Initialize database tables"""
        try:
            # Create admin table if not exists
            cls.execute_query("""
                CREATE TABLE IF NOT EXISTS admin (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Insert default admin
            cls.execute_query("""
                INSERT INTO admin (username, password) 
                VALUES ('admin', 'admin123')
                ON CONFLICT (username) DO NOTHING
            """)
            
            # Create visitors table
            cls.execute_query("""
                CREATE TABLE IF NOT EXISTS visitors (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    roll_no VARCHAR(20) NOT NULL,
                    level VARCHAR(2) NOT NULL CHECK (level IN ('JC', 'UG', 'PG')),
                    course VARCHAR(100) NOT NULL,
                    year VARCHAR(20),
                    jc_year VARCHAR(10),
                    jc_stream VARCHAR(20),
                    purpose VARCHAR(100) NOT NULL,
                    entry_time TIME DEFAULT (CURRENT_TIME),
                    exit_time TIME,
                    visit_date DATE DEFAULT (CURRENT_DATE),
                    visit_day VARCHAR(10) NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Create indexes
            for index_query in [
                "CREATE INDEX IF NOT EXISTS idx_visit_date ON visitors(visit_date)",
                "CREATE INDEX IF NOT EXISTS idx_level ON visitors(level)",
                "CREATE INDEX IF NOT EXISTS idx_roll_no ON visitors(roll_no)"
            ]:
                cls.execute_query(index_query)
            
            print("✅ Database tables initialized successfully")
            
        except Exception as e:
            print(f"⚠️ Database init: {str(e)[:100]}")

# ❌ DON'T initialize on import in serverless
# Initialize only when needed
