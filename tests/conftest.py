import pytest
import requests
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from tests.utils.browser_setup import get_chrome_driver_visible

BASE_URL = 'http://localhost:3000'
API_BASE_URL = 'http://localhost:5555'

EMPLOYEE_DATA = {
    'email': 'employee@test.com',
    'password': 'password123',
    'full_name': 'Test Employee',
    'department': 'Engineering',
    'role': 'employee'
}

@pytest.fixture(scope='session')
def api_url():
    return API_BASE_URL

@pytest.fixture(scope='session')
def frontend_url():
    return BASE_URL

@pytest.fixture(scope='function')
def driver():
    print("Creating driver...")
    driver = get_chrome_driver_visible()  # 可视化模式，能看到窗口
    yield driver
    print("Closing driver...")
    driver.quit()

@pytest.fixture(scope='session', autouse=True)
def setup_test_users():
    print(f"Setting up test users at {API_BASE_URL}...")
    
    try:
        response = requests.post(f'{API_BASE_URL}/auth/register', json=EMPLOYEE_DATA, timeout=5)
        print(f"Registration response: {response.status_code}")
    except Exception as e:
        print(f"Registration error (user might exist): {e}")
    
    yield
    print("Test users setup complete")

@pytest.fixture
def login_as_employee(driver, frontend_url):
    print(f"Navigating to {frontend_url}/login")
    driver.get(f'{frontend_url}/login')
    
    print(f"Current URL after navigation: {driver.current_url}")
    
    try:
        print("Looking for email input...")
        # 等待页面加载，找到 email 输入框
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, 'email'))
        )
        print("Found email input")
        
        # 直接输入
        email_input.send_keys(EMPLOYEE_DATA['email'])
        print(f"Entered email: {EMPLOYEE_DATA['email']}")
        
        password_input = driver.find_element(By.NAME, 'password')
        password_input.send_keys(EMPLOYEE_DATA['password'])
        print("Entered password")
        
        # 点击登录按钮
        login_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        print("Clicking login button...")
        login_button.click()
        
        # 等待跳转到 dashboard
        print("Waiting for dashboard redirect...")
        WebDriverWait(driver, 10).until(
            EC.url_contains('/dashboard')
        )
        
        print(f"Login successful! Current URL: {driver.current_url}")
        
        # 等待 Dashboard 页面完全加载（等待主要内容出现）
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//h1[contains(text(), "Welcome")]'))
            )
            print("Dashboard loaded")
        except TimeoutException:
            print("Dashboard content not fully loaded, but continuing...")
        
        print(f"Final URL: {driver.current_url}")
        
    except Exception as e:
        print(f"Login failed: {e}")
        print(f"Current URL: {driver.current_url}")
        driver.save_screenshot('login_failure.png')
        print("Screenshot saved to login_failure.png")
        raise
    
    return driver

# 在文件末尾添加

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

@pytest.fixture(scope='module')
def test_users(api_url):
    """Create test users with different roles"""
    users = {
        'employee': EMPLOYEE_DATA,
        'hr': {'email': 'hr@test.com', 'password': 'password123', 'full_name': 'Test HR', 'department': 'HR', 'role': 'hr'},
        'admin': {'email': 'admin@test.com', 'password': 'password123', 'full_name': 'Test Admin', 'department': 'Operations', 'role': 'admin'}
    }
    
    for role, user_data in users.items():
        try:
            response = requests.post(f'{api_url}/auth/register', json=user_data)
            print(f"Created {role} user: {response.status_code}")
        except Exception as e:
            print(f"{role} user may already exist: {e}")
    
    return users