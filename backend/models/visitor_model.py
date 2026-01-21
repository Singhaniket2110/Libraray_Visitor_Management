from backend.supabase_direct import SupabaseDirect as Database
from datetime import datetime

def add_visitor(data):
    """Add a new visitor entry"""
    try:
        visitor_data = {
            'name': data.get('name', '').strip(),
            'roll_no': data.get('roll_no', '').strip().upper(),
            'level': data.get('level', ''),
            'purpose': data.get('purpose', 'Study'),
            'course': data.get('course', 'Not Specified')
        }
        
        # Add year/stream based on level
        if data.get('level') == 'JC':
            visitor_data['jc_year'] = data.get('jc_year')
            visitor_data['jc_stream'] = data.get('jc_stream')
        else:
            if data.get('year'):
                visitor_data['year'] = data.get('year')
        
        result = Database.insert_visitor(visitor_data)
        return result.get('id') if result else None
        
    except Exception as e:
        print(f"Error adding visitor: {e}")
        raise e

def mark_exit(visitor_id):
    """Mark exit time for a visitor"""
    try:
        result = Database.update_exit_by_id(visitor_id)
        return result is not None
    except Exception as e:
        print(f"Error marking exit: {e}")
        raise e

def get_active_visitor_by_rollno(roll_no):
    """Get active visitor by roll number"""
    try:
        return Database.get_active_visitor_by_rollno(roll_no)
    except Exception as e:
        print(f"Error getting active visitor: {e}")
        return None

def get_today_visitors():
    """Get today's visitors"""
    try:
        return Database.get_today_visitors()
    except Exception as e:
        print(f"Error getting today's visitors: {e}")
        return []

def get_all_visitors():
    """Get all visitors"""
    try:
        return Database.get_all_visitors()
    except Exception as e:
        print(f"Error getting all visitors: {e}")
        return []

def get_filtered_visitors(level=None, date=None):
    """Get filtered visitors"""
    try:
        visitors = Database.get_all_visitors()
        
        # Apply filters
        if level:
            visitors = [v for v in visitors if v.get('level') == level]
        if date:
            visitors = [v for v in visitors if str(v.get('visit_date')) == date]
        
        return visitors
    except Exception as e:
        print(f"Error filtering visitors: {e}")
        return []

def get_visitors_by_date_range(start_date, end_date):
    """Get visitors by date range"""
    try:
        return Database.get_visitors_by_date_range(start_date, end_date)
    except Exception as e:
        print(f"Error getting visitors by date range: {e}")
        return []
