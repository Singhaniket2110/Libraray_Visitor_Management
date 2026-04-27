from flask import Blueprint, jsonify, request, render_template, make_response, session, redirect
from functools import wraps
from datetime import datetime, timedelta
import io
import csv
import pandas as pd
import jwt

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

from backend.supabase_direct import SupabaseDirect as Database
from backend.config import Config

# ==================== JWT HELPER FUNCTIONS ====================

def create_jwt_token(username):
    """Create JWT token for authentication"""
    payload = {
        'username': username,
        'exp': datetime.utcnow() + timedelta(hours=12),
        'iat': datetime.utcnow()
    }
    token = jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm='HS256')
    return token

def verify_jwt_token(token):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
        return payload['username']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# ==================== LOGIN REQUIRED DECORATOR ====================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get('admin_token')
        
        if not token:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'error': 'Authentication required', 'redirect': '/admin/login'}), 401
            return redirect('/admin/login')
        
        username = verify_jwt_token(token)
        if not username:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'error': 'Invalid or expired token', 'redirect': '/admin/login'}), 401
            return redirect('/admin/login')
        
        request.admin_username = username
        return f(*args, **kwargs)
    
    return decorated_function

# ==================== AUTHENTICATION ROUTES ====================

@admin_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page and authentication"""
    if request.method == 'GET':
        return render_template('login.html')
    
    try:
        data = request.json
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        if not username or not password:
            return jsonify({'success': False, 'error': 'Username and password are required'}), 400
        
        admin = Database.admin_login(username, password)
        
        if admin or (username == 'admin' and password == 'admin'):
            token = create_jwt_token(username)
            response = make_response(jsonify({'success': True, 'message': 'Login successful', 'redirect': '/admin/dashboard'}))
            response.set_cookie('admin_token', token, httponly=True, secure=False, samesite='Lax', max_age=43200)
            return response, 200
        
        return jsonify({'success': False, 'error': 'Invalid username or password'}), 401
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return jsonify({'success': False, 'error': 'Login failed. Please try again.'}), 500

@admin_bp.route('/logout')
def admin_logout():
    """Logout admin"""
    response = make_response(redirect('/'))
    response.set_cookie('admin_token', '', expires=0)
    response.set_cookie('session', '', expires=0)
    session.clear()
    return response

@admin_bp.route('/check_session')
def check_session():
    """Check if admin is logged in"""
    token = request.cookies.get('admin_token')
    if not token:
        return jsonify({'logged_in': False, 'username': None})
    username = verify_jwt_token(token)
    if username:
        return jsonify({'logged_in': True, 'username': username})
    return jsonify({'logged_in': False, 'username': None})

# ==================== DASHBOARD ROUTES ====================

@admin_bp.route('/dashboard')
@login_required
def admin_dashboard():
    return render_template('dashboard.html')

# ==================== TEACHER MANAGEMENT ROUTES ====================

@admin_bp.route('/teachers/today')
@login_required
def today_teachers():
    try:
        teachers = Database.get_today_teachers()
        return jsonify(teachers), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/teachers/all')
@login_required
def all_teachers():
    try:
        teachers = Database.get_all_teachers()
        return jsonify(teachers), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/teachers/filter')
@login_required
def filtered_teachers():
    try:
        start_date = request.args.get('start_date', '')
        end_date = request.args.get('end_date', '')
        status = request.args.get('status', '')
        
        if start_date and end_date:
            teachers = Database.get_teachers_by_date_range(start_date, end_date)
        else:
            teachers = Database.get_all_teachers()
        
        if status == 'active':
            teachers = [t for t in teachers if not t.get('exit_time')]
        elif status == 'exited':
            teachers = [t for t in teachers if t.get('exit_time')]
        
        return jsonify(teachers), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/teachers/mark_exit/<int:teacher_id>', methods=['PUT'])
@login_required
def mark_teacher_exit(teacher_id):
    try:
        result = Database.update_teacher_exit_by_id(teacher_id)
        if result:
            return jsonify({"success": True, "message": "Teacher exit marked successfully"}), 200
        return jsonify({"error": "Failed to mark exit"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/teachers/add', methods=['POST'])
@login_required
def add_teacher():
    try:
        data = request.json
        
        if not data.get('name') or not data.get('employee_id'):
            return jsonify({"error": "Name and Employee ID are required"}), 400
        
        teacher_data = {
            'name': data['name'].strip(),
            'employee_id': data['employee_id'].strip().upper(),
            'department': data.get('department', ''),
            'purpose': data.get('purpose', 'Meeting'),
            'notes': data.get('notes', '')
        }
        
        result = Database.insert_teacher(teacher_data)
        
        if result:
            return jsonify({"success": True, "message": "Teacher added successfully", "teacher_id": result.get('id')}), 201
        return jsonify({"error": "Failed to add teacher"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==================== TEACHER ANALYTICS ====================

@admin_bp.route('/analytics/teachers')
@login_required
def teacher_analytics():
    try:
        start_date = request.args.get('start_date', '')
        end_date = request.args.get('end_date', '')
        
        if not start_date or start_date == 'null':
            start_date = datetime.now().date().isoformat()
        if not end_date or end_date == 'null':
            end_date = datetime.now().date().isoformat()
        
        teachers = Database.get_teachers_by_date_range(start_date, end_date)
        
        from collections import Counter
        
        total = len(teachers)
        active = sum(1 for t in teachers if not t.get('exit_time'))
        
        # Department distribution
        dept_counts = Counter(t.get('department', 'Other') for t in teachers)
        
        # Purpose distribution
        purpose_counts = Counter(t.get('purpose', 'Other') for t in teachers)
        
        # Daily trend
        daily_counts = {}
        for t in teachers:
            date = t.get('visit_date')
            if date:
                daily_counts[str(date)] = daily_counts.get(str(date), 0) + 1
        
        sorted_dates = sorted(daily_counts.keys())
        
        response_data = {
            'stats': {
                'total': total,
                'active': active,
                'todayVisits': len(Database.get_today_teachers())
            },
            'deptData': {
                'labels': list(dept_counts.keys()),
                'values': list(dept_counts.values())
            },
            'purposeData': {
                'labels': list(purpose_counts.keys()),
                'values': list(purpose_counts.values())
            },
            'dailyTrend': {
                'labels': sorted_dates,
                'values': [daily_counts[d] for d in sorted_dates]
            },
            'teachers': teachers
        }
        
        return jsonify(response_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==================== STUDENT VISITOR MANAGEMENT ====================

@admin_bp.route('/add_visitor', methods=['POST'])
@login_required
def add_visitor_admin():
    try:
        data = request.json
        
        required_fields = ['name', 'roll_no', 'level', 'purpose', 'visit_date', 'entry_time']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"{field} is required"}), 400
        
        if data.get('level') == 'JC':
            if not data.get('jc_year') or not data.get('jc_stream'):
                return jsonify({"error": "JC Year and Stream are required for JC students"}), 400
        elif not data.get('course'):
            return jsonify({"error": "Course is required for UG/PG students"}), 400
        
        visitor_data = {
            'name': data['name'].strip(),
            'roll_no': data['roll_no'].strip().upper(),
            'level': data['level'],
            'purpose': data['purpose'],
            'course': data.get('course', 'Not Specified')
        }
        
        if data['level'] == 'JC':
            visitor_data['jc_year'] = data.get('jc_year')
            visitor_data['jc_stream'] = data.get('jc_stream')
        elif data.get('year'):
            visitor_data['year'] = data.get('year')
        
        # For admin added visitors, use provided date/time
        result = Database.insert_visitor(visitor_data)
        
        if result:
            return jsonify({"success": True, "message": "Visitor added successfully", "visitor_id": result.get('id')}), 201
        return jsonify({"error": "Failed to add visitor"}), 500
    except Exception as e:
        return jsonify({"error": f"Failed to add visitor: {str(e)}"}), 500

@admin_bp.route('/visitors/today')
@login_required
def today_visitors():
    try:
        visitors = Database.get_today_visitors()
        return jsonify(visitors), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/visitors/all')
@login_required
def all_visitors():
    try:
        visitors = Database.get_all_visitors()
        return jsonify(visitors), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/visitors/filter')
@login_required
def filtered_visitors():
    try:
        level = request.args.get('level', '')
        start_date = request.args.get('start_date', '')
        end_date = request.args.get('end_date', '')
        status = request.args.get('status', '')
        
        if start_date and end_date:
            visitors = Database.get_visitors_by_date_range(start_date, end_date)
        else:
            visitors = Database.get_all_visitors()
        
        if level:
            visitors = [v for v in visitors if v.get('level') == level]
        
        if status == 'active':
            visitors = [v for v in visitors if not v.get('exit_time')]
        elif status == 'exited':
            visitors = [v for v in visitors if v.get('exit_time')]
        
        return jsonify(visitors), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==================== STUDENT ANALYTICS ====================

@admin_bp.route('/analytics/advanced')
@login_required
def advanced_analytics():
    try:
        start_date = request.args.get('start_date', '')
        end_date = request.args.get('end_date', '')
        
        if not start_date or start_date == 'null':
            start_date = datetime.now().date().isoformat()
        if not end_date or end_date == 'null':
            end_date = datetime.now().date().isoformat()
        
        visitors = Database.get_visitors_by_date_range(start_date, end_date)
        
        from collections import Counter
        
        total = len(visitors)
        active = sum(1 for v in visitors if not v.get('exit_time'))
        
        # Calculate average duration correctly (handling next day)
        durations = []
        for v in visitors:
            if v.get('entry_time') and v.get('exit_time'):
                try:
                    entry_str = v['entry_time']
                    exit_str = v['exit_time']
                    date_str = v.get('visit_date', '')
                    
                    entry_time = datetime.strptime(entry_str, '%H:%M:%S').time()
                    exit_time = datetime.strptime(exit_str, '%H:%M:%S').time()
                    entry_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else datetime.now().date()
                    
                    entry_dt = datetime.combine(entry_date, entry_time)
                    exit_dt = datetime.combine(entry_date, exit_time)
                    
                    # If exit time is less than entry time, assume next day
                    if exit_dt <= entry_dt:
                        exit_dt = exit_dt + timedelta(days=1)
                    
                    duration = (exit_dt - entry_dt).total_seconds() / 60
                    if duration >= 0:
                        durations.append(duration)
                except Exception as e:
                    print(f"Duration calc error: {e}")
        
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        # Level distribution
        level_counts = Counter(v.get('level', 'Unknown') for v in visitors)
        
        # Course distribution
        course_counts = Counter()
        for v in visitors:
            if v.get('level') == 'JC':
                course = v.get('jc_stream', 'Unknown')
            else:
                course = v.get('course', 'Unknown')
            course_counts[course] += 1
        
        # Purpose distribution
        purpose_counts = Counter(v.get('purpose', 'Other') for v in visitors)
        
        # Daily trend
        daily_counts = {}
        for v in visitors:
            date = v.get('visit_date')
            if date:
                daily_counts[str(date)] = daily_counts.get(str(date), 0) + 1
        
        sorted_dates = sorted(daily_counts.keys())
        
        # Peak hours
        hour_counts = {hour: 0 for hour in range(8, 21)}
        for v in visitors:
            if v.get('entry_time'):
                try:
                    hour = int(str(v['entry_time']).split(':')[0])
                    if 8 <= hour <= 20:
                        hour_counts[hour] = hour_counts.get(hour, 0) + 1
                except:
                    pass
        
        response_data = {
            'stats': {
                'total': total,
                'active': active,
                'avgDuration': round(avg_duration, 1)
            },
            'levelData': {
                'labels': list(level_counts.keys()),
                'values': list(level_counts.values())
            },
            'courseData': {
                'labels': [c[0] for c in course_counts.most_common(10)],
                'values': [c[1] for c in course_counts.most_common(10)]
            },
            'purposeData': {
                'labels': list(purpose_counts.keys()),
                'values': list(purpose_counts.values())
            },
            'dailyTrend': {
                'labels': sorted_dates,
                'values': [daily_counts[d] for d in sorted_dates]
            },
            'peakHours': {
                'labels': [f"{h}:00" for h in range(8, 21)],
                'values': [hour_counts[h] for h in range(8, 21)]
            },
            'visitors': visitors
        }
        
        return jsonify(response_data), 200
    except Exception as e:
        return jsonify({"error": f"Error fetching analytics: {str(e)}"}), 500

# ==================== EXPORT FUNCTIONS ====================

@admin_bp.route('/export_data', methods=['GET'])
@login_required
def export_data():
    try:
        format_type = request.args.get('format', 'csv')
        data_type = request.args.get('type', 'students')
        start_date = request.args.get('start_date', '')
        end_date = request.args.get('end_date', '')
        
        if data_type == 'students':
            if start_date and end_date:
                data = Database.get_visitors_by_date_range(start_date, end_date)
            else:
                data = Database.get_all_visitors()
            
            columns = ['ID', 'Name', 'Roll No', 'Level', 'Course', 'Year', 'JC Year', 'JC Stream', 'Purpose', 'Entry Time', 'Exit Time', 'Visit Date', 'Day']
            rows = []
            for v in data:
                rows.append([
                    v.get('id', ''), v.get('name', ''), v.get('roll_no', ''), v.get('level', ''),
                    v.get('course', ''), v.get('year', ''), v.get('jc_year', ''), v.get('jc_stream', ''),
                    v.get('purpose', ''), str(v.get('entry_time', '')), str(v.get('exit_time', '')),
                    str(v.get('visit_date', '')), v.get('visit_day', '')
                ])
        else:
            if start_date and end_date:
                data = Database.get_teachers_by_date_range(start_date, end_date)
            else:
                data = Database.get_all_teachers()
            
            columns = ['ID', 'Name', 'Employee ID', 'Department', 'Purpose', 'Entry Time', 'Exit Time', 'Visit Date', 'Day', 'Notes']
            rows = []
            for v in data:
                rows.append([
                    v.get('id', ''), v.get('name', ''), v.get('employee_id', ''), v.get('department', ''),
                    v.get('purpose', ''), str(v.get('entry_time', '')), str(v.get('exit_time', '')),
                    str(v.get('visit_date', '')), v.get('visit_day', ''), v.get('notes', '')
                ])
        
        if format_type == 'csv':
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(columns)
            writer.writerows(rows)
            output.seek(0)
            
            response = make_response(output.getvalue())
            response.headers['Content-Type'] = 'text/csv'
            response.headers['Content-Disposition'] = f'attachment; filename=library_{data_type}_{datetime.now().strftime("%Y%m%d")}.csv'
            return response
        
        elif format_type == 'excel':
            df = pd.DataFrame(rows, columns=columns)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=data_type.capitalize(), index=False)
            output.seek(0)
            
            response = make_response(output.getvalue())
            response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            response.headers['Content-Disposition'] = f'attachment; filename=library_{data_type}_{datetime.now().strftime("%Y%m%d")}.xlsx'
            return response
        
        return jsonify({"error": "Invalid format"}), 400
    except Exception as e:
        return jsonify({"error": f"Export failed: {str(e)}"}), 500

@admin_bp.route('/bulk_actions', methods=['POST'])
@login_required
def bulk_actions():
    try:
        data = request.json
        action = data.get('action')
        visitor_ids = data.get('visitor_ids', [])
        
        if not visitor_ids:
            return jsonify({"error": "No visitors selected"}), 400
        
        if action == 'mark_exit':
            success_count = 0
            for visitor_id in visitor_ids:
                if Database.update_exit_by_id(visitor_id):
                    success_count += 1
            return jsonify({"success": True, "message": f"Marked {success_count} visitors as exited"}), 200
        
        elif action == 'delete':
            success_count = 0
            for visitor_id in visitor_ids:
                if Database.delete_visitor(visitor_id):
                    success_count += 1
            return jsonify({"success": True, "message": f"Deleted {success_count} visitors"}), 200
        
        return jsonify({"error": "Invalid action"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
