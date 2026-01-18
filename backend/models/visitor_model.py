from datetime import datetime, date, time
from backend.supabase_db import SupabaseDatabase as Database

def convert_to_json(data):
    """Convert PostgreSQL data types to JSON-serializable formats"""
    if data is None:
        return None
    elif isinstance(data, dict):
        return {key: convert_to_json(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_to_json(item) for item in data]
    elif isinstance(data, (date, datetime)):
        return data.isoformat()
    elif isinstance(data, time):
        return str(data)
    else:
        return data

def add_visitor(data):
    """Add a new visitor entry"""
    visit_day = datetime.now().strftime('%A')
    
    if data['level'] == 'JC':
        query = """
            INSERT INTO visitors
            (name, roll_no, level, course, jc_year, jc_stream, purpose, visit_day)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        
        values = (
            data['name'].strip(),
            data['roll_no'].strip().upper(),
            data['level'],
            data.get('course', 'Junior College'),
            data.get('jc_year'),
            data.get('jc_stream'),
            data['purpose'],
            visit_day
        )
    else:
        query = """
            INSERT INTO visitors
            (name, roll_no, level, course, year, purpose, visit_day)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        
        values = (
            data['name'].strip(),
            data['roll_no'].strip().upper(),
            data['level'],
            data['course'],
            data.get('year'),
            data['purpose'],
            visit_day
        )
    
    result = Database.execute_query(query, values, fetch=True)
    return result['id'] if result else None

def mark_exit(visitor_id):
    """Mark exit time for a visitor"""
    query = "UPDATE visitors SET exit_time = CURRENT_TIME WHERE id = %s"
    Database.execute_query(query, (visitor_id,))
    return True

def get_all_visitors():
    """Get all visitors"""
    query = "SELECT * FROM visitors ORDER BY id DESC"
    data = Database.execute_query(query, fetch_all=True)
    return convert_to_json(data)

def get_today_visitors():
    """Get today's visitors"""
    query = """
        SELECT * FROM visitors 
        WHERE visit_date = CURRENT_DATE 
        ORDER BY id DESC
    """
    data = Database.execute_query(query, fetch_all=True)
    return convert_to_json(data)

def get_filtered_visitors(level='', date=''):
    """Get filtered visitors based on level and/or date"""
    query = "SELECT * FROM visitors WHERE 1=1"
    params = []
    
    if level:
        query += " AND level = %s"
        params.append(level)
    
    if date:
        query += " AND visit_date = %s"
        params.append(date)
    
    query += " ORDER BY id DESC"
    
    data = Database.execute_query(query, tuple(params) if params else None, fetch_all=True)
    return convert_to_json(data)

def get_active_visitor_by_rollno(roll_no):
    """Get active visitor by roll number (not exited yet)"""
    query = """
        SELECT * FROM visitors 
        WHERE roll_no = %s 
        AND exit_time IS NULL
        AND visit_date = CURRENT_DATE
        ORDER BY id DESC 
        LIMIT 1
    """
    visitor = Database.execute_query(query, (roll_no.upper(),), fetch=True)
    return convert_to_json(visitor) if visitor else None

def get_visitors_by_date_range(start_date, end_date):
    """Get visitors within date range"""
    try:
        if not start_date or start_date == 'null':
            start_date = datetime.now().date().isoformat()
        if not end_date or end_date == 'null':
            end_date = datetime.now().date().isoformat()
        
        query = """
            SELECT * FROM visitors 
            WHERE visit_date BETWEEN %s AND %s
            ORDER BY visit_date DESC, entry_time DESC
        """
        data = Database.execute_query(query, (start_date, end_date), fetch_all=True)
        return convert_to_json(data)
    except Exception as e:
        print(f"Error in get_visitors_by_date_range: {e}")
        return []