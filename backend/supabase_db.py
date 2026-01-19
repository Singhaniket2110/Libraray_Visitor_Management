import os
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from urllib.parse import urlparse
import time

load_dotenv()

class SupabaseDatabase:
    _connection_pool = None
    
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
    def get_pool(cls):
        """Create connection pool to Supabase with retry"""
        if cls._connection_pool is None:
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    conn_string = cls.get_connection_string()
                    print(f"🔗 Attempt {attempt + 1}: Connecting to Supabase...")
                    
                    cls._connection_pool = psycopg2.pool.SimpleConnectionPool(
                        1, 10,  # min 1, max 10 connections
                        conn_string,
                        cursor_factory=RealDictCursor
                    )
                    
                    # Test connection
                    conn = cls._connection_pool.getconn()
                    cur = conn.cursor()
                    cur.execute("SELECT 1 as test")
                    result = cur.fetchone()
                    cur.close()
                    cls._connection_pool.putconn(conn)
                    
                    print("✅ Supabase connection established successfully!")
                    break
                    
                except Exception as e:
                    print(f"❌ Connection attempt {attempt + 1} failed: {str(e)[:100]}")
                    if attempt < max_retries - 1:
                        time.sleep(2)  # Wait before retry
                    else:
                        raise
    
    @classmethod
    def execute_query(cls, query, params=None, fetch=False, fetch_all=False, commit=True):
        """Execute query with error handling"""
        connection = None
        cursor = None
        try:
            cls.get_pool()
            connection = cls._connection_pool.getconn()
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
            # Recreate pool if connection failed
            cls._connection_pool = None
            raise
        finally:
            if cursor:
                cursor.close()
            if connection and cls._connection_pool:
                cls._connection_pool.putconn(connection)
    
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
            """, commit=False)
            
            # Insert default admin (plain text password for now)
            cls.execute_query("""
                INSERT INTO admin (username, password) 
                VALUES ('admin', 'admin123')
                ON CONFLICT (username) DO NOTHING
            """, commit=False)
            
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
            """, commit=False)
            
            # Create indexes
            for index_query in [
                "CREATE INDEX IF NOT EXISTS idx_visit_date ON visitors(visit_date)",
                "CREATE INDEX IF NOT EXISTS idx_level ON visitors(level)",
                "CREATE INDEX IF NOT EXISTS idx_roll_no ON visitors(roll_no)"
            ]:
                cls.execute_query(index_query, commit=False)
            
            print("✅ Database tables initialized successfully")
            
        except Exception as e:
            print(f"⚠️ Database init note: {str(e)[:100]}")

# Initialize on import
try:
    SupabaseDatabase.init_database()
except Exception as e:
    print(f"ℹ️ Database initialization: {str(e)[:100]}")
