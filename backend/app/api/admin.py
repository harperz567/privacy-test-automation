from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from app.database import db
from app.models import Employee, DSRRequest, Role
from app.auth_utils import token_required
from app.permissions import require_role
from config import Config

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/reports', methods=['GET'])
@token_required
@require_role(Role.HR)
def get_reports():
    total_employees = Employee.query.filter_by(is_deleted=False).count()
    deleted_employees = Employee.query.filter_by(is_deleted=True).count()
    
    pending_dsr = DSRRequest.query.filter_by(status='pending').count()
    completed_dsr = DSRRequest.query.filter_by(status='completed').count()
    
    return jsonify({
        'total_employees': total_employees,
        'deleted_employees': deleted_employees,
        'pending_dsr_requests': pending_dsr,
        'completed_dsr_requests': completed_dsr,
        'generated_at': datetime.utcnow().isoformat()
    }), 200

@bp.route('/purge', methods=['POST'])
@token_required
@require_role(Role.ADMIN)
def purge_deleted_employees():
    retention_date = datetime.utcnow() - timedelta(days=Config.DSR_RETENTION_DAYS)
    
    deleted_employees = Employee.query.filter(
        Employee.is_deleted == True,
        Employee.updated_at < retention_date
    ).all()
    
    count = 0
    for employee in deleted_employees:
        db.session.delete(employee)
        count += 1
    
    db.session.commit()
    
    return jsonify({
        'message': f'Purged {count} employees',
        'purged_count': count
    }), 200

@bp.route('/audit-logs', methods=['GET'])
@token_required
@require_role(Role.ADMIN)
def get_audit_logs():
    try:
        with open(Config.AUDIT_LOG_FILE, 'r') as f:
            logs = f.readlines()
            recent_logs = logs[-100:]
        
        return jsonify({
            'logs': recent_logs,
            'total_entries': len(logs)
        }), 200
    except FileNotFoundError:
        return jsonify({'logs': [], 'total_entries': 0}), 200

@bp.route('/dsr-requests', methods=['GET'])
@token_required
@require_role(Role.HR)
def get_all_dsr_requests():
    requests = DSRRequest.query.all()
    return jsonify([r.to_dict() for r in requests]), 200