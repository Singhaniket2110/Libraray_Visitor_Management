import os
from supabase import create_client, Client
from datetime import datetime

class SupabaseDatabase:
    supabase: Client = None
    
    @classmethod
    def init_client(cls):
        """Initialize Supabase client with SERVICE ROLE key"""
        if cls.supabase is None:
            try:
                # Use SERVICE ROLE KEY for admin operations
                SUPABASE_URL = "https://wboxcfmizfkapdslzkks.supabase.co"
                SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Indib3hjZm1pemZrYXBkc2x6a2tzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczNzQ0ODMxNywiZXhwIjoyMDUzMDI0MzE3fQ.DOYTKlg3bE2znm4AWQgxxQ_-vPzBOAO"
                
                cls.supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
                print("✅ Supabase client initialized")
            except Exception as e:
                print(f"❌ Supabase init failed: {e}")
                raise
    
    @classmethod
    def test_connection(cls):
        """Test database connection"""
        try:
            if cls.supabase is None:
                cls.init_client()
            
            # Test query - try to fetch from visitors table
            result = cls.supabase.table('visitors').select("id").limit(1).execute()
            print(f"✅ Connection test passed - found {len(result.data)} records")
            return True
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return False
    
    @classmethod
    def execute_query(cls, query, params=None, fetch=False, fetch_all=False, commit=True):
        """
        Execute database operations using Supabase client
        This is a compatibility layer for SQL-style queries
        """
        try:
            if cls.supabase is None:
                cls.init_client()
            
            query_lower = query.strip().lower()
            
            # ============ SELECT QUERIES ============
            if query_lower.startswith('select'):
                
                # Admin login check
                if 'admin' in query_lower and 'username' in query_lower:
                    username = params[0] if params else None
                    if username:
                        result = cls.supabase.table('admin').select("*").eq('username', username).execute()
                        if result.data and len(result.data) > 0:
                            # Check password match
                            password = params[1] if len(params) > 1 else None
                            if password and result.data[0].get('password') == password:
                                return result.data[0] if fetch else result.data
                        return None
                
                # Get active visitor by roll number
                if 'roll_no' in query_lower and 'exit_time is null' in query_lower:
                    roll_no = params[0] if params else None
                    if roll_no:
                        result = cls.supabase.table('visitors').select("*").eq('roll_no', roll_no.upper()).is_('exit_time', 'null').order('id', desc=True).limit(1).execute()
                        return result.data[0] if result.data else None
                
                # Get visitor by roll number (any)
                if 'roll_no' in query_lower and 'order by id desc' in query_lower:
                    roll_no = params[0] if params else None
                    if roll_no:
                        result = cls.supabase.table('visitors').select("*").eq('roll_no', roll_no.upper()).order('id', desc=True).limit(1).execute()
                        return result.data[0] if result.data else None
                
                # Get today's visitors
                if 'visit_date = current_date' in query_lower or 'current_date' in query_lower:
                    today = datetime.now().date().isoformat()
                    result = cls.supabase.table('visitors').select("*").eq('visit_date', today).order('id', desc=True).execute()
                    return result.data if fetch_all else result.data
                
                # Get visitors by date range
                if 'visit_date between' in query_lower:
                    start_date = params[0] if params else None
                    end_date = params[1] if len(params) > 1 else None
                    if start_date and end_date:
                        result = cls.supabase.table('visitors').select("*").gte('visit_date', start_date).lte('visit_date', end_date).order('visit_date', desc=True).execute()
                        return result.data if fetch_all else result.data
                
                # Generic SELECT from visitors with filters
                if 'visitors' in query_lower:
                    query_builder = cls.supabase.table('visitors').select("*")
                    
                    # Apply level filter
                    if params and 'level' in str(query_lower):
                        # Extract level from params if available
                        pass
                    
                    result = query_builder.order('id', desc=True).execute()
                    return result.data if fetch_all else (result.data[0] if result.data else None)
                
                # Default: get all from table
                table_name = cls._extract_table_name(query_lower)
                if table_name:
                    result = cls.supabase.table(table_name).select("*").execute()
                    return result.data if fetch_all else (result.data[0] if result.data else None)
            
            # ============ INSERT QUERIES ============
            elif query_lower.startswith('insert'):
                if 'visitors' in query_lower:
                    # Parse INSERT for visitors
                    if params and len(params) >= 7:
                        visitor_data = {
                            'name': params[0],
                            'roll_no': params[1].upper() if params[1] else None,
                            'level': params[2],
                            'course': params[3] if params[3] else 'Not Specified',
                            'purpose': params[6] if len(params) > 6 else 'Study',
                            'visit_day': params[7] if len(params) > 7 else datetime.now().strftime('%A')
                        }
                        
                        # Add optional fields
                        if len(params) > 4 and params[4]:
                            if params[2] == 'JC':
                                visitor_data['jc_year'] = params[4]
                            else:
                                visitor_data['year'] = params[4]
                        
                        if len(params) > 5 and params[5]:
                            visitor_data['jc_stream'] = params[5]
                        
                        result = cls.supabase.table('visitors').insert(visitor_data).execute()
                        return result.data[0] if result.data else None
            
            # ============ UPDATE QUERIES ============
            elif query_lower.startswith('update'):
                if 'visitors' in query_lower:
                    if 'exit_time' in query_lower:
                        # Mark exit
                        if params:
                            if 'roll_no' in query_lower:
                                # Update by roll_no
                                roll_no = params[0]
                                exit_time = datetime.now().time().isoformat()
                                result = cls.supabase.table('visitors').update({'exit_time': exit_time}).eq('roll_no', roll_no.upper()).is_('exit_time', 'null').execute()
                                return result.data
                            else:
                                # Update by ID
                                visitor_id = params[0]
                                exit_time = datetime.now().time().isoformat()
                                result = cls.supabase.table('visitors').update({'exit_time': exit_time}).eq('id', visitor_id).execute()
                                return result.data
            
            # ============ DELETE QUERIES ============
            elif query_lower.startswith('delete'):
                if 'visitors' in query_lower and params:
                    visitor_id = params[0]
                    result = cls.supabase.table('visitors').delete().eq('id', visitor_id).execute()
                    return result.data
            
            return None
            
        except Exception as e:
            print(f"❌ Database error: {e}")
            raise Exception(f"Database operation failed: {str(e)}")
    
    @classmethod
    def _extract_table_name(cls, query):
        """Extract table name from SQL query"""
        try:
            if 'from' in query:
                parts = query.split('from')[1].strip().split()
                return parts[0] if parts else None
        except:
            return None
    
    @classmethod
    def init_database(cls):
        """Initialize database - test connection"""
        try:
            cls.init_client()
            return cls.test_connection()
        except Exception as e:
            print(f"⚠️ Database init error: {e}")
            return False
