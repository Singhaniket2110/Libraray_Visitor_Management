import os
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

class SupabaseDatabase:
    _connection_pool = None
    
    @classmethod
    def get_pool(cls):
        """Create connection pool to Supabase"""
        if cls._connection_pool is None:
            try:
                # Try DATABASE_URL first
                database_url = os.getenv('DATABASE_URL')
                
                if not database_url:
                    # Construct from Supabase components
                    supabase_url = os.getenv('SUPABASE_URL', '').replace('https://', '')
                    password = os.getenv('SUPABASE_DB_PASSWORD', '')
                    
                    if supabase_url and password:
                        database_url = f"postgresql://postgres:{password}@db.{supabase_url}:5432/postgres"
                    else:
                        raise ValueError("Database connection details not found in .env")
                
                print(f"🔗 Connecting to: {database_url.split('@')[1] if '@' in database_url else database_url}")
                
                cls._connection_pool = psycopg2.pool.SimpleConnectionPool(
                    1, 20,  # min 1, max 20 connections
                    database_url,
                    cursor_factory=RealDictCursor
                )
                print("✅ Supabase connection pool created successfully")
                
                # Test connection
                conn = cls._connection_pool.getconn()
                cur = conn.cursor()
                cur.execute("SELECT version();")
                db_version = cur.fetchone()
                print(f"📊 Database version: {db_version['version'][:50]}...")
                cur.close()
                cls._connection_pool.putconn(conn)
                
            except Exception as e:
                print(f"❌ Error creating connection pool: {str(e)}")
                raise
        
        return cls._connection_pool
    
    @classmethod
    def get_connection(cls):
        """Get connection from pool"""
        pool = cls.get_pool()
        return pool.getconn()
    
    @classmethod
    def return_connection(cls, connection):
        """Return connection to pool"""
        pool = cls.get_pool()
        pool.putconn(connection)
    
    @classmethod
    def execute_query(cls, query, params=None, fetch=False, fetch_all=False):
        """Execute query with connection pooling"""
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
                connection.commit()
                result = cursor.rowcount if 'INSERT' not in query.upper() else cursor.fetchone()
            
            return result
            
        except Exception as e:
            print(f"❌ Database query error: {e}")
            print(f"Query: {query}")
            print(f"Params: {params}")
            if connection:
                connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                cls.return_connection(connection)
    
    @classmethod
    def create_tables(cls):
        """Create necessary tables if they don't exist"""
        try:
            # Create admin table
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
            cls.execute_query("CREATE INDEX IF NOT EXISTS idx_visit_date ON visitors(visit_date)")
            cls.execute_query("CREATE INDEX IF NOT EXISTS idx_level ON visitors(level)")
            cls.execute_query("CREATE INDEX IF NOT EXISTS idx_roll_no ON visitors(roll_no)")
            
            print("✅ Supabase tables created/verified successfully")
            
        except Exception as e:
            print(f"⚠️  Note: {e}")
    
    @classmethod
    def close_pool(cls):
        """Close all connections in pool"""
        if cls._connection_pool:
            cls._connection_pool.closeall()
            print("✅ Connection pool closed")

# Initialize database on import
try:
    SupabaseDatabase.create_tables()
except Exception as e:
    print(f"ℹ️  Database initialization note: {e}")