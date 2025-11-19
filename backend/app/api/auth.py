from flask import Blueprint, request, jsonify
from datetime import date
from app.database import db
from app.models import Employee, Role
from app.auth_utils import generate_token, token_required

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400
    
    if Employee.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 409
    
    employee = Employee(
        email=data['email'],
        full_name=data.get('full_name', ''),
        phone=data.get('phone'),
        address=data.get('address'),
        department=data.get('department'),
        role=data.get('role', Role.EMPLOYEE),
        hire_date=date.today()
    )
    employee.set_password(data['password'])
    
    db.session.add(employee)
    db.session.commit()
    
    return jsonify({
        'message': 'Registration successful',
        'employee': employee.to_dict()
    }), 201

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400
    
    employee = Employee.query.filter_by(email=data['email']).first()
    
    if not employee or not employee.check_password(data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    if employee.is_deleted:
        return jsonify({'error': 'Account has been deleted'}), 403
    
    token = generate_token(employee.id, employee.email, employee.role)
    
    return jsonify({
        'token': token,
        'employee': employee.to_dict()
    }), 200

@bp.route('/me', methods=['GET'])
@token_required
def get_current_user():
    employee = Employee.query.get(request.current_user['user_id'])
    
    if not employee:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify(employee.to_dict(include_sensitive=True)), 200

@bp.route('/logout', methods=['POST'])
@token_required
def logout():
    return jsonify({'message': 'Logout successful'}), 200