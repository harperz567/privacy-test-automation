from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import shutil
import tempfile

def get_chrome_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    
    # 禁用各种可能的弹窗和自动填充
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-popup-blocking')
    chrome_options.add_argument('--disable-infobars')
    chrome_options.add_argument('--disable-save-password-bubble')
    chrome_options.add_argument('--disable-features=PasswordManager,PasswordManagerLeak')
    
    temp_dir = tempfile.mkdtemp()
    chrome_options.add_argument(f'--user-data-dir={temp_dir}')
    chrome_options.add_argument('--profile-directory=Default')
    
    prefs = {
        'credentials_enable_service': False,
        'profile.password_manager_enabled': False,
        'profile.default_content_setting_values.notifications': 2,
        'autofill.profile_enabled': False,
        'autofill.credit_card_enabled': False,
        'password_manager_enabled': False,
        # 完全禁用密码泄露检查和密码管理器
        'profile.password_manager_leak_detection': False,
        'profile.default_content_settings.popups': 2,
        'safebrowsing.enabled': False,
    }
    chrome_options.add_experimental_option('prefs', prefs)
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    chromedriver_path = shutil.which('chromedriver')
    
    if chromedriver_path:
        from selenium.webdriver.chrome.service import Service
        service = Service(chromedriver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
    else:
        driver = webdriver.Chrome(options=chrome_options)
    
    # 移除自动化标识
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        '''
    })
    
    driver.implicitly_wait(10)
    return driver

def get_chrome_driver_visible():
    chrome_options = Options()
    chrome_options.add_argument('--window-size=1920,1080')
    
    # 禁用各种可能的弹窗和自动填充
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-popup-blocking')
    chrome_options.add_argument('--disable-infobars')
    
    temp_dir = tempfile.mkdtemp()
    chrome_options.add_argument(f'--user-data-dir={temp_dir}')
    chrome_options.add_argument('--profile-directory=Default')
    
    prefs = {
        'credentials_enable_service': False,
        'profile.password_manager_enabled': False,
        'profile.default_content_setting_values.notifications': 2,
        'autofill.profile_enabled': False,
        'autofill.credit_card_enabled': False,
        'password_manager_enabled': False,
        # 完全禁用密码泄露检查和密码管理器
        'profile.password_manager_leak_detection': False,
        'profile.default_content_settings.popups': 2,
        'safebrowsing.enabled': False,
    }
    chrome_options.add_experimental_option('prefs', prefs)
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    chromedriver_path = shutil.which('chromedriver')
    
    if chromedriver_path:
        from selenium.webdriver.chrome.service import Service
        service = Service(chromedriver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
    else:
        driver = webdriver.Chrome(options=chrome_options)
    
    # 移除自动化标识
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        '''
    })
    
    driver.implicitly_wait(10)
    return driver