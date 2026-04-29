import os
import requests
import json
from datetime import datetime, timezone, timedelta
from backend.config import Config

class SupabaseDirect:
    """Direct HTTP interface to Supabase - NO PACKAGE DEPENDENCIES"""
    
    @classmethod
    def _get_headers(cls):
        """Get headers for Supabase API"""
        return {
            'apikey': Config.SUPABASE_KEY,
            'Authorization': f'Bearer {Config.SUPABASE_SERVICE_KEY}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        }
    
    @classmethod
    def _get_indian_time(cls):
        """Get current Indian Standard Time (IST)"""
        # Get UTC time
        utc_now = datetime.now(timezone.utc)
        # Convert to IST (UTC + 5 hours 30 minutes)
        ist_now = utc_now + timedelta(hours=5, minutes=30)
        return ist_now
    
    @classmethod
    def execute_query(cls, query, params=None, fetch=False, fetch_all=False, commit=True):
        """Compatibility method to match old Database interface"""
        try:
            query_lower = query.strip().lower()
            
            # ============ ADMIN LOGIN ============
            if 'admin' in query_lower and 'username' in query_lower and 'password' in query_lower:
                if params and len(params) >= 2:
                    return cls.admin_login(params[0], params[1])
            
            # ============ INSERT VISITOR ============
            elif 'insert into visitors' in query_lower:
                if params:
                    visitor_data = {}
                    
                    if len(params) >= 11:  # Full visitor data
                        visitor_data = {
                            'name': str(params[0]).strip(),
                            'roll_no': str(params[1]).strip().upper(),
                            'level': str(params[2]),
                            'course': str(params[3]) if params[3] else 'Not Specified',
                            'purpose': str(params[6]) if len(params) > 6 else 'Study'
                        }
                        
                        # Handle year fields
                        if params[2] == 'JC':
                            if len(params) > 4 and params[4]:
                                visitor_data['jc_year'] = str(params[4])
                            if len(params) > 5 and params[5]:
                                visitor_data['jc_stream'] = str(params[5])
                        else:
                            if len(params) > 4 and params[4]:
                                visitor_data['year'] = str(params[4])
                    
                    return cls.insert_visitor(visitor_data)
            
            # ============ GET VISITORS ============
            elif 'select * from visitors' in query_lower:
                if 'current_date' in query_lower:
                    return cls.get_today_visitors()
                elif 'between' in query_lower and params and len(params) >= 2:
                    return cls.get_visitors_by_date_range(params[0], params[1])
                else:
                    return cls.get_all_visitors()
            
            # ============ UPDATE EXIT TIME ============
            elif 'update visitors set exit_time' in query_lower:
                if params:
                    if 'id' in query_lower:
                        return cls.update_exit_by_id(params[0])
                    elif 'roll_no' in query_lower:
                        return cls.update_exit_by_rollno(params[0])
            
            # ============ DELETE VISITOR ============
            elif 'delete from visitors' in query_lower and params:
                return cls.delete_visitor(params[0])
            
            print(f"⚠️ Query not handled: {query[:100]}...")
            return None if fetch else []
            
        except Exception as e:
            print(f"❌ Database operation failed: {e}")
            raise Exception(f"Database operation failed: {str(e)}")
    
    @classmethod
    def admin_login(cls, username, password):
        """Admin login using direct API"""
        try:
            url = f"{Config.SUPABASE_URL}/rest/v1/admin"
            params = {
                'username': f'eq.{username}',
                'password': f'eq.{password}',
                'select': '*'
            }
            
            response = requests.get(url, headers=cls._get_headers(), params=params)
            
            if response.status_code == 200:
                data = response.json()
                return data[0] if data else None
            return None
            
        except Exception as e:
            print(f"❌ Admin login error: {e}")
            return None
    
    @classmethod
    def insert_visitor(cls, visitor_data):
        """Insert visitor record with INDIAN TIME (IST)"""
        try:
            url = f"{Config.SUPABASE_URL}/rest/v1/visitors"
            
            # Get Indian Standard Time
            ist_now = cls._get_indian_time()
            
            # Prepare data with Indian time
            data = {
                'name': visitor_data.get('name', '').strip(),
                'roll_no': visitor_data.get('roll_no', '').strip().upper(),
                'level': visitor_data.get('level', ''),
                'course': visitor_data.get('course', 'Not Specified'),
                'purpose': visitor_data.get('purpose', 'Study'),
                'visit_day': ist_now.strftime('%A'),  # Monday, Tuesday, etc.
                'entry_time': ist_now.strftime('%H:%M:%S'),  # HH:MM:SS format
                'visit_date': ist_now.date().isoformat()  # YYYY-MM-DD format
            }
            
            print(f"🇮🇳 INDIAN TIME SET: {data['entry_time']} IST on {data['visit_date']}")
            
            # Add year based on level
            if visitor_data.get('level') == 'JC':
                if 'jc_year' in visitor_data:
                    data['jc_year'] = visitor_data['jc_year']
                if 'jc_stream' in visitor_data:
                    data['jc_stream'] = visitor_data['jc_stream']
            elif 'year' in visitor_data:
                data['year'] = visitor_data['year']
            
            # Send to Supabase
            response = requests.post(
                url, 
                headers=cls._get_headers(),
                json=data
            )
            
            if response.status_code == 201:
                print(f"✅ Visitor inserted successfully with Indian time")
                return response.json()[0]
            else:
                print(f"❌ Insert failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Insert visitor error: {e}")
            return None
    
    @classmethod
    def get_active_visitor_by_rollno(cls, roll_no):
        """Get active visitor by roll number"""
        try:
            url = f"{Config.SUPABASE_URL}/rest/v1/visitors"
            # Use Indian date for today
            ist_now = cls._get_indian_time()
            today = ist_now.date().isoformat()
            
            params = {
                'roll_no': f'eq.{roll_no.upper()}',
                'visit_date': f'eq.{today}',
                'exit_time': f'is.null',
                'select': '*',
                'order': 'id.desc',
                'limit': '1'
            }
            
            response = requests.get(url, headers=cls._get_headers(), params=params)
            
            if response.status_code == 200:
                data = response.json()
                return data[0] if data else None
            return None
            
        except Exception as e:
            print(f"❌ Get active visitor error: {e}")
            return None
    
    @classmethod
    def update_exit_by_id(cls, visitor_id):
        """Update exit time by ID with INDIAN TIME"""
        try:
            url = f"{Config.SUPABASE_URL}/rest/v1/visitors"
            params = {'id': f'eq.{visitor_id}'}
            
            # Use Indian time for exit
            ist_now = cls._get_indian_time()
            exit_time = ist_now.strftime('%H:%M:%S')
            
            data = {
                'exit_time': exit_time
            }
            
            print(f"🕐 Setting exit time: {exit_time} IST")
            
            response = requests.patch(
                url,
                headers=cls._get_headers(),
                params=params,
                json=data
            )
            
            if response.status_code == 200:
                return response.json()[0] if response.json() else None
            return None
            
        except Exception as e:
            print(f"❌ Update exit by ID error: {e}")
            return None
    
    @classmethod
    def update_exit_by_rollno(cls, roll_no):
        """Update exit time by roll number"""
        try:
            url = f"{Config.SUPABASE_URL}/rest/v1/visitors"
            ist_now = cls._get_indian_time()
            today = ist_now.date().isoformat()
            
            # First get active visitor
            params = {
                'roll_no': f'eq.{roll_no.upper()}',
                'visit_date': f'eq.{today}',
                'exit_time': f'is.null',
                'select': 'id',
                'limit': '1'
            }
            
            response = requests.get(url, headers=cls._get_headers(), params=params)
            
            if response.status_code == 200 and response.json():
                visitor_id = response.json()[0]['id']
                return cls.update_exit_by_id(visitor_id)
            
            return None
            
        except Exception as e:
            print(f"❌ Update exit by rollno error: {e}")
            return None
    
    @classmethod
    def get_today_visitors(cls):
        """Get today's visitors (Indian date)"""
        try:
            url = f"{Config.SUPABASE_URL}/rest/v1/visitors"
            ist_now = cls._get_indian_time()
            today = ist_now.date().isoformat()
            
            params = {
                'visit_date': f'eq.{today}',
                'select': '*',
                'order': 'id.desc'
            }
            
            response = requests.get(url, headers=cls._get_headers(), params=params)
            
            if response.status_code == 200:
                return response.json()
            return []
            
        except Exception as e:
            print(f"❌ Get today visitors error: {e}")
            return []
    
    @classmethod
    def get_all_visitors(cls):
        """Get all visitors"""
        try:
            url = f"{Config.SUPABASE_URL}/rest/v1/visitors"
            
            params = {
                'select': '*',
                'order': 'id.desc'
            }
            
            response = requests.get(url, headers=cls._get_headers(), params=params)
            
            if response.status_code == 200:
                return response.json()
            return []
            
        except Exception as e:
            print(f"❌ Get all visitors error: {e}")
            return []
    
    @classmethod
    def get_visitors_by_date_range(cls, start_date, end_date):
        """Get visitors by date range"""
        try:
            url = f"{Config.SUPABASE_URL}/rest/v1/visitors"
            
            params = {
                'visit_date': f'gte.{start_date}',
                'visit_date': f'lte.{end_date}',
                'select': '*',
                'order': 'visit_date.desc,id.desc'
            }
            
            response = requests.get(url, headers=cls._get_headers(), params=params)
            
            if response.status_code == 200:
                return response.json()
            return []
            
        except Exception as e:
            print(f"❌ Get visitors by date range error: {e}")
            return []
    
    @classmethod
    def delete_visitor(cls, visitor_id):
        """Delete visitor"""
        try:
            url = f"{Config.SUPABASE_URL}/rest/v1/visitors"
            params = {'id': f'eq.{visitor_id}'}
            
            response = requests.delete(url, headers=cls._get_headers(), params=params)
            
            if response.status_code == 204:
                return True
            return False
            
        except Exception as e:
            print(f"❌ Delete visitor error: {e}")
            return False
    
    @classmethod
    def test_connection(cls):
        """Test Supabase connection"""
        try:
            url = f"{Config.SUPABASE_URL}/rest/v1/"
            response = requests.get(url, headers=cls._get_headers())
            
            if response.status_code == 200:
                print("✅ Supabase API is accessible")
                return True
            else:
                print(f"❌ Supabase API error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False

    
    @classmethod
    def test_indian_time(cls):
        """Test Indian time function"""
        try:
            ist_now = cls._get_indian_time()
            print(f"🕐 INDIAN TIME TEST:")
            print(f"   IST Time: {ist_now.strftime('%H:%M:%S')}")
            print(f"   IST Date: {ist_now.date().isoformat()}")
            print(f"   IST Day:  {ist_now.strftime('%A')}")
            return True
        except Exception as e:
            print(f"❌ Time test failed: {e}")
            return False
    
    @classmethod
    def insert_teacher(cls, teacher_data):
        """Insert teacher visit record with INDIAN TIME (IST)"""
        try:
            url = f"{Config.SUPABASE_URL}/rest/v1/teachers"
            
            ist_now = cls._get_indian_time()
            
            data = {
                'name': teacher_data.get('name', '').strip(),
                'employee_id': teacher_data.get('employee_id', '').strip().upper(),
                'designation': teacher_data.get('designation', ''),
                'nature_of_work': teacher_data.get('nature_of_work', ''),
                'purpose': teacher_data.get('purpose', 'Library Work'),
                'notes': teacher_data.get('notes', ''),
                'entry_time': ist_now.strftime('%H:%M:%S'),
                'visit_date': ist_now.date().isoformat(),
                'visit_day': ist_now.strftime('%A')
            }
            
            print(f"👨‍🏫 TEACHER ENTRY: {data['name']} at {data['entry_time']} IST")
            
            response = requests.post(
                url, 
                headers=cls._get_headers(),
                json=data
            )
            
            if response.status_code == 201:
                print(f"✅ Teacher inserted successfully")
                return response.json()[0]
            else:
                print(f"❌ Teacher insert failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Insert teacher error: {e}")
            return None

    @classmethod
    def get_active_teacher_by_employee_id(cls, employee_id):
        """Get active teacher by employee ID"""
        try:
            url = f"{Config.SUPABASE_URL}/rest/v1/teachers"
            ist_now = cls._get_indian_time()
            today = ist_now.date().isoformat()
            
            params = {
                'employee_id': f'eq.{employee_id.upper()}',
                'visit_date': f'eq.{today}',
                'exit_time': f'is.null',
                'select': '*',
                'order': 'id.desc',
                'limit': '1'
            }
            
            response = requests.get(url, headers=cls._get_headers(), params=params)
            
            if response.status_code == 200:
                data = response.json()
                return data[0] if data else None
            return None
            
        except Exception as e:
            print(f"❌ Get active teacher error: {e}")
            return None

    @classmethod
    def update_teacher_exit_by_id(cls, teacher_id):
        """Update exit time for teacher by ID"""
        try:
            url = f"{Config.SUPABASE_URL}/rest/v1/teachers"
            params = {'id': f'eq.{teacher_id}'}
            
            ist_now = cls._get_indian_time()
            exit_time = ist_now.strftime('%H:%M:%S')
            
            data = {'exit_time': exit_time}
            
            print(f"👨‍🏫 TEACHER EXIT: ID {teacher_id} at {exit_time} IST")
            
            response = requests.patch(
                url,
                headers=cls._get_headers(),
                params=params,
                json=data
            )
            
            if response.status_code == 200:
                return response.json()[0] if response.json() else None
            return None
            
        except Exception as e:
            print(f"❌ Update teacher exit error: {e}")
            return None

    @classmethod
    def get_all_teachers(cls):
        """Get all teacher visits"""
        try:
            url = f"{Config.SUPABASE_URL}/rest/v1/teachers"
            params = {'select': '*', 'order': 'id.desc'}
            
            response = requests.get(url, headers=cls._get_headers(), params=params)
            
            if response.status_code == 200:
                return response.json()
            return []
            
        except Exception as e:
            print(f"❌ Get all teachers error: {e}")
            return []

    @classmethod
    def get_teachers_by_date_range(cls, start_date, end_date):
        """Get teachers by date range"""
        try:
            url = f"{Config.SUPABASE_URL}/rest/v1/teachers"
            params = {
                'visit_date': f'gte.{start_date}',
                'visit_date': f'lte.{end_date}',
                'select': '*',
                'order': 'visit_date.desc,id.desc'
            }
            
            response = requests.get(url, headers=cls._get_headers(), params=params)
            
            if response.status_code == 200:
                return response.json()
            return []
            
        except Exception as e:
            print(f"❌ Get teachers by date range error: {e}")
            return []

    @classmethod
    def get_today_teachers(cls):
        """Get today's teachers"""
        try:
            ist_now = cls._get_indian_time()
            today = ist_now.date().isoformat()
            
            url = f"{Config.SUPABASE_URL}/rest/v1/teachers"
            params = {
                'visit_date': f'eq.{today}',
                'select': '*',
                'order': 'id.desc'
            }
            
            response = requests.get(url, headers=cls._get_headers(), params=params)
            
            if response.status_code == 200:
                return response.json()
            return []
            
        except Exception as e:
            print(f"❌ Get today teachers error: {e}")
            return []
        
    @classmethod
    def auto_exit_overdue_visitors(cls):
        """Automatically mark exit for visitors still inside after 4 PM"""
        try:
            ist_now = cls._get_indian_time()
            current_hour = ist_now.hour
            
            # Only run between 4:00 PM and 4:30 PM
            if current_hour < 16 or current_hour > 16:
                return 0
            
            today = ist_now.date().isoformat()
            closing_time = "16:00:00"
            
            url = f"{Config.SUPABASE_URL}/rest/v1/visitors"
            params = {
                'visit_date': f'eq.{today}',
                'exit_time': 'is.null',
                'select': 'id'
            }
            
            response = requests.get(url, headers=cls._get_headers(), params=params)
            
            if response.status_code == 200:
                active_visitors = response.json()
                
                if not active_visitors:
                    return 0
                
                updated_count = 0
                for visitor in active_visitors:
                    url_update = f"{Config.SUPABASE_URL}/rest/v1/visitors"
                    params_update = {'id': f'eq.{visitor["id"]}'}
                    data = {'exit_time': closing_time}
                    
                    update_response = requests.patch(
                        url_update,
                        headers=cls._get_headers(),
                        params=params_update,
                        json=data
                    )
                    
                    if update_response.status_code == 200:
                        updated_count += 1
                
                print(f"🕐 AUTO-EXIT: Marked {updated_count} visitors as exited at 4 PM")
                return updated_count
            
            return 0
            
        except Exception as e:
            print(f"❌ Auto-exit visitor error: {e}")
            return 0

    @classmethod
def delete_teacher(cls, teacher_id):
    """Delete teacher record"""
    try:
        url = f"{Config.SUPABASE_URL}/rest/v1/teachers"
        params = {'id': f'eq.{teacher_id}'}
        
        response = requests.delete(url, headers=cls._get_headers(), params=params)
        
        if response.status_code == 204:
            print(f"✅ Teacher {teacher_id} deleted successfully")
            return True
        return False
        
    except Exception as e:
        print(f"❌ Delete teacher error: {e}")
        return False
    
    @classmethod
    def auto_exit_overdue_teachers(cls):
        """Automatically mark exit for teachers still inside after 4 PM"""
        try:
            ist_now = cls._get_indian_time()
            current_hour = ist_now.hour
            
            # Only run between 4:00 PM and 4:30 PM
            if current_hour < 16 or current_hour > 16:
                return 0
            
            today = ist_now.date().isoformat()
            closing_time = "16:00:00"
            
            url = f"{Config.SUPABASE_URL}/rest/v1/teachers"
            params = {
                'visit_date': f'eq.{today}',
                'exit_time': 'is.null',
                'select': 'id'
            }
            
            response = requests.get(url, headers=cls._get_headers(), params=params)
            
            if response.status_code == 200:
                active_teachers = response.json()
                
                if not active_teachers:
                    return 0
                
                updated_count = 0
                for teacher in active_teachers:
                    url_update = f"{Config.SUPABASE_URL}/rest/v1/teachers"
                    params_update = {'id': f'eq.{teacher["id"]}'}
                    data = {'exit_time': closing_time}
                    
                    update_response = requests.patch(
                        url_update,
                        headers=cls._get_headers(),
                        params=params_update,
                        json=data
                    )
                    
                    if update_response.status_code == 200:
                        updated_count += 1
                
                print(f"🕐 AUTO-EXIT: Marked {updated_count} teachers as exited at 4 PM")
                return updated_count
            
            return 0
            
        except Exception as e:
            print(f"❌ Auto-exit teacher error: {e}")
            return 0
