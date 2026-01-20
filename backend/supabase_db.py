import psycopg2
from psycopg2.extras import RealDictCursor

class SupabaseDatabase:
    
    @classmethod
    def get_connection(cls):
        """Connect via Supabase Connection Pooler (port 6543) for Vercel"""
        try:
            # Use connection pooler port 6543 instead of 5432
            conn = psycopg2.connect(
                host="aws-0-ap-south-1.pooler.supabase.com",  # Pooler host
                port=6543,  # Connection pooler port
                database="postgres",
                user="postgres.wboxcfmizfkapdslzkks",  # Format: postgres.{project-ref}
                password="pqjEH49+W*-3RfJ",
                sslmode="require",
                connect_timeout=10,
                cursor_factory=RealDictCursor
            )
            return conn
            
        except Exception as e:
            raise Exception(f"Database connection failed: {str(e)}")
    
    @classmethod
    def execute_query(cls, query, params=None, fetch=False, fetch_all=False, commit=True):
        """Execute query with connection management"""
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
            if connection:
                connection.rollback()
            raise Exception(f"Database error: {str(e)[:100]}")
            
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
