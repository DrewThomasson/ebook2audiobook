from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Start WebDriver
driver = webdriver.Chrome()
driver.get("http://localhost:7860")  # Adjust if needed

try:
    # Wait for the button inside #component-31 to be clickable
    button = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "#component-31 button[aria-label*='Click to upload']"))
    )
    print("✅ Button found and clickable.")

    # Click the button
    button.click()
    print("✅ Button clicked successfully.")

except Exception as e:
    print(f"❌ Error occurred: {e}")

finally:
    driver.quit()
    print("✅ Browser closed.")
