import random
import string

def generate_random_email():
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"test_{random_str}@example.com"

def generate_employee_data(role='employee'):
    return {
        'email': generate_random_email(),
        'password': 'TestPassword123!',
        'full_name': f'Test User {random.randint(1000, 9999)}',
        'phone': f'555-{random.randint(1000, 9999)}',
        'department': random.choice(['Engineering', 'Sales', 'HR', 'Finance']),
        'role': role
    }

EMPLOYEE_DATA = {
    'email': 'employee@test.com',
    'password': 'password123',
    'full_name': 'Test Employee',
    'department': 'Engineering',
    'role': 'employee'
}

MANAGER_DATA = {
    'email': 'manager@test.com',
    'password': 'password123',
    'full_name': 'Test Manager',
    'department': 'Sales',
    'role': 'manager'
}

HR_DATA = {
    'email': 'hr@test.com',
    'password': 'password123',
    'full_name': 'Test HR',
    'department': 'HR',
    'role': 'hr'
}

ADMIN_DATA = {
    'email': 'admin@test.com',
    'password': 'password123',
    'full_name': 'Test Admin',
    'department': 'Operations',
    'role': 'admin'
}