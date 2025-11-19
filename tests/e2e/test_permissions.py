import pytest
import requests
from tests.utils.test_data import EMPLOYEE_DATA, HR_DATA, ADMIN_DATA

@pytest.fixture(scope='module')
def test_users(api_url):
    """Create test users with different roles"""
    users = {
        'employee': EMPLOYEE_DATA,
        'hr': HR_DATA,
        'admin': ADMIN_DATA
    }
    
    for role, user_data in users.items():
        try:
            response = requests.post(f'{api_url}/auth/register', json=user_data)
            print(f"Created {role} user: {response.status_code}")
        except Exception as e:
            print(f"{role} user may already exist: {e}")
    
    return users

@pytest.fixture
def get_token(api_url):
    """Helper function to get authentication token"""
    def _get_token(email, password):
        response = requests.post(f'{api_url}/auth/login', json={
            'email': email,
            'password': password
        })
        if response.status_code == 200:
            return response.json()['token']
        return None
    return _get_token

@pytest.mark.permissions
class TestEmployeePermissions:
    """Test Employee role permissions"""
    
    def test_employee_can_view_own_profile(self, api_url, get_token, test_users):
        token = get_token(EMPLOYEE_DATA['email'], EMPLOYEE_DATA['password'])
        headers = {'Authorization': f'Bearer {token}'}
        
        response = requests.get(f'{api_url}/employees/me', headers=headers)
        assert response.status_code == 200
        assert response.json()['email'] == EMPLOYEE_DATA['email']
    
    def test_employee_cannot_view_all_employees(self, api_url, get_token, test_users):
        token = get_token(EMPLOYEE_DATA['email'], EMPLOYEE_DATA['password'])
        headers = {'Authorization': f'Bearer {token}'}
        
        response = requests.get(f'{api_url}/employees', headers=headers)
        assert response.status_code == 403
    
    def test_employee_cannot_access_admin_reports(self, api_url, get_token, test_users):
        token = get_token(EMPLOYEE_DATA['email'], EMPLOYEE_DATA['password'])
        headers = {'Authorization': f'Bearer {token}'}
        
        response = requests.get(f'{api_url}/admin/reports', headers=headers)
        assert response.status_code == 403
    
    def test_employee_cannot_purge_data(self, api_url, get_token, test_users):
        token = get_token(EMPLOYEE_DATA['email'], EMPLOYEE_DATA['password'])
        headers = {'Authorization': f'Bearer {token}'}
        
        response = requests.post(f'{api_url}/admin/purge', headers=headers)
        assert response.status_code == 403
    
    def test_employee_can_view_own_salary(self, api_url, get_token, test_users):
        token = get_token(EMPLOYEE_DATA['email'], EMPLOYEE_DATA['password'])
        headers = {'Authorization': f'Bearer {token}'}
        
        response = requests.get(f'{api_url}/salaries/me', headers=headers)
        assert response.status_code in [200, 404]
    
    def test_employee_can_request_dsr_export(self, api_url, get_token, test_users):
        token = get_token(EMPLOYEE_DATA['email'], EMPLOYEE_DATA['password'])
        headers = {'Authorization': f'Bearer {token}'}
        
        response = requests.post(f'{api_url}/dsr/export', headers=headers)
        assert response.status_code == 200

@pytest.mark.permissions
class TestHRPermissions:
    """Test HR role permissions"""
    
    def test_hr_can_view_all_employees(self, api_url, get_token, test_users):
        token = get_token(HR_DATA['email'], HR_DATA['password'])
        headers = {'Authorization': f'Bearer {token}'}
        
        response = requests.get(f'{api_url}/employees', headers=headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_hr_can_view_reports(self, api_url, get_token, test_users):
        token = get_token(HR_DATA['email'], HR_DATA['password'])
        headers = {'Authorization': f'Bearer {token}'}
        
        response = requests.get(f'{api_url}/admin/reports', headers=headers)
        assert response.status_code == 200
    
    def test_hr_cannot_purge_data(self, api_url, get_token, test_users):
        token = get_token(HR_DATA['email'], HR_DATA['password'])
        headers = {'Authorization': f'Bearer {token}'}
        
        response = requests.post(f'{api_url}/admin/purge', headers=headers)
        assert response.status_code == 403
    
    def test_hr_can_view_dsr_requests(self, api_url, get_token, test_users):
        token = get_token(HR_DATA['email'], HR_DATA['password'])
        headers = {'Authorization': f'Bearer {token}'}
        
        response = requests.get(f'{api_url}/admin/dsr-requests', headers=headers)
        assert response.status_code == 200

@pytest.mark.permissions
class TestAdminPermissions:
    """Test Admin role permissions"""
    
    def test_admin_can_view_all_employees(self, api_url, get_token, test_users):
        token = get_token(ADMIN_DATA['email'], ADMIN_DATA['password'])
        headers = {'Authorization': f'Bearer {token}'}
        
        response = requests.get(f'{api_url}/employees', headers=headers)
        assert response.status_code == 200
    
    def test_admin_can_view_reports(self, api_url, get_token, test_users):
        token = get_token(ADMIN_DATA['email'], ADMIN_DATA['password'])
        headers = {'Authorization': f'Bearer {token}'}
        
        response = requests.get(f'{api_url}/admin/reports', headers=headers)
        assert response.status_code == 200
    
    def test_admin_can_purge_data(self, api_url, get_token, test_users):
        token = get_token(ADMIN_DATA['email'], ADMIN_DATA['password'])
        headers = {'Authorization': f'Bearer {token}'}
        
        response = requests.post(f'{api_url}/admin/purge', headers=headers)
        assert response.status_code == 200
    
    def test_admin_can_view_audit_logs(self, api_url, get_token, test_users):
        token = get_token(ADMIN_DATA['email'], ADMIN_DATA['password'])
        headers = {'Authorization': f'Bearer {token}'}
        
        response = requests.get(f'{api_url}/admin/audit-logs', headers=headers)
        assert response.status_code == 200

@pytest.mark.permissions  
class TestUnauthorizedAccess:
    """Test that unauthenticated requests are blocked"""
    
    def test_no_token_returns_401(self, api_url):
        response = requests.get(f'{api_url}/employees/me')
        assert response.status_code == 401
    
    def test_invalid_token_returns_401(self, api_url):
        headers = {'Authorization': 'Bearer invalid_token_12345'}
        response = requests.get(f'{api_url}/employees/me', headers=headers)
        assert response.status_code == 401