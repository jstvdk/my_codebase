from selenium import webdriver
import json
import time

# Set up WebDriver
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(options=options)

# Load the Pararius website
driver.get("https://www.pararius.com/apartments/amsterdam/1000-2500/50m2")

# Wait for the user to manually accept cookies
print("Please accept the cookies manually if prompted...")
time.sleep(15)  # Wait 15 seconds for cookies to be accepted (adjust if necessary)

# Extract and save cookies
cookies = driver.get_cookies()
with open("pararius_cookies.json", "w") as file:
    json.dump(cookies, file)
    print("Cookies saved to pararius_cookies.json")

# Clean up
driver.quit()
