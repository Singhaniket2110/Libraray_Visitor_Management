import os
from supabase import create_client, Client

class SupabaseDatabase:
    # Initialize Supabase client ONCE
    supabase: Client = None
    
    @classmethod
    def init_client(cls):
        """Initialize Supabase client"""
        if cls.supabase is None:
            try:
                # Your Supabase credentials (hardcoded to avoid env issues)
                SUPABASE_URL = "https://wboxcfmizfkapdslzkks.supabase.co"
                SUPABASE_KEY = "sb_publishable_E-NsrmHADXLuAND0raA1-g_wwSGLx1t"
                
                cls.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
                print("✅ Supabase client initialized")
            except Exception as e:
                print(f"❌ Supabase init failed: {e}")
                raise
    
    @classmethod
    def execute_query(cls, query, params=None, fetch=False, fetch_all=False, commit=True):
        """Execute database operations using Supabase client"""
        try:
            # Initialize client if not done
            if cls.supabase is None:
                cls.init_client()
            
            # Handle different query types
            query_lower = query.strip().lower()
            
            # SELECT queries
            if query_lower.startswith('select'):
                if 'admin' in query_lower:
                    # Admin login check
                    table = query_lower.split('from')[1].strip().split()[0]
                    username = params[0] if params else None
                    
                    if username:
                        result = cls.supabase.table(table).select("*").eq('username', username).execute()
                        return result.data[0] if result.data else None
                
                # Generic SELECT
                table_match = query_lower.split('from')[1].strip().split()[0] if 'from' in query_lower else None
                if table_match:
                    result = cls.supabase.table(table_match).select("*").execute()
                    return result.data if fetch_all else (result.data[0] if result.data else None)
            
            # INSERT queries
            elif query_lower.startswith('insert'):
                if 'visitors' in query_lower:
                    # Extract data from params
                    if params and len(params) >= 10:
                        visitor_data = {
                            'name': params[0],
                            'roll_no': params[1],
                            'level': params[2],
                            'course': params[3],
                            'year': params[4] if params[4] else None,
                            'jc_year': params[5] if params[5] else None,
                            'jc_stream': params[6] if params[6] else None,
                            'purpose': params[7],
                            'visit_day': params[8],
                            'entry_time': params[9] if len(params) > 9 else None
                        }
                        
                        result = cls.supabase.table('visitors').insert(visitor_data).execute()
                        return result.data[0] if result.data else None
            
            # UPDATE queries
            elif query_lower.startswith('update'):
                if 'visitors' in query_lower and 'exit_time' in query_lower:
                    roll_no = params[0] if params else None
                    exit_time = params[1] if params and len(params) > 1 else None
                    
                    if roll_no and exit_time:
                        result = cls.supabase.table('visitors').update({'exit_time': exit_time}).eq('roll_no', roll_no).eq('exit_time', None).execute()
                        return result.data
            
            return None
            
        except Exception as e:
            print(f"❌ Database error: {e}")
            raise Exception(f"Database operation failed: {str(e)[:100]}")
    
    @classmethod
    def init_database(cls):
        """Initialize database - minimal check"""
        try:
            cls.init_client()
            print("✅ Database ready")
            return True
        except Exception as e:
            print(f"⚠️ Database init: {e}")
            return False
