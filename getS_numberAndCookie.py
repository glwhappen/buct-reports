from loguru import logger
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re

from tools.ConfigManager import ConfigManager

config_manager = ConfigManager()

@logger.catch
def getValue():
   # 设置 Chrome 的启动选项
   options = webdriver.ChromeOptions()
   options.add_argument('--headless')  # 无头模式，不显示浏览器窗口
   options.add_argument('--no-sandbox')
   options.add_argument('--disable-dev-shm-usage')
   options.page_load_strategy = 'eager'  # 或者使用 'none'
   executable_path = config_manager.get_param('system', 'executable_path', '/usr/local/bin/chromedriver')
   logger.debug(f"浏览器正在加载 驱动位置 {executable_path}")
   # 启动 Chrome 浏览器
   driver = webdriver.Chrome(options=options, service=Service(executable_path=executable_path))
   logger.debug("浏览器运行成功")
   # driver = webdriver.Chrome(options=options)
   wait = WebDriverWait(driver, 10)
   # 访问指定的网址
   driver.get('https://portal.buct.edu.cn/cas/login')
   driver.switch_to.frame("loginIframe")
   # 找到用户名输入框，并输入用户名
   username_input = wait.until(EC.presence_of_element_located((By.ID, "username")))
   user_id = config_manager.get_param("info", 'user_id', "2022210000")
   user_password = config_manager.get_param("info", 'user_password', "xxxxxx")
   try:
      username_input.send_keys(user_id)

      # 找到密码输入框，并输入密码
      password_input = driver.find_element(By.ID, "password")
      password_input.send_keys(user_password)
      windows = driver.window_handles
      # 找到登录按钮，并点击登录
      login_button = driver.find_element(By.XPATH, '//input[@i18n="login.password.loginbutton"]')
      login_button.click()
      logger.debug("学校系统登录成功")

      driver.get('https://i.buct.edu.cn/_s2/yjs_sy/main.psp')

      # Wait for the element with the specific href to be clickable and then click it
      desired_div = wait.until(
          EC.element_to_be_clickable((By.XPATH, "//div[@class='remind2-box-img' and div[text()='研究生系统']]")))
      desired_div.click()
      # Wait for the new window/tab to open
      # wait.until(lambda d: len(d.window_handles) == 2)

      # Switch to the new window/tab
      new_window_handle = driver.window_handles[1]
      driver.switch_to.window(new_window_handle)

      # Now you can interact with the new window/tab
      # Get the current URL
      logger.debug("正在获取url")
      current_url = driver.current_url
      logger.debug("获取url成功")
      # current_url = driver.execute_script("return window.location.href;")

      # Regular expression pattern to extract the required part
      pattern = r"\(S\((.*?)\)\)"

      # Search the URL for the pattern and extract the matching group
      match = re.search(pattern, current_url)
      if match:
          S_number = match.group(1)
          logger.debug(f"S_number: {S_number}")
      else:
          logger.debug("No match found")
      # Get cookies
      cookies_list = driver.get_cookies()
      cookie_string = '; '.join([cookie['name'] + '=' + cookie['value'] for cookie in cookies_list])
      logger.debug(f"Cookies: {cookie_string}")
   except:
      logger.error("可能用户名密码错误")
      return None, None
   finally:

      driver.quit()
   return S_number, cookie_string


if __name__ == '__main__':
   getValue()