from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.database import db

class DataTag:
    PUBLIC = "PUBLIC"
    PII = "PII"
    SENSITIVE = "SENSITIVE"
    HIGHLY_SENSITIVE = "HIGHLY_SENSITIVE"

class Role:
    EMPLOYEE = "employee"
    MANAGER = "manager"
    HR = "hr"
    ADMIN = "admin"

class Employee(db.Model):
    __tablename__ = 'employees'
    
    id = db.Column(db.Integer, primary_key=True)
    
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    ssn = db.Column(db.String(11))
    
    role = db.Column(db.String(20), default=Role.EMPLOYEE)
    department = db.Column(db.String(50))
    manager_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    
    hire_date = db.Column(db.Date)
    is_deleted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    salaries = db.relationship('Salary', backref='employee', lazy=True, cascade='all, delete-orphan')
    reviews_received = db.relationship('PerformanceReview', 
                                      foreign_keys='PerformanceReview.employee_id',
                                      backref='employee', lazy=True, cascade='all, delete-orphan')
    reviews_given = db.relationship('PerformanceReview',
                                   foreign_keys='PerformanceReview.reviewer_id',
                                   backref='reviewer', lazy=True)
    attendance_records = db.relationship('Attendance', backref='employee', lazy=True, cascade='all, delete-orphan')
    consents = db.relationship('ConsentRecord', backref='employee', lazy=True, cascade='all, delete-orphan')
    dsr_requests = db.relationship('DSRRequest', backref='employee', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self, include_sensitive=False):
        data = {
            'id': self.id,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role,
            'department': self.department,
            'hire_date': self.hire_date.isoformat() if self.hire_date else None,
            'created_at': self.created_at.isoformat()
        }
        
        if include_sensitive:
            data.update({
                'phone': self.phone,
                'address': self.address,
                'ssn': self.ssn,
                'manager_id': self.manager_id
            })
        
        return data

class Salary(db.Model):
    __tablename__ = 'salaries'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    
    base_salary = db.Column(db.Float, nullable=False)
    bonus = db.Column(db.Float, default=0)
    month = db.Column(db.String(7), nullable=False)
    payment_date = db.Column(db.Date)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'base_salary': self.base_salary,
            'bonus': self.bonus,
            'total': self.base_salary + self.bonus,
            'month': self.month,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None
        }

class PerformanceReview(db.Model):
    __tablename__ = 'performance_reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    
    rating = db.Column(db.Integer, nullable=False)
    feedback = db.Column(db.Text)
    review_period = db.Column(db.String(20), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'reviewer_id': self.reviewer_id,
            'rating': self.rating,
            'feedback': self.feedback,
            'review_period': self.review_period,
            'created_at': self.created_at.isoformat()
        }

class Attendance(db.Model):
    __tablename__ = 'attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    
    date = db.Column(db.Date, nullable=False)
    clock_in_time = db.Column(db.Time)
    clock_out_time = db.Column(db.Time)
    hours_worked = db.Column(db.Float)
    leave_type = db.Column(db.String(20))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'date': self.date.isoformat(),
            'clock_in_time': self.clock_in_time.isoformat() if self.clock_in_time else None,
            'clock_out_time': self.clock_out_time.isoformat() if self.clock_out_time else None,
            'hours_worked': self.hours_worked,
            'leave_type': self.leave_type
        }

class ConsentRecord(db.Model):
    __tablename__ = 'consent_records'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    
    consent_type = db.Column(db.String(50), nullable=False)
    is_granted = db.Column(db.Boolean, default=False)
    granted_at = db.Column(db.DateTime)
    revoked_at = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'consent_type': self.consent_type,
            'is_granted': self.is_granted,
            'granted_at': self.granted_at.isoformat() if self.granted_at else None,
            'revoked_at': self.revoked_at.isoformat() if self.revoked_at else None
        }

class DSRRequest(db.Model):
    __tablename__ = 'dsr_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    
    request_type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='pending')
    result_file_path = db.Column(db.String(255))
    
    requested_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'request_type': self.request_type,
            'status': self.status,
            'result_file_path': self.result_file_path,
            'requested_at': self.requested_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }