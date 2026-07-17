from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os
import time

STREAMLIT_URL = os.environ.get("STREAMLIT_APP_URL", "https://your-app-name.streamlit.app/")

def keep_app_alive():
    try:
        options = Options()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)')

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        print(f"Opening {STREAMLIT_URL}...")
        driver.get(STREAMLIT_URL)

        WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "script"))
        )

        time.sleep(5)
        print("✅ App pinged successfully!")

        driver.quit()
        return True

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = keep_app_alive()
    if not success:
        exit(1)  # make the workflow actually show red X on failure
