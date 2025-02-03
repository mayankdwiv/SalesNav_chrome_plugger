import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
with open("C:\\Users\\mayan\\OneDrive\\Desktop\\Linkedin_Scraped\\config.json", 'r') as config_file:
    config = json.load(config_file)
def login_to_site():
    """Logs in to LinkedIn and navigates to the start URL."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-webrtc") 
    chrome_options.add_argument("--disable-features=WebRTC-HW-Decoding,WebRTC-HW-Encoding")
    chrome_options.add_argument("--log-level=3")  
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
    driver.get("https://www.linkedin.com/feed")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "session_key")))
    
    email_field = driver.find_element(By.NAME, "session_key")
    password_field = driver.find_element(By.NAME, "session_password")

    email_field.send_keys(config['email'])
    password_field.send_keys(config['password'])
    password_field.send_keys(Keys.RETURN)
    time.sleep(10)
    return driver
# def login_to_site():    
#     chrome_options = Options()
#     chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
#     chrome_options.add_argument("user-data-dir=C:\\selenium\\ChromeProfile")  # Use the same profile
#     # chrome_options.add_argument("--headless")
#     driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
#     driver.get("https://www.linkedin.com/feed")
#     time.sleep(10)
#     return driver