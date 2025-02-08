import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import json,pickle
with open("C:\\Users\\mayan\\OneDrive\\Desktop\\Linkedin_Scraped\\config.json", 'r') as config_file:
    config = json.load(config_file)
def login_to_site():
    """Logs in to LinkedIn and navigates to the start URL."""
    print("Starting LinkedIn login process...")
    
    try:
        # Configure Chrome options
        chrome_options = Options()
        # chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-webrtc")  # Disable WebRTC
        chrome_options.add_argument("--disable-features=WebRTC-HW-Decoding,WebRTC-HW-Encoding")
        chrome_options.add_argument("--log-level=3") 
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        chrome_options.add_argument("--disable-breakpad")
        chrome_options.add_argument("--disable-component-extensions-with-background-pages")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-features=TranslateUI,BlinkGenPropertyTrees")
        chrome_options.add_argument("--disable-ipc-flooding-protection")
        chrome_options.add_argument("--disable-renderer-backgrounding")
        chrome_options.add_argument("--enable-features=NetworkService,NetworkServiceInProcess")
        chrome_options.add_argument("--force-color-profile=srgb")
        chrome_options.add_argument("--hide-scrollbars")
        chrome_options.add_argument("--metrics-recording-only")
        chrome_options.add_argument("--mute-audio")
        chrome_options.add_argument("--no-sandbox") # Suppress verbose logs
        chrome_options.add_argument("--enable-logging")
        chrome_options.add_argument("--v=1")  # Increase verbosity level
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")


        print("Initializing Chrome WebDriver...")
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
        print("Chrome WebDriver initialized successfully.")

        print("Navigating to LinkedIn login page...")
        driver.get("https://www.linkedin.com/feed")
        print("LinkedIn login page loaded.")

        # Wait for the email field to be present
        print("Waiting for email field to be present...")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "session_key")))
        print("Email field found.")

        # Find email and password fields
        email_field = driver.find_element(By.NAME, "session_key")
        password_field = driver.find_element(By.NAME, "session_password")
        print("Email and password fields located.")

        # Enter email and password
        print("Entering email...")
        email_field.send_keys(config['email'])
        print("Email entered.")

        print("Entering password...")
        password_field.send_keys(config['password'])
        print("Password entered.")

        # Submit the form
        print("Submitting login form...")
        password_field.send_keys(Keys.RETURN)
        print("Login form submitted.")

        # Wait for login to complete
        print("Waiting for login to complete...")
        time.sleep(10)  # Adjust this delay if needed
        print("LinkedIn login successful.")

        return driver

    except NoSuchElementException as e:
        print(f"Element not found during login: {str(e)}")
        raise
    except TimeoutException as e:
        print(f"Timeout during login: {str(e)}")
        raise
    except Exception as e:
        print(f"Unexpected error during login: {str(e)}")
        raise
# def login_to_site():    
#     chrome_options = Options()
#     chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
#     # chrome_options.add_argument("user-data-dir=C:\\selenium\\ChromeProfile")  # Use the same profile
#     chrome_options.add_argument("--headless")
#     chrome_options.add_argument("--disable-dev-shm-usage")
#     chrome_options.add_argument("--no-sandbox")
#     chrome_options.add_argument("--disable-webrtc") 
#     chrome_options.add_argument("--disable-features=WebRTC-HW-Decoding,WebRTC-HW-Encoding")
#     chrome_options.add_argument("--log-level=3")

#     driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
#     driver.get("https://www.linkedin.com/feed")
#     time.sleep(10)
#     return driver

def load_cookies_and_open():
    
    # chrome_options.add_argument("--headless")
    chrome_options = Options()
# Core headless operation
    # chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # GPU/WebGL configuration
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--enable-unsafe-swiftshader")
    chrome_options.add_argument("--use-angle=swiftshader")
    chrome_options.add_argument("--disable-software-rasterizer")

    # Performance/security tweaks
    chrome_options.add_argument("--log-level=3")  # Suppress non-critical logs
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-background-networking")



    print("Initializing Chrome WebDriver...")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
    print("Chrome WebDriver initialized successfully.")

    print("Navigating to LinkedIn login page...")
    driver.get("https://www.linkedin.com/feed")
    print("LinkedIn login page loaded.")
    time.sleep(5)
    # Load cookies from file
    with open("cookies.pkl", "rb") as f:
        cookies = pickle.load(f)
    for cookie in cookies:
        driver.add_cookie(cookie)
    # Refresh page to use loaded cookies
    driver.refresh()
    time.sleep(8)
    return driver