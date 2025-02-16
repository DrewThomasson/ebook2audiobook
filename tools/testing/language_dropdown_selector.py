from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# Start WebDriver
driver = webdriver.Chrome()
driver.get("http://localhost:7860")  # Load the local web app
time.sleep(2)  # Allow the page to load

try:
    # Click the dropdown to activate the search field
    dropdown = driver.find_element(By.CLASS_NAME, "svelte-1hfxrpf.container")  # Adjust if needed
    dropdown.click()
    print("✅ Dropdown clicked.")
    time.sleep(1)  # Wait for dropdown to expand

    # Locate the input field
    search_box = driver.find_element(By.CSS_SELECTOR, "input[role='listbox']")
    print("✅ Found search box.")

    # Type "English" and wait for suggestions
    search_box.send_keys("English")
    time.sleep(1)  # Allow UI to filter options

    # Press Enter to select
    search_box.send_keys(Keys.RETURN)
    print("✅ English selected.")

except Exception as e:
    print(f"❌ Error: {e}")

finally:
    time.sleep(2)  # Allow observation before closing
    driver.quit()
    print("✅ Browser closed.")
