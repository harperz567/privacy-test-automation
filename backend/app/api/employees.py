from flask import Blueprint, request, jsonify
from app.database import db
from app.models import Employee, Role
from app.auth_utils import token_required
from app.permissions import require_role, check_resource_ownership

bp = Blueprint('employees', __name__, url_prefix='/employees')

@bp.route('/me', methods=['GET'])
@token_required
def get_my_profile():
    employee = Employee.query.get(request.current_user['user_id'])
    
    if not employee:
        return jsonify({'error': 'Employee not found'}), 404
    
    return jsonify(employee.to_dict(include_sensitive=True)), 200

@bp.route('/<int:id>', methods=['GET'])
@token_required
@check_resource_ownership
def get_employee(id):
    employee = Employee.query.get(id)
    
    if not employee or employee.is_deleted:
        return jsonify({'error': 'Employee not found'}), 404
    
    user_role = request.current_user.get('role')
    include_sensitive = user_role in [Role.HR, Role.ADMIN]
    
    return jsonify(employee.to_dict(include_sensitive=include_sensitive)), 200

@bp.route('', methods=['GET'])
@token_required
@require_role(Role.HR)
def get_all_employees():
    employees = Employee.query.filter_by(is_deleted=False).all()
    
    return jsonify([emp.to_dict(include_sensitive=True) for emp in employees]), 200

@bp.route('/<int:id>', methods=['PUT'])
@token_required
@check_resource_ownership
def update_employee(id):
    employee = Employee.query.get(id)
    
    if not employee or employee.is_deleted:
        return jsonify({'error': 'Employee not found'}), 404
    
    data = request.get_json()
    
    if 'full_name' in data:
        employee.full_name = data['full_name']
    if 'phone' in data:
        employee.phone = data['phone']
    if 'address' in data:
        employee.address = data['address']
    if 'department' in data:
        employee.department = data['department']
    
    user_role = request.current_user.get('role')
    if user_role in [Role.HR, Role.ADMIN]:
        if 'role' in data:
            employee.role = data['role']
        if 'manager_id' in data:
            employee.manager_id = data['manager_id']
    
    db.session.commit()
    
    return jsonify(employee.to_dict(include_sensitive=True)), 200