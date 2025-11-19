import pytest
import time
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.browser_setup import get_chrome_driver_visible

def test_debug_dsr_popup():
    """调试测试 - 可视化运行，手动查看弹窗"""
    
    # 使用可视化浏览器
    driver = get_chrome_driver_visible()
    
    try:
        # 1. 登录
        print("Navigating to login page...")
        driver.get('http://localhost:3000/login')
        time.sleep(2)
        
        # 输入登录信息
        email_input = driver.find_element(By.NAME, 'email')
        password_input = driver.find_element(By.NAME, 'password')
        email_input.send_keys('employee@test.com')
        password_input.send_keys('password123')
        
        # 点击登录
        login_button = driver.find_element(By.XPATH, '//button[@type="submit"]')
        login_button.click()
        
        # 等待跳转到 dashboard
        WebDriverWait(driver, 10).until(
            EC.url_contains('/dashboard')
        )
        print(f"Logged in! Current URL: {driver.current_url}")
        
        # 2. 在这里暂停，让你看看页面
        print("\n" + "="*60)
        print("现在浏览器窗口应该打开了，你能看到页面吗？")
        print("看看有没有弹窗？")
        print("按回车继续...")
        print("="*60 + "\n")
        input()  # 等待你按回车
        
        # 3. 尝试打印所有覆盖层元素
        print("\n查找可能的遮罩层...")
        overlays = driver.execute_script("""
            let elements = [];
            document.querySelectorAll('*').forEach(el => {
                let style = window.getComputedStyle(el);
                let zIndex = parseInt(style.zIndex);
                if (zIndex > 100 || 
                    style.position === 'fixed' || 
                    el.className.includes('modal') ||
                    el.className.includes('popup') ||
                    el.className.includes('overlay') ||
                    el.className.includes('backdrop')) {
                    elements.push({
                        tag: el.tagName,
                        id: el.id,
                        className: el.className,
                        zIndex: style.zIndex,
                        position: style.position,
                        display: style.display,
                        text: el.innerText ? el.innerText.substring(0, 50) : ''
                    });
                }
            });
            return elements;
        """)
        
        print(f"\n找到 {len(overlays)} 个可能的遮罩/弹窗元素：")
        for i, el in enumerate(overlays):
            print(f"{i+1}. {el}")
        
        # 4. 截图
        driver.save_screenshot('debug_after_login.png')
        print("\n截图已保存到: debug_after_login.png")
        
        # 5. 保存页面HTML
        with open('debug_page_source.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print("页面源码已保存到: debug_page_source.html")
        
        # 6. 再次暂停，让你尝试手动关闭弹窗
        print("\n" + "="*60)
        print("现在尝试查看或手动关闭弹窗")
        print("准备好后按回车继续尝试点击 DSR 链接...")
        print("="*60 + "\n")
        input()
        
        # 7. 查找 DSR 链接
        print("\n查找 DSR 链接...")
        dsr_links = driver.find_elements(By.XPATH, '//a[contains(text(), "DSR") or contains(text(), "Data")]')
        print(f"找到 {len(dsr_links)} 个 DSR 相关链接：")
        for i, link in enumerate(dsr_links):
            print(f"{i+1}. 文本: '{link.text}', href: {link.get_attribute('href')}")
        
        if dsr_links:
            # 8. 尝试点击第一个
            print(f"\n尝试点击: {dsr_links[0].text}")
            try:
                dsr_links[0].click()
                print("点击成功（普通点击）")
            except Exception as e:
                print(f"普通点击失败: {e}")
                print("尝试 JavaScript 点击...")
                driver.execute_script("arguments[0].click();", dsr_links[0])
                print("JavaScript 点击执行完成")
            
            time.sleep(2)
            print(f"点击后的 URL: {driver.current_url}")
            
            # 最后一次截图
            driver.save_screenshot('debug_after_click.png')
            print("点击后截图已保存到: debug_after_click.png")
        
        print("\n" + "="*60)
        print("调试完成！按回车关闭浏览器...")
        print("="*60 + "\n")
        input()
        
    finally:
        driver.quit()
        print("浏览器已关闭")

if __name__ == '__main__':
    test_debug_dsr_popup()