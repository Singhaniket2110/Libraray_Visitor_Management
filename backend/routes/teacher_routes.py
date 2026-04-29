from flask import Blueprint, render_template, request, jsonify
from backend.supabase_direct import SupabaseDirect as Database
from datetime import datetime

teacher_bp = Blueprint('teacher', __name__, url_prefix='/teacher')

# Entry form page (hidden from homepage)
@teacher_bp.route('/entry', methods=['GET'])
def teacher_entry_form():
    return render_template('teacher_entry.html')

# Exit form page (hidden from homepage)
@teacher_bp.route('/exit', methods=['GET'])
def teacher_exit_form():
    return render_template('teacher_exit.html')

# Check if teacher is currently inside
@teacher_bp.route('/check/<employee_id>', methods=['GET'])
def check_teacher(employee_id):
    """Check if a teacher with given employee ID is currently inside"""
    try:
        teacher = Database.get_active_teacher_by_employee_id(employee_id)
        
        if teacher:
            return jsonify({"teacher": teacher}), 200
        else:
            return jsonify({
                "teacher": None,
                "message": "No active teacher found with this Employee ID"
            }), 200
            
    except Exception as e:
        print(f"Error checking teacher: {e}")
        return jsonify({"error": str(e)}), 500

# Record teacher entry
@teacher_bp.route('/entry', methods=['POST'])
def teacher_entry():
    try:
        data = request.json
        
        if not data:
            return jsonify({"error": "Invalid data"}), 400
        
        # Validate required fields
        required_fields = ['name', 'employee_id', 'designation', 'nature_of_work']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"{field} is required"}), 400
        
        # Check if already inside today
        active = Database.get_active_teacher_by_employee_id(data['employee_id'])
        if active:
            return jsonify({
                "success": False,
                "error": f"You are already inside since {active.get('entry_time')}. Please exit first."
            }), 400
        
        # Prepare data
        teacher_data = {
            'name': data['name'].strip(),
            'employee_id': data['employee_id'].strip().upper(),
            'designation': data['designation'],
            'nature_of_work': data['nature_of_work'],
            'purpose': data.get('purpose', 'Library Work'),
            'notes': data.get('notes', '')
        }
        
        # Insert teacher record
        result = Database.insert_teacher(teacher_data)
        
        if result:
            return jsonify({
                "success": True,
                "message": "Teacher entry recorded successfully",
                "teacher_id": result.get('id')
            }), 201
        else:
            return jsonify({
                "success": False,
                "error": "Failed to record teacher entry"
            }), 500
            
    except Exception as e:
        print(f"Error recording teacher entry: {e}")
        return jsonify({
            "success": False,
            "error": f"Failed to record entry: {str(e)}"
        }), 500

# Record teacher exit
@teacher_bp.route('/exit/<int:teacher_id>', methods=['PUT'])
def teacher_exit(teacher_id):
    try:
        result = Database.update_teacher_exit_by_id(teacher_id)
        
        if result:
            return jsonify({"message": "Exit time marked successfully"}), 200
        else:
            return jsonify({"error": "Failed to mark exit"}), 500
    except Exception as e:
        print(f"Error marking teacher exit: {e}")
        return jsonify({"error": f"Failed to mark exit: {str(e)}"}), 500
