from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# Start WebDriver
driver = webdriver.Chrome()
driver.get("http://localhost:7860")  # Load the local web app
time.sleep(2)  # Allow the page to load

# Click the dropdown to activate the search field
dropdown = driver.find_element(By.CLASS_NAME, "svelte-1hfxrpf.container")  # Adjust if needed
dropdown.click()
time.sleep(1)  # Wait for the dropdown to open

# Locate the input field and type the option name
search_box = driver.find_element(By.CSS_SELECTOR, "input[role='listbox']")
search_box.send_keys("English")  # Replace with the desired option
time.sleep(1)  # Wait for the filtered results to appear

# Press Enter to select the first matched option
search_box.send_keys(Keys.RETURN)

# Close the browser
time.sleep(2)
driver.quit()
