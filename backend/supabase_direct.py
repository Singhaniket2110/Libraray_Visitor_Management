import os
import requests
import json
from datetime import datetime
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
    def test_connection(cls):
        """Test Supabase connection"""
        try:
            print("🧪 Testing Supabase connection...")
            
            # Test 1: Check if URL is accessible
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
        """Insert visitor record"""
        try:
            url = f"{Config.SUPABASE_URL}/rest/v1/visitors"
            
            # Prepare data
            data = {
                'name': visitor_data.get('name', '').strip(),
                'roll_no': visitor_data.get('roll_no', '').strip().upper(),
                'level': visitor_data.get('level', ''),
                'course': visitor_data.get('course', 'Not Specified'),
                'purpose': visitor_data.get('purpose', 'Study'),
                'visit_day': datetime.now().strftime('%A'),
                'entry_time': datetime.now().time().strftime('%H:%M:%S'),
                'visit_date': datetime.now().date().isoformat()
            }
            
            # Add year based on level
            if visitor_data.get('level') == 'JC':
                if 'jc_year' in visitor_data:
                    data['jc_year'] = visitor_data['jc_year']
                if 'jc_stream' in visitor_data:
                    data['jc_stream'] = visitor_data['jc_stream']
            elif 'year' in visitor_data:
                data['year'] = visitor_data['year']
            
            response = requests.post(
                url, 
                headers=cls._get_headers(),
                json=data
            )
            
            if response.status_code == 201:
                return response.json()[0]
            else:
                print(f"❌ Insert failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Insert visitor error: {e}")
            return None
    
    @classmethod
    def get_active_visitor(cls, roll_no):
        """Get active visitor by roll number"""
        try:
            url = f"{Config.SUPABASE_URL}/rest/v1/visitors"
            today = datetime.now().date().isoformat()
            
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
            print(f"❌ Get visitor error: {e}")
            return None
    
    @classmethod
    def update_exit_time(cls, roll_no):
        """Update exit time for visitor"""
        try:
            # First get active visitor
            visitor = cls.get_active_visitor(roll_no)
            if not visitor:
                return None
            
            # Update exit time
            url = f"{Config.SUPABASE_URL}/rest/v1/visitors"
            params = {'id': f'eq.{visitor["id"]}'}
            
            data = {
                'exit_time': datetime.now().time().strftime('%H:%M:%S')
            }
            
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
            print(f"❌ Update exit time error: {e}")
            return None
    
    @classmethod
    def get_today_visitors(cls):
        """Get today's visitors"""
        try:
            url = f"{Config.SUPABASE_URL}/rest/v1/visitors"
            today = datetime.now().date().isoformat()
            
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
