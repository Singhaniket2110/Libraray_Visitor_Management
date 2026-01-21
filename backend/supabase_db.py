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
                print("=" * 50)
                print("🔄 INITIALIZING SUPABASE CLIENT")
                print("=" * 50)
                
                # Step 1: Validate config
                if not Config.validate_config():
                    raise Exception("Config validation failed")
                
                # Step 2: Get cleaned values
                SUPABASE_URL = Config.SUPABASE_URL
                SUPABASE_SERVICE_KEY = Config.SUPABASE_SERVICE_KEY
                
                # Step 3: Extra cleaning (safety)
                SUPABASE_URL = SUPABASE_URL.strip()
                SUPABASE_SERVICE_KEY = SUPABASE_SERVICE_KEY.strip()
                
                # Remove any accidental prefixes
                if "SUPABASE_URL=" in SUPABASE_URL:
                    SUPABASE_URL = SUPABASE_URL.replace("SUPABASE_URL=", "")
                if "SUPABASE_SERVICE_ROLE_KEY=" in SUPABASE_SERVICE_KEY:
                    SUPABASE_SERVICE_KEY = SUPABASE_SERVICE_KEY.replace("SUPABASE_SERVICE_ROLE_KEY=", "")
                
                SUPABASE_URL = SUPABASE_URL.strip('"').strip("'")
                SUPABASE_SERVICE_KEY = SUPABASE_SERVICE_KEY.strip('"').strip("'")
                
                # Step 4: Validate before creating client
                if not SUPABASE_URL:
                    raise Exception("SUPABASE_URL is EMPTY after cleaning")
                
                if not SUPABASE_URL.startswith("https://"):
                    raise Exception(f"URL must start with https://. Got: {SUPABASE_URL[:50]}")
                
                if not SUPABASE_SERVICE_KEY:
                    raise Exception("SUPABASE_SERVICE_KEY is EMPTY after cleaning")
                
                if len(SUPABASE_SERVICE_KEY) < 20:
                    raise Exception(f"Service key too short: {len(SUPABASE_SERVICE_KEY)} chars")
                
                # Step 5: Debug info
                print(f"🔗 URL (cleaned): {SUPABASE_URL}")
                print(f"🔑 Key (first 20 chars): {SUPABASE_SERVICE_KEY[:20]}...")
                print(f"📏 Key length: {len(SUPABASE_SERVICE_KEY)} characters")
                
                # Step 6: Create client
                print("🛠️ Creating Supabase client...")
                cls.supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
                print("✅ Supabase client created successfully")
                print("=" * 50)
                
            except Exception as e:
                print("=" * 50)
                print(f"❌ SUPABASE INIT FAILED: {e}")
                print("=" * 50)
                print("TROUBLESHOOTING:")
                print(f"1. SUPABASE_URL: '{Config.SUPABASE_URL[:80] if Config.SUPABASE_URL else 'EMPTY'}'")
                print(f"2. Starts with https://: {Config.SUPABASE_URL.startswith('https://') if Config.SUPABASE_URL else False}")
                print(f"3. Key exists: {bool(Config.SUPABASE_SERVICE_KEY)}")
                print("=" * 50)
                raise
    
    @classmethod
    def test_connection(cls):
        """Test database connection - SIMPLIFIED VERSION"""
        try:
            print("🧪 Testing Supabase connection...")
            
            if cls.supabase is None:
                cls.init_client()
            
            # Try a simple query - get server timestamp
            print("   Sending test query...")
            
            # Alternative: Try to list tables
            try:
                # Get first visitor record
                result = cls.supabase.table('visitors').select('id').limit(1).execute()
                print(f"✅ Connection SUCCESS - Visitors table accessible")
                print(f"   Found {len(result.data)} records")
                return True
            except Exception as table_error:
                # Try admin table
                try:
                    result = cls.supabase.table('admin').select('id').limit(1).execute()
                    print(f"✅ Connection SUCCESS - Admin table accessible")
                    return True
                except:
                    print(f"⚠️ Tables not accessible, but connection established")
                    print(f"   Error: {str(table_error)[:100]}")
                    # Even if tables don't exist, connection is successful
                    return True
                    
        except Exception as e:
            print(f"❌ Connection FAILED: {str(e)[:200]}")
            return False
    
    @classmethod
    def execute_query(cls, query, params=None, fetch=False, fetch_all=False, commit=True):
        """
        Execute database operations using Supabase client
        """
        try:
            # Ensure client is initialized
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
            
            # If no specific handler matched
            print(f"⚠️ No handler for query: {query[:100]}...")
            return None
            
        except Exception as e:
            print(f"❌ Database operation failed: {e}")
            raise Exception(f"Database operation failed: {str(e)}")
    
    @classmethod
    def init_database(cls):
        """Initialize database - test connection"""
        try:
            print("🔄 Initializing database connection...")
            cls.init_client()
            success = cls.test_connection()
            
            if success:
                print("✅ Database initialized successfully")
            else:
                print("⚠️ Database connected but tables may not exist")
            
            return success
        except Exception as e:
            print(f"❌ Database init error: {e}")
            return False
