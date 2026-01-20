import psycopg2
from psycopg2.extras import RealDictCursor
import socket

class SupabaseDatabase:
    
    @classmethod
    def get_connection(cls):
        """Direct IP connection bypassing DNS issues"""
        try:
            # Use direct IP address to bypass DNS resolution
            # This IP is for db.wboxcfmizfkapdslzkks.supabase.co (Asia Pacific - Mumbai)
            conn = psycopg2.connect(
                host="13.126.205.229",  # Direct IP for Supabase Mumbai region
                port=5432,
                database="postgres",
                user="postgres",
                password="pqjEH49+W*-3RfJ",
                sslmode="require",
                connect_timeout=15,
                cursor_factory=RealDictCursor,
                # Disable hostname verification for SSL
                sslcert=None,
                sslkey=None,
                # Connection settings
                keepalives=1,
                keepalives_idle=30,
                keepalives_interval=10
            )
            return conn
            
        except Exception as e:
            # Fallback to hostname if IP fails
            try:
                conn = psycopg2.connect(
                    host="db.wboxcfmizfkapdslzkks.supabase.co",
                    port=5432,
                    database="postgres",
                    user="postgres",
                    password="pqjEH49+W*-3RfJ",
                    sslmode="require",
                    connect_timeout=15,
                    cursor_factory=RealDictCursor
                )
                return conn
            except Exception as e2:
                raise Exception(f"Database connection failed: {str(e2)}")
    
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
