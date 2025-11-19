from flask import Blueprint, request, jsonify
from datetime import datetime
import json
import os
from app.database import db
from app.models import Employee, Salary, PerformanceReview, Attendance, ConsentRecord, DSRRequest, Role
from app.auth_utils import token_required
from app.permissions import require_role
from config import Config

bp = Blueprint('dsr', __name__, url_prefix='/dsr')

@bp.route('/export', methods=['POST'])
@token_required
def request_export():
    employee_id = request.current_user['user_id']
    employee = Employee.query.get(employee_id)
    
    if not employee:
        return jsonify({'error': 'Employee not found'}), 404
    
    dsr_request = DSRRequest(
        employee_id=employee_id,
        request_type='export',
        status='processing'
    )
    db.session.add(dsr_request)
    db.session.commit()
    
    export_data = {
        'employee': employee.to_dict(include_sensitive=True),
        'salaries': [s.to_dict() for s in employee.salaries],
        'reviews': [r.to_dict() for r in employee.reviews_received],
        'attendance': [a.to_dict() for a in employee.attendance_records],
        'consents': [c.to_dict() for c in employee.consents]
    }
    
    os.makedirs(Config.DSR_EXPORT_FOLDER, exist_ok=True)
    filename = f'export_{employee_id}_{dsr_request.id}.json'
    filepath = os.path.join(Config.DSR_EXPORT_FOLDER, filename)
    
    with open(filepath, 'w') as f:
        json.dump(export_data, f, indent=2)
    
    dsr_request.status = 'completed'
    dsr_request.result_file_path = filepath
    dsr_request.completed_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'message': 'Export completed',
        'request_id': dsr_request.id,
        'file_path': filepath
    }), 200

@bp.route('/delete', methods=['POST'])
@token_required
def request_delete():
    employee_id = request.current_user['user_id']
    employee = Employee.query.get(employee_id)
    
    if not employee:
        return jsonify({'error': 'Employee not found'}), 404
    
    dsr_request = DSRRequest(
        employee_id=employee_id,
        request_type='delete',
        status='processing'
    )
    db.session.add(dsr_request)
    db.session.commit()
    
    employee.is_deleted = True
    employee.email = f'deleted_{employee.id}@deleted.com'
    employee.phone = None
    employee.address = None
    employee.ssn = None
    
    dsr_request.status = 'completed'
    dsr_request.completed_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'message': 'Account deletion completed',
        'request_id': dsr_request.id
    }), 200

@bp.route('/consent', methods=['PUT'])
@token_required
def update_consent():
    employee_id = request.current_user['user_id']
    data = request.get_json()
    
    if not data or 'consent_type' not in data or 'is_granted' not in data:
        return jsonify({'error': 'consent_type and is_granted are required'}), 400
    
    consent = ConsentRecord.query.filter_by(
        employee_id=employee_id,
        consent_type=data['consent_type']
    ).first()
    
    if consent:
        consent.is_granted = data['is_granted']
        if data['is_granted']:
            consent.granted_at = datetime.utcnow()
            consent.revoked_at = None
        else:
            consent.revoked_at = datetime.utcnow()
    else:
        consent = ConsentRecord(
            employee_id=employee_id,
            consent_type=data['consent_type'],
            is_granted=data['is_granted'],
            granted_at=datetime.utcnow() if data['is_granted'] else None,
            revoked_at=None if data['is_granted'] else datetime.utcnow()
        )
        db.session.add(consent)
    
    db.session.commit()
    
    return jsonify(consent.to_dict()), 200

@bp.route('/status/<int:id>', methods=['GET'])
@token_required
def get_dsr_status(id):
    dsr_request = DSRRequest.query.get(id)
    
    if not dsr_request:
        return jsonify({'error': 'Request not found'}), 404
    
    user_id = request.current_user['user_id']
    user_role = request.current_user['role']
    
    if dsr_request.employee_id != user_id and user_role not in [Role.HR, Role.ADMIN]:
        return jsonify({'error': 'Access denied'}), 403
    
    return jsonify(dsr_request.to_dict()), 200

@bp.route('/my-requests', methods=['GET'])
@token_required
def get_my_requests():
    employee_id = request.current_user['user_id']
    requests = DSRRequest.query.filter_by(employee_id=employee_id).all()
    
    return jsonify([r.to_dict() for r in requests]), 200

@bp.route('/<int:id>/process', methods=['POST'])
@token_required
@require_role(Role.HR)
def process_dsr_request(id):
    dsr_request = DSRRequest.query.get(id)
    
    if not dsr_request:
        return jsonify({'error': 'Request not found'}), 404
    
    if dsr_request.status == 'completed':
        return jsonify({'error': 'Request already processed'}), 400
    
    dsr_request.status = 'completed'
    dsr_request.completed_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'message': 'Request processed successfully',
        'request': dsr_request.to_dict()
    }), 200