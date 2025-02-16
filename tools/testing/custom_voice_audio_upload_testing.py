from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

# Start WebDriver
driver = webdriver.Chrome()
driver.get("http://localhost:7860")  # Adjust if needed

try:
    # Wait for file upload button and input
    file_button = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "button[aria-label*='Click to upload']"))
    )
    print("✅ File upload button found.")

    # Find the hidden file input inside the button
    file_input = file_button.find_element(By.CSS_SELECTOR, "input[type='file']")
    print("✅ File input field located.")

    # Make sure it's visible (if hidden)
    driver.execute_script("arguments[0].style.display = 'block';", file_input)
    print("✅ Made file input visible (if hidden).")

    # Create a test audio file
    test_file_path = "/Users/drew/ebook2audiobook/voices/eng/adult/male/AiExplained_16000.wav"

    # Upload file
    file_input.send_keys(test_file_path)
    print("✅ File upload attempt made.")

    # Wait for file preview to confirm successful upload
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.wrap.svelte-12ioyct"))
    )
    print("✅ File upload confirmed by preview.")

except Exception as e:
    print(f"❌ Error occurred: {e}")

finally:
    driver.quit()
    print("✅ Browser closed.")
