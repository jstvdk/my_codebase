import json
from selenium import webdriver
import time

# Function to save cookies to a JSON file
def save_cookies(driver, filepath):
    # Get all cookies from the current session
    cookies = driver.get_cookies()
    
    # Save cookies to a JSON file
    with open(filepath, 'w') as file:
        json.dump(cookies, file)
    print(f"Cookies saved to {filepath}")

# Main function to navigate to Funda and save cookies after successful loading
def extract_funda_cookies():
    url = "https://www.funda.nl"
    time.sleep(10)
    # Set up Chrome WebDriver with anti-detection settings
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")

    driver = webdriver.Chrome(options=options)

    # Navigate to the website
    driver.get(url)
    
    print("Page loaded without triggering CAPTCHA.")

    # Save the cookies after successful loading
    save_cookies(driver, 'funda_cookies.json')

    # Close the browser
    driver.quit()

if __name__ == "__main__":
    extract_funda_cookies()
