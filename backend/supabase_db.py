import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import urllib.parse
import ssl

load_dotenv()

class SupabaseDatabase:
    
    @classmethod
    def get_connection(cls):
        """Get a fresh database connection - Vercel optimized"""
        try:
            # Use DATABASE_URL from your .env
            database_url = os.getenv('postgresql://postgres:pqjEH49%2BW%2A-3RfJ@db.wboxcfmizfkapdslzkks.supabase.co:5432/postgres')
            
            if not database_url:
                print("❌ DATABASE_URL not found in environment")
                raise Exception("DATABASE_URL not configured")
            
            print(f"🔗 Connecting via DATABASE_URL...")
            
            # IMPORTANT: Parse the URL to extract components
            parsed_url = urllib.parse.urlparse(database_url)
            
            # Decode password if it's URL encoded
            password = urllib.parse.unquote(parsed_url.password)
            
            # Build connection parameters for Vercel
            db_params = {
                'host': parsed_url.hostname,
                'port': parsed_url.port or 5432,
                'database': parsed_url.path[1:],  # Remove leading '/'
                'user': parsed_url.username,
                'password': password,
                'connect_timeout': 10,
                'sslmode': 'require',  # IMPORTANT: Supabase requires SSL
                'sslrootcert': '/etc/ssl/certs/ca-certificates.crt',  # Vercel's cert path
            }
            
            conn = psycopg2.connect(
                **db_params,
                cursor_factory=RealDictCursor
            )
            
            print("✅ Connected to Supabase Database")
            return conn
            
        except Exception as e:
            print(f"❌ Connection failed: {str(e)}")
            # For better debugging
            if "DATABASE_URL" in os.environ:
                print(f"📝 DATABASE_URL present in env")
                # Don't show full URL for security, just confirm it exists
            raise Exception(f"Database connection failed: {str(e)[:200]}")
    
    @classmethod
    def execute_query(cls, query, params=None, fetch=False, fetch_all=False, commit=True):
        """Execute query with automatic connection management - Vercel optimized"""
        connection = None
        cursor = None
        
        try:
            connection = cls.get_connection()
            cursor = connection.cursor()
            
            # Print query for debugging (truncated)
            if len(query) > 100:
                print(f"📝 Executing: {query[:100]}...")
            else:
                print(f"📝 Executing: {query}")
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # Handle results based on query type
            if fetch:
                result = cursor.fetchone()
            elif fetch_all:
                result = cursor.fetchall()
            else:
                if commit:
                    connection.commit()
                result = cursor.rowcount
            
            return result
            
        except psycopg2.OperationalError as e:
            print(f"❌ Database operational error: {str(e)}")
            if connection:
                connection.rollback()
            raise Exception(f"Database connection issue. Please try again.")
            
        except Exception as e:
            print(f"❌ Query error: {str(e)}")
            if connection:
                connection.rollback()
            raise Exception(f"Database error: {str(e)[:100]}")
            
        finally:
            # IMPORTANT: Always close connections on Vercel
            if cursor:
                cursor.close()
            if connection:
                connection.close()
                print("🔌 Connection closed")
    
    @classmethod
    def test_connection(cls):
        """Test database connection"""
        try:
            result = cls.execute_query("SELECT NOW() as current_time", fetch=True)
            if result:
                print(f"✅ Database test successful: {result}")
                return True
            return False
        except Exception as e:
            print(f"❌ Database test failed: {e}")
            return False
    
    @classmethod
    def init_database(cls):
        """Initialize database tables - Vercel compatible version"""
        try:
            print("🔄 Initializing database tables...")
            
            # Test connection first
            if not cls.test_connection():
                raise Exception("Cannot initialize - database connection failed")
            
            # Create admin table
            cls.execute_query("""
                CREATE TABLE IF NOT EXISTS admin (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Insert default admin if not exists
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
            
            print("✅ Database initialization complete")
            return True
            
        except Exception as e:
            print(f"⚠️ DB init error: {str(e)[:200]}")
            return False

