import logging
import re
from datetime import datetime
from flask import request, g
from functools import wraps

logging.basicConfig(
    filename='logs/audit.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

audit_logger = logging.getLogger('audit')

PII_PATTERNS = {
    'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
    'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
    'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'
}

def mask_sensitive_data(data):
    if isinstance(data, str):
        masked = data
        for field_type, pattern in PII_PATTERNS.items():
            masked = re.sub(pattern, f'[MASKED_{field_type.upper()}]', masked)
        return masked
    elif isinstance(data, dict):
        return {k: mask_sensitive_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [mask_sensitive_data(item) for item in data]
    return data

def log_request():
    user_info = 'anonymous'
    if hasattr(request, 'current_user'):
        user_info = f"user_id={request.current_user.get('user_id')}, role={request.current_user.get('role')}"
    
    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'method': request.method,
        'endpoint': request.path,
        'user': user_info,
        'ip': request.remote_addr
    }
    
    if request.path.startswith('/dsr/') or request.path.startswith('/admin/'):
        log_entry['sensitive_operation'] = True
        if request.json:
            log_entry['request_data'] = mask_sensitive_data(request.json)
    
    audit_logger.info(str(log_entry))

def setup_request_logging(app):
    @app.before_request
    def before_request():
        g.start_time = datetime.utcnow()
    
    @app.after_request
    def after_request(response):
        if hasattr(g, 'start_time'):
            duration = (datetime.utcnow() - g.start_time).total_seconds()
            log_entry = {
                'timestamp': datetime.utcnow().isoformat(),
                'method': request.method,
                'endpoint': request.path,
                'status': response.status_code,
                'duration': f'{duration:.3f}s'
            }
            if hasattr(request, 'current_user'):
                log_entry['user_id'] = request.current_user.get('user_id')
            
            audit_logger.info(str(log_entry))
        
        return response