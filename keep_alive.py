from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time

# Get your Streamlit app URL from environment variable
STREAMLIT_URL = os.environ.get("STREAMLIT_APP_URL", "https://your-app-name.streamlit.app/")

def keep_app_alive():
    """Visit the Streamlit app to prevent it from sleeping"""
    try:
        options = Options()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)')
        
        driver = webdriver.Chrome(options=options)
        
        print(f"Opening {STREAMLIT_URL}...")
        driver.get(STREAMLIT_URL)
        
        # Wait for page to load (up to 30 seconds)
        WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "script"))
        )
        
        time.sleep(5)  # Let it load fully
        print("✅ App pinged successfully!")
        
        driver.quit()
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    keep_app_alive()
