import os
from supabase import create_client, Client
from datetime import datetime
from backend.config import Config  # Import Config class

class SupabaseDatabase:
    supabase: Client = None
    
    @classmethod
    def init_client(cls):
        """Initialize Supabase client with SERVICE ROLE key"""
        if cls.supabase is None:
            try:
                # VALIDATE CONFIG FIRST
                if not Config.validate_config():
                    raise Exception("Configuration validation failed")
                
                # USE VALUES FROM Config CLASS (which reads from .env)
                SUPABASE_URL = Config.SUPABASE_URL
                SUPABASE_SERVICE_KEY = Config.SUPABASE_SERVICE_KEY
                
                if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
                    raise Exception(
                        f"Supabase credentials missing. URL: {bool(SUPABASE_URL)}, "
                        f"Key: {bool(SUPABASE_SERVICE_KEY)}"
                    )
                
                print(f"🔗 Connecting to Supabase: {SUPABASE_URL}")
                print(f"   Using Service Role Key: {SUPABASE_SERVICE_KEY[:20]}...")
                
                # Initialize client
                cls.supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
                print("✅ Supabase client initialized successfully")
                
            except Exception as e:
                print(f"❌ SUPABASE INIT FAILED: {e}")
                print("   Check your .env file credentials")
                raise
    
    @classmethod
    def test_connection(cls):
        """Test database connection"""
        try:
            if cls.supabase is None:
                cls.init_client()
            
            # Method 1: Try to list tables (simple test)
            print("🧪 Testing database connection...")
            
            # Try to access admin table first
            try:
                result = cls.supabase.table('admin').select("id").limit(1).execute()
                print(f"✅ Connection test passed - Admin table accessible")
                return True
            except Exception as table_error:
                print(f"⚠️ Admin table not accessible: {table_error}")
                
                # Try system table as fallback
                try:
                    result = cls.supabase.table('visitors').select("count").limit(1).execute()
                    print(f"✅ Visitors table accessible")
                    return True
                except:
                    print(f"⚠️ Testing with simple ping...")
                    
                    # Last resort: Just check if client responds
                    response = cls.supabase.auth.get_session()
                    print(f"✅ Supabase client responding")
                    return True
                    
        except Exception as e:
            print(f"❌ Connection test failed: {str(e)[:200]}")
            return False
    
    @classmethod
    def execute_query(cls, query, params=None, fetch=False, fetch_all=False, commit=True):
        """
        Execute database operations using Supabase client
        Compatible with SQL-style queries from your models
        """
        try:
            if cls.supabase is None:
                cls.init_client()
            
            query_lower = query.strip().lower()
            
            # ============ SELECT QUERIES ============
            if query_lower.startswith('select'):
                
                # 1. Admin Login Query
                # SELECT * FROM admin WHERE username = %s AND password = %s
                if 'admin' in query_lower and 'username' in query_lower and 'password' in query_lower:
                    if params and len(params) >= 2:
                        username = params[0]
                        password = params[1]
                        result = cls.supabase.table('admin')\
                            .select("*")\
                            .eq('username', username)\
                            .eq('password', password)\
                            .execute()
                        return result.data[0] if result.data else None
                
                # 2. Get Active Visitor by Roll No
                # SELECT * FROM visitors WHERE roll_no = %s AND exit_time IS NULL AND visit_date = CURRENT_DATE
                if 'roll_no' in query_lower and 'exit_time is null' in query_lower and 'current_date' in query_lower:
                    if params:
                        roll_no = params[0].upper()
                        today = datetime.now().date().isoformat()
                        result = cls.supabase.table('visitors')\
                            .select("*")\
                            .eq('roll_no', roll_no)\
                            .eq('visit_date', today)\
                            .is_('exit_time', 'null')\
                            .order('id', desc=True)\
                            .limit(1)\
                            .execute()
                        return result.data[0] if result.data else None
                
                # 3. Get Any Visitor by Roll No (even exited)
                # SELECT * FROM visitors WHERE roll_no = %s ORDER BY id DESC LIMIT 1
                if 'roll_no' in query_lower and 'order by id desc' in query_lower and 'exit_time is null' not in query_lower:
                    if params:
                        roll_no = params[0].upper()
                        result = cls.supabase.table('visitors')\
                            .select("*")\
                            .eq('roll_no', roll_no)\
                            .order('id', desc=True)\
                            .limit(1)\
                            .execute()
                        return result.data[0] if result.data else None
                
                # 4. Get Today's Visitors
                # SELECT * FROM visitors WHERE visit_date = CURRENT_DATE ORDER BY id DESC
                if 'visit_date = current_date' in query_lower or ('current_date' in query_lower and 'between' not in query_lower):
                    today = datetime.now().date().isoformat()
                    result = cls.supabase.table('visitors')\
                        .select("*")\
                        .eq('visit_date', today)\
                        .order('id', desc=True)\
                        .execute()
                    return result.data if fetch_all else result.data
                
                # 5. Get Visitors by Date Range
                # SELECT * FROM visitors WHERE visit_date BETWEEN %s AND %s
                if 'visit_date between' in query_lower or 'between' in query_lower:
                    if params and len(params) >= 2:
                        start_date = params[0]
                        end_date = params[1]
                        result = cls.supabase.table('visitors')\
                            .select("*")\
                            .gte('visit_date', start_date)\
                            .lte('visit_date', end_date)\
                            .order('visit_date', desc=True)\
                            .execute()
                        return result.data if fetch_all else result.data
                
                # 6. Get Filtered Visitors (with level and/or date)
                # SELECT * FROM visitors WHERE 1=1 AND level = %s AND visit_date = %s ORDER BY id DESC
                if 'visitors' in query_lower and 'where' in query_lower:
                    query_builder = cls.supabase.table('visitors').select("*")
                    
                    if params:
                        # Apply filters based on params
                        for i, param in enumerate(params):
                            if param and 'level' in query_lower:
                                query_builder = query_builder.eq('level', param)
                            elif param and (i > 0 or 'date' in query_lower):
                                # Date filter
                                try:
                                    datetime.fromisoformat(str(param))
                                    query_builder = query_builder.eq('visit_date', param)
                                except:
                                    pass
                    
                    result = query_builder.order('id', desc=True).execute()
                    return result.data if fetch_all else result.data
                
                # 7. Get All Visitors
                # SELECT * FROM visitors ORDER BY id DESC
                if 'visitors' in query_lower:
                    result = cls.supabase.table('visitors')\
                        .select("*")\
                        .order('id', desc=True)\
                        .execute()
                    return result.data if fetch_all else result.data
                
                # 8. Test Query (SELECT NOW())
                if 'now()' in query_lower or 'current_time' in query_lower:
                    return {'time': datetime.now().isoformat()}
            
            # ============ INSERT QUERIES ============
            elif query_lower.startswith('insert'):
                if 'visitors' in query_lower:
                    # INSERT INTO visitors (...) VALUES (...)
                    if params and len(params) >= 7:
                        visitor_data = {
                            'name': params[0].strip(),
                            'roll_no': params[1].strip().upper(),
                            'level': params[2],
                            'course': params[3] if params[3] else 'Not Specified',
                            'purpose': params[6] if len(params) > 6 else 'Study',
                            'visit_day': params[7] if len(params) > 7 else datetime.now().strftime('%A')
                        }
                        
                        # Handle year fields based on level
                        if params[2] == 'JC':
                            if len(params) > 4 and params[4]:
                                visitor_data['jc_year'] = params[4]
                            if len(params) > 5 and params[5]:
                                visitor_data['jc_stream'] = params[5]
                        else:
                            if len(params) > 4 and params[4]:
                                visitor_data['year'] = params[4]
                        
                        # Handle entry_time if provided
                        if len(params) > 8 and params[8]:
                            visitor_data['entry_time'] = params[8]
                        
                        # Handle visit_date if provided
                        if len(params) > 9 and params[9]:
                            visitor_data['visit_date'] = params[9]
                        
                        # Handle exit_time if provided
                        if len(params) > 10 and params[10]:
                            visitor_data['exit_time'] = params[10]
                        
                        result = cls.supabase.table('visitors').insert(visitor_data).execute()
                        return result.data[0] if result.data else None
            
            # ============ UPDATE QUERIES ============
            elif query_lower.startswith('update'):
                if 'visitors' in query_lower and 'exit_time' in query_lower:
                    # UPDATE visitors SET exit_time = CURRENT_TIME WHERE ...
                    
                    if 'id' in query_lower and params:
                        # Update by ID
                        visitor_id = params[0]
                        exit_time = datetime.now().time().strftime('%H:%M:%S')
                        result = cls.supabase.table('visitors')\
                            .update({'exit_time': exit_time})\
                            .eq('id', visitor_id)\
                            .execute()
                        return result.data
                    
                    elif 'roll_no' in query_lower and params:
                        # Update by roll_no
                        roll_no = params[0].upper()
                        exit_time = params[1] if len(params) > 1 else datetime.now().time().strftime('%H:%M:%S')
                        result = cls.supabase.table('visitors')\
                            .update({'exit_time': exit_time})\
                            .eq('roll_no', roll_no)\
                            .is_('exit_time', 'null')\
                            .execute()
                        return result.data
            
            # ============ DELETE QUERIES ============
            elif query_lower.startswith('delete'):
                if 'visitors' in query_lower and params:
                    # DELETE FROM visitors WHERE id = %s
                    visitor_id = params[0]
                    result = cls.supabase.table('visitors')\
                        .delete()\
                        .eq('id', visitor_id)\
                        .execute()
                    return result.data
            
            return None
            
        except Exception as e:
            print(f"❌ Database error: {e}")
            raise Exception(f"Database operation failed: {str(e)}")
    
    @classmethod
    def init_database(cls):
        """Initialize database - test connection"""
        try:
            cls.init_client()
            return cls.test_connection()
        except Exception as e:
            print(f"⚠️ Database init error: {e}")
            return False
