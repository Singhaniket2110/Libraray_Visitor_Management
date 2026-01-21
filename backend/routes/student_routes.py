from flask import Blueprint, render_template, request, jsonify
from backend.supabase_direct import SupabaseDirect as Database

student_bp = Blueprint('student', __name__, url_prefix='/student')

@student_bp.route('/', methods=['GET'])
def visitor_form():
    return render_template('visitor_form.html')

@student_bp.route('/exit', methods=['GET'])
def exit_form():
    return render_template('exit_form.html')

@student_bp.route('/check/<roll_no>', methods=['GET'])
def check_visitor(roll_no):
    """Check if a visitor with given roll number is currently inside"""
    try:
        # ✅ USE DIRECT API
        visitor = Database.get_active_visitor_by_rollno(roll_no)
        
        if visitor:
            return jsonify({"visitor": visitor}), 200
        else:
            # Also check if any visitor exists with this roll number (even exited)
            all_visitors = Database.get_all_visitors()
            any_visitor = None
            for v in all_visitors:
                if v.get('roll_no', '').upper() == roll_no.upper():
                    any_visitor = v
                    break
            
            if any_visitor:
                return jsonify({
                    "visitor": None,
                    "message": "Visitor found but already exited"
                }), 200
            else:
                return jsonify({
                    "visitor": None,
                    "message": "No visitor found with this roll number"
                }), 200
                
    except Exception as e:
        print(f"Error checking visitor: {e}")
        return jsonify({"error": str(e)}), 500

@student_bp.route('/visit', methods=['POST'])
def student_visit():
    try:
        data = request.json
        
        if not data:
            return jsonify({"error": "Invalid data"}), 400
        
        # Validate required fields
        required_fields = ['name', 'roll_no', 'level', 'purpose']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"{field} is required"}), 400
        
        # Additional validation for JC
        if data.get('level') == 'JC':
            if not data.get('jc_year') or not data.get('jc_stream'):
                return jsonify({"error": "JC Year and Stream are required for JC students"}), 400
        else:
            # For UG/PG, course is required
            if not data.get('course'):
                return jsonify({"error": "Course is required for UG/PG students"}), 400
        
        # Prepare data for direct API
        visitor_data = {
            'name': data['name'].strip(),
            'roll_no': data['roll_no'].strip().upper(),
            'level': data['level'],
            'purpose': data['purpose'],
            'course': data.get('course', 'Not Specified')
        }
        
        # Add year/stream based on level
        if data['level'] == 'JC':
            visitor_data['jc_year'] = data.get('jc_year')
            visitor_data['jc_stream'] = data.get('jc_stream')
        else:
            if data.get('year'):
                visitor_data['year'] = data.get('year')
        
        # ✅ USE DIRECT API
        result = Database.insert_visitor(visitor_data)
        
        if result:
            return jsonify({
                "success": True,
                "message": "Visit recorded successfully",
                "visitor_id": result.get('id')
            }), 201
        else:
            return jsonify({
                "success": False,
                "error": "Failed to record visit"
            }), 500
            
    except Exception as e:
        print(f"Error recording visit: {e}")
        return jsonify({
            "success": False,
            "error": f"Failed to record visit: {str(e)}"
        }), 500

@student_bp.route('/exit/<int:visitor_id>', methods=['PUT'])
def student_exit(visitor_id):
    try:
        # ✅ USE DIRECT API
        result = Database.update_exit_by_id(visitor_id)
        
        if result:
            return jsonify({"message": "Exit time marked successfully"}), 200
        else:
            return jsonify({"error": "Failed to mark exit"}), 500
    except Exception as e:
        print(f"Error marking exit: {e}")
        return jsonify({"error": f"Failed to mark exit: {str(e)}"}), 500
