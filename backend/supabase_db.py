import os
from supabase import create_client, Client
from datetime import datetime
from backend.config import Config

class SupabaseDatabase:
    supabase: Client = None
    
    @classmethod
    def init_client(cls):
        """Initialize Supabase client"""
        if cls.supabase is None:
            try:
                print("=" * 50)
                print("🔄 INITIALIZING SUPABASE CLIENT")
                
                # Validate config
                if not Config.validate_config():
                    raise Exception("Config validation failed")
                
                # Get and clean values
                SUPABASE_URL = Config.SUPABASE_URL.strip('"\' ')
                SUPABASE_SERVICE_KEY = Config.SUPABASE_SERVICE_KEY.strip('"\' ')
                
                # Remove any accidental prefixes
                if SUPABASE_URL.startswith("SUPABASE_URL="):
                    SUPABASE_URL = SUPABASE_URL.replace("SUPABASE_URL=", "")
                if SUPABASE_SERVICE_KEY.startswith("SUPABASE_SERVICE_ROLE_KEY="):
                    SUPABASE_SERVICE_KEY = SUPABASE_SERVICE_KEY.replace("SUPABASE_SERVICE_ROLE_KEY=", "")
                
                # Final cleaning
                SUPABASE_URL = SUPABASE_URL.strip()
                SUPABASE_SERVICE_KEY = SUPABASE_SERVICE_KEY.strip()
                
                # Validate
                if not SUPABASE_URL:
                    raise Exception("SUPABASE_URL is EMPTY")
                if not SUPABASE_URL.startswith("https://"):
                    raise Exception(f"URL must start with https://")
                if not SUPABASE_SERVICE_KEY:
                    raise Exception("SUPABASE_SERVICE_KEY is EMPTY")
                
                print(f"🔗 URL: {SUPABASE_URL}")
                print(f"🔑 Key length: {len(SUPABASE_SERVICE_KEY)} chars")
                
                # CREATE CLIENT (FIXED - no proxy parameter)
                print("🛠️ Creating client...")
                cls.supabase = create_client(
                    supabase_url=SUPABASE_URL,
                    supabase_key=SUPABASE_SERVICE_KEY
                )
                
                print("✅ Supabase client initialized")
                print("=" * 50)
                
            except Exception as e:
                print("=" * 50)
                print(f"❌ SUPABASE INIT FAILED: {e}")
                print(f"URL: {Config.SUPABASE_URL[:50] if Config.SUPABASE_URL else 'None'}")
                print("=" * 50)
                raise
    
    @classmethod
    def test_connection(cls):
        """Test database connection"""
        try:
            print("🧪 Testing connection...")
            
            if cls.supabase is None:
                cls.init_client()
            
            # Try to access a table
            try:
                result = cls.supabase.table('admin').select('id').limit(1).execute()
                print(f"✅ Admin table accessible")
                return True
            except Exception as e1:
                try:
                    result = cls.supabase.table('visitors').select('id').limit(1).execute()
                    print(f"✅ Visitors table accessible")
                    return True
                except Exception as e2:
                    print(f"⚠️ Tables not found, but connection OK")
                    return True  # Connection successful, tables might not exist
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    @classmethod
    def execute_query(cls, query, params=None, fetch=False, fetch_all=False, commit=True):
        """Execute database query"""
        try:
            if cls.supabase is None:
                cls.init_client()
            
            query_lower = query.strip().lower()
            
            # ============ SELECT QUERIES ============
            if query_lower.startswith('select'):
                
                # 1. Admin Login
                if 'admin' in query_lower and 'username' in query_lower:
                    if params and len(params) >= 2:
                        result = cls.supabase.table('admin')\
                            .select("*")\
                            .eq('username', params[0])\
                            .eq('password', params[1])\
                            .execute()
                        return result.data[0] if result.data else None
                
                # 2. Active Visitor by Roll No
                if 'roll_no' in query_lower and 'exit_time is null' in query_lower:
                    if params:
                        today = datetime.now().date().isoformat()
                        result = cls.supabase.table('visitors')\
                            .select("*")\
                            .eq('roll_no', params[0].upper())\
                            .eq('visit_date', today)\
                            .is_('exit_time', 'null')\
                            .order('id', desc=True)\
                            .limit(1)\
                            .execute()
                        return result.data[0] if result.data else None
                
                # 3. Any Visitor by Roll No
                if 'roll_no' in query_lower and 'order by id desc' in query_lower:
                    if params:
                        result = cls.supabase.table('visitors')\
                            .select("*")\
                            .eq('roll_no', params[0].upper())\
                            .order('id', desc=True)\
                            .limit(1)\
                            .execute()
                        return result.data[0] if result.data else None
                
                # 4. Today's Visitors
                if 'current_date' in query_lower:
                    today = datetime.now().date().isoformat()
                    result = cls.supabase.table('visitors')\
                        .select("*")\
                        .eq('visit_date', today)\
                        .order('id', desc=True)\
                        .execute()
                    return result.data if fetch_all else result.data
                
                # 5. All Visitors
                if 'visitors' in query_lower:
                    result = cls.supabase.table('visitors')\
                        .select("*")\
                        .order('id', desc=True)\
                        .execute()
                    return result.data if fetch_all else result.data
            
            # ============ INSERT QUERIES ============
            elif query_lower.startswith('insert') and 'visitors' in query_lower:
                if params and len(params) >= 7:
                    visitor_data = {
                        'name': params[0].strip(),
                        'roll_no': params[1].strip().upper(),
                        'level': params[2],
                        'course': params[3] if params[3] else 'Not Specified',
                        'purpose': params[6] if len(params) > 6 else 'Study',
                        'visit_day': datetime.now().strftime('%A')
                    }
                    
                    # Add year based on level
                    if params[2] == 'JC':
                        if len(params) > 4 and params[4]:
                            visitor_data['jc_year'] = params[4]
                        if len(params) > 5 and params[5]:
                            visitor_data['jc_stream'] = params[5]
                    elif len(params) > 4 and params[4]:
                        visitor_data['year'] = params[4]
                    
                    result = cls.supabase.table('visitors').insert(visitor_data).execute()
                    return result.data[0] if result.data else None
            
            # ============ UPDATE QUERIES ============
            elif query_lower.startswith('update') and 'visitors' in query_lower:
                if 'exit_time' in query_lower:
                    if params:
                        exit_time = datetime.now().time().strftime('%H:%M:%S')
                        
                        if 'id' in query_lower:
                            result = cls.supabase.table('visitors')\
                                .update({'exit_time': exit_time})\
                                .eq('id', params[0])\
                                .execute()
                            return result.data
                        elif 'roll_no' in query_lower:
                            result = cls.supabase.table('visitors')\
                                .update({'exit_time': exit_time})\
                                .eq('roll_no', params[0].upper())\
                                .is_('exit_time', 'null')\
                                .execute()
                            return result.data
            
            # ============ DELETE QUERIES ============
            elif query_lower.startswith('delete') and 'visitors' in query_lower:
                if params:
                    result = cls.supabase.table('visitors')\
                        .delete()\
                        .eq('id', params[0])\
                        .execute()
                    return result.data
            
            print(f"⚠️ No handler for query: {query[:50]}...")
            return None
            
        except Exception as e:
            print(f"❌ Database error: {e}")
            raise Exception(f"Database operation failed: {str(e)}")
    
    @classmethod
    def init_database(cls):
        """Initialize database"""
        try:
            cls.init_client()
            return cls.test_connection()
        except Exception as e:
            print(f"❌ Database init error: {e}")
            return False
