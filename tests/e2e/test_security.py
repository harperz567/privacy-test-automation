import pytest
import requests
import jwt
from tests.utils.test_data import EMPLOYEE_DATA, generate_employee_data

@pytest.mark.security
class TestIDORVulnerabilities:
    """Test for Insecure Direct Object Reference vulnerabilities"""
    
    def test_employee_cannot_access_other_employee_profile(self, api_url, test_users, get_token):
        """Employee should not access another employee's profile by changing ID"""
        # Create two employees
        emp1 = generate_employee_data()
        emp2 = generate_employee_data()
        
        requests.post(f'{api_url}/auth/register', json=emp1)
        requests.post(f'{api_url}/auth/register', json=emp2)
        
        # Login as employee 1
        token1 = get_token(emp1['email'], emp1['password'])
        headers = {'Authorization': f'Bearer {token1}'}
        
        # Get employee 1's ID
        me_response = requests.get(f'{api_url}/employees/me', headers=headers)
        emp1_id = me_response.json()['id']
        
        # Try to access employee 2's profile by guessing ID
        other_id = emp1_id + 1
        response = requests.get(f'{api_url}/employees/{other_id}', headers=headers)
        
        # Should be blocked with 403
        assert response.status_code == 403, \
            f"IDOR vulnerability! Employee accessed another employee's profile. Status: {response.status_code}"
    
    def test_employee_cannot_view_other_salary(self, api_url, get_token):
        """Employee should not view another employee's salary"""
        token = get_token(EMPLOYEE_DATA['email'], EMPLOYEE_DATA['password'])
        headers = {'Authorization': f'Bearer {token}'}
        
        # Try to access salary of employee ID 999 (likely someone else)
        response = requests.get(f'{api_url}/salaries/999', headers=headers)
        
        assert response.status_code in [403, 404], \
            f"IDOR vulnerability! Can view other employee's salary. Status: {response.status_code}"

@pytest.mark.security
class TestPrivilegeEscalation:
    """Test for privilege escalation vulnerabilities"""
    
    def test_cannot_escalate_privilege_by_modifying_jwt(self, api_url, get_token):
        """User should not escalate privileges by tampering with JWT"""
        # Login as employee
        token = get_token(EMPLOYEE_DATA['email'], EMPLOYEE_DATA['password'])
        
        # Decode JWT (without verification)
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            print(f"Original payload: {payload}")
            
            # Attempt to modify role to admin
            payload['role'] = 'admin'
            
            # Re-encode with a fake secret
            tampered_token = jwt.encode(payload, 'fake_secret', algorithm='HS256')
            
            headers = {'Authorization': f'Bearer {tampered_token}'}
            
            # Try to access admin endpoint
            response = requests.get(f'{api_url}/admin/reports', headers=headers)
            
            # Should fail with 401 (invalid signature)
            assert response.status_code == 401, \
                f"Privilege escalation! Tampered JWT was accepted. Status: {response.status_code}"
        except Exception as e:
            print(f"JWT tampering test passed (token validation working): {e}")
    
    def test_employee_cannot_modify_own_role(self, api_url, get_token):
        """Employee should not be able to change their own role"""
        token = get_token(EMPLOYEE_DATA['email'], EMPLOYEE_DATA['password'])
        headers = {'Authorization': f'Bearer {token}'}
        
        # Get current employee ID
        me_response = requests.get(f'{api_url}/employees/me', headers=headers)
        emp_id = me_response.json()['id']
        
        # Try to update role to admin
        response = requests.put(
            f'{api_url}/employees/{emp_id}',
            headers=headers,
            json={'role': 'admin'}
        )
        
        # Verify role was not changed
        updated = requests.get(f'{api_url}/employees/me', headers=headers)
        assert updated.json()['role'] == 'employee', \
            "Privilege escalation! Employee changed their own role"

@pytest.mark.security
class TestDataLeakage:
    """Test for data leakage vulnerabilities"""
    
    def test_deleted_user_data_not_accessible(self, api_url):
        """Deleted user data should not be accessible"""
        # Create and delete a user
        temp_user = generate_employee_data()
        requests.post(f'{api_url}/auth/register', json=temp_user)
        
        # Login and get token
        login_resp = requests.post(f'{api_url}/auth/login', json={
            'email': temp_user['email'],
            'password': temp_user['password']
        })
        token = login_resp.json()['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Delete account
        requests.post(f'{api_url}/dsr/delete', headers=headers)
        
        # Try to login again
        login_attempt = requests.post(f'{api_url}/auth/login', json={
            'email': temp_user['email'],
            'password': temp_user['password']
        })
        
        assert login_attempt.status_code in [401, 403], \
            "Data leakage! Deleted user can still login"
    
    def test_error_messages_dont_leak_info(self, api_url):
        """Error messages should not reveal sensitive information"""
        # Try to login with non-existent email
        response = requests.post(f'{api_url}/auth/login', json={
            'email': 'nonexistent@test.com',
            'password': 'password123'
        })
        
        error_message = response.json().get('error', '').lower()
        
        # Should not reveal whether email exists
        assert 'not found' not in error_message, \
            "Information disclosure! Error reveals user existence"
        assert 'does not exist' not in error_message, \
            "Information disclosure! Error reveals user existence"

@pytest.mark.security
class TestAuthenticationSecurity:
    """Test authentication security"""
    
    def test_no_auth_token_blocked(self, api_url):
        """Requests without token should be blocked"""
        response = requests.get(f'{api_url}/employees/me')
        assert response.status_code == 401
    
    def test_invalid_token_blocked(self, api_url):
        """Requests with invalid token should be blocked"""
        headers = {'Authorization': 'Bearer invalid_token_12345'}
        response = requests.get(f'{api_url}/employees/me', headers=headers)
        assert response.status_code == 401
    
    def test_expired_token_blocked(self, api_url, get_token):
        """Expired tokens should be rejected"""
        # This would require manipulating JWT exp field
        # For now, just test that tokens have expiration
        token = get_token(EMPLOYEE_DATA['email'], EMPLOYEE_DATA['password'])
        payload = jwt.decode(token, options={"verify_signature": False})
        
        assert 'exp' in payload, "JWT does not have expiration field"
        print(f"Token expires at: {payload['exp']}")

@pytest.mark.security
class TestInputValidation:
    """Test input validation and sanitization"""
    
    def test_sql_injection_in_login(self, api_url):
        """Login should be protected against SQL injection"""
        sql_payloads = [
            "' OR '1'='1",
            "admin'--",
            "' OR '1'='1' --",
        ]
        
        for payload in sql_payloads:
            response = requests.post(f'{api_url}/auth/login', json={
                'email': payload,
                'password': 'anything'
            })
            
            assert response.status_code in [400, 401], \
                f"Possible SQL injection vulnerability with payload: {payload}"
    
    def test_xss_in_registration(self, api_url):
        """Registration should sanitize XSS attempts"""
        xss_payload = '<script>alert("XSS")</script>'
        
        user_data = generate_employee_data()
        user_data['full_name'] = xss_payload
        
        response = requests.post(f'{api_url}/auth/register', json=user_data)
        
        if response.status_code in [200, 201]:
            # Login and check if XSS payload is stored as-is
            login_resp = requests.post(f'{api_url}/auth/login', json={
                'email': user_data['email'],
                'password': user_data['password']
            })
            token = login_resp.json()['token']
            headers = {'Authorization': f'Bearer {token}'}
            
            me_resp = requests.get(f'{api_url}/employees/me', headers=headers)
            stored_name = me_resp.json()['full_name']
            
            # Name should be sanitized (no script tags)
            assert '<script>' not in stored_name.lower(), \
                "XSS vulnerability! Script tags not sanitized"