from functools import wraps
from flask import request, jsonify
from app.models import Role

ROLE_HIERARCHY = {
    Role.EMPLOYEE: 1,
    Role.MANAGER: 2,
    Role.HR: 3,
    Role.ADMIN: 4
}

def require_role(required_role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(request, 'current_user'):
                return jsonify({'error': 'Authentication required'}), 401
            
            user_role = request.current_user.get('role')
            
            if ROLE_HIERARCHY.get(user_role, 0) < ROLE_HIERARCHY.get(required_role, 999):
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def check_resource_ownership(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(request, 'current_user'):
            return jsonify({'error': 'Authentication required'}), 401
        
        user_id = request.current_user.get('user_id')
        user_role = request.current_user.get('role')
        
        resource_id = kwargs.get('id') or kwargs.get('employee_id')
        
        if user_role in [Role.HR, Role.ADMIN]:
            return f(*args, **kwargs)
        
        if resource_id and int(resource_id) != user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function