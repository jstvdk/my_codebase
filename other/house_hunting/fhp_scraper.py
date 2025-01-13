from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import schedule
import json
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Email configuration
SENDER_EMAIL = 'coolmuon@gmail.com'  # Your verified sender email
RECEIVER_EMAIL = 'coolmuon@gmail.com'          # Recipient's email
MAILJET_API_KEY = 'REDACTED_MAILJET_API_KEY'          # Mailjet API Key (Public Key)
MAILJET_SECRET_KEY = 'REDACTED_MAILJET_SECRET_KEY'    # Mailjet Secret Key (Private Key)

# URLs for the search
FUNDA_URL = 'https://www.funda.nl/zoeken/huur?selected_area=[%22amsterdam%22]&price=%221000-2000%22&object_type=[%22house%22,%22apartment%22]&publication_date=%225%22&floor_area=%2240-100%22&rooms=%220-3%22&bedrooms=%220-3%22'
HUURWONINGEN_URL = 'https://www.huurwoningen.com/in/amsterdam/?price=900-2000&living_size=25&since=3'
PARARIUS_URL = 'https://www.pararius.com/apartments/amsterdam/apartment/900-2000/25m2/since-3'

runheadless = 0

# Function to parse and return listings from the page
def parse_listings_funda(page_source):
    soup = BeautifulSoup(page_source, 'html.parser')
    
    # Find all listing containers (assuming 'sm:flex' is the class for listing containers)
    listings = soup.find_all('div', class_='sm:flex')
    result = []
    
    if not listings:
        print("No listings found. Please check the HTML structure or class name.")
        return result

    # Loop through listings and collect relevant details
    for listing in listings:
        # Extract the address (street name and house number)
        title_tag = listing.find('h2', {'data-test-id': 'street-name-house-number'})
        title = title_tag.get_text(strip=True) if title_tag else "Title not specified"
        
        # Extract the postal code and city
        location_tag = listing.find('div', {'data-test-id': 'postal-code-city'})
        location = location_tag.get_text(strip=True) if location_tag else "Location not specified"
        
        # Extract the price
        price_tag = listing.find('p', {'data-test-id': 'price-rent'})
        price = price_tag.get_text(strip=True) if price_tag else "Price not specified"
        
        # Extract the listing URL
        link_tag = listing.find('a', {'data-test-id': 'object-image-link'})
        if link_tag:
            link = link_tag['href']
            if not link.startswith('http'):
                link = "https://www.funda.nl" + link
        else:
            link = "URL not specified"
        
        # Extract the number of bedrooms
        bedrooms = 'Not specified'
        surface_area = 'Not specified'

        details = listing.find_all('li', class_='flex flex-[0_0_auto]')
        for detail in details:
            text = detail.get_text(strip=True)
            if 'm²' in text:
                surface_area = text
            elif text.isdigit():
                bedrooms = text

        # Append listing details to result list
        result.append({
            "Address": location,
            "Price": price,
            "Rooms": bedrooms,
            "Surface Area": surface_area,
            "URL": link
        })
    
    return result

# Function to handle pagination by clicking the "Volgende" button
def fetch_all_pages_funda(driver):
    listings = []
    while True:
        # Parse the current page
        page_source = driver.page_source
        listings.extend(parse_listings_funda(page_source))

        try:
            # Find the "Volgende" button
            #next_button = driver.find_element(By.XPATH, '//span[contains(text(), "Volgende")]/../..')
            next_button = driver.find_element(By.XPATH, '//a[@aria-label="Volgende"]')
            
            # Check if the button is disabled (class contains 'disabled')
            if "disabled" in next_button.get_attribute("class"):
                print("Reached the last page, no more pages to navigate.")
                break
            
            # Scroll into view and click the button
            driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", next_button)
            time.sleep(2)  # Pause to mimic human interaction
            
            # Click the "Volgende" button
            next_button.click()
            print("Next button clicked, moving to the next page...")
            time.sleep(5)  # Delay for page to load

        except Exception as e:
            print("No more pages or an error occurred:", e)
            return listings
            #break
    return listings

# Main function to load cookies and fetch listings across multiple pages
def fetch_funda_with_pagination(url):
    #url = "https://www.funda.nl/zoeken/huur?selected_area=%5B%22amsterdam%22%5D&energy_label=%5B%22A%22,%22A%2B%22,%22A%2B%2B%22,%22A%2B%2B%2B%22,%22A%2B%2B%2B%2B%22%5D&price=%22-3000%22"

    # Set up Chrome WebDriver
    options = Options()
    if runheadless == 1:
        options.add_argument("--headless") # Headless mode can be disabled for debugging purposes
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")

    driver = webdriver.Chrome(options=options)

    # Load a generic URL first to load cookies
    driver.get("https://www.funda.nl")
    time.sleep(5)  # Wait for the page to load completely

    # Load cookies from a JSON file
    try:
        with open('funda_cookies.json', 'r') as cookies_file:
            cookies = json.load(cookies_file)
            for cookie in cookies:
                driver.add_cookie(cookie)
        print("Cookies loaded successfully!")
    except Exception as e:
        print("Failed to load cookies:", e)
        driver.quit()
        return []

    # Refresh the page to apply cookies
    driver.get(url)
    time.sleep(5)  # Wait for the page to load completely
    print("Page loaded successfully! Title:", driver.title)

    # Fetch listings from all pages
    listings = fetch_all_pages_funda(driver)

    # Close the browser
    driver.quit()
    return listings


# Function to parse and return listings from the page
def parse_listings_huurwoningen(page_source, driver):
    soup = BeautifulSoup(page_source, 'html.parser')
    
    # Find all listing containers (assuming 'listing-search-item' is the class for listing containers)
    listings = soup.find_all('section', class_='listing-search-item')
    result = []

    if not listings:
        print("No listings found. Please check the HTML structure or class name.")
        return result

    # Loop through listings and collect relevant details
    for idx, listing in enumerate(listings):
        try:
            # Extract the address using Selenium XPath
            address_xpath = f"(//div[contains(@class, 'listing-search-item__sub-title')])[{idx+1}]"
            address_element = driver.find_element(By.XPATH, address_xpath)
            address = address_element.text.strip() if address_element else "Address not specified"
        except Exception:
            # Fallback to BeautifulSoup extraction
            address_tag = listing.find('div', class_='listing-search-item__sub-title')
            address = address_tag.get_text(strip=True) if address_tag else "Address not specified"

        # Extract the price
        price_tag = listing.find('div', class_='listing-search-item__price')
        price = price_tag.get_text(strip=True) if price_tag else "Price not specified"
        
        # Extract the listing URL
        link_tag = listing.find('a', class_='listing-search-item__link--title')
        if link_tag:
            link = link_tag['href']
            if not link.startswith('http'):
                link = "https://www.huurwoningen.com" + link
        else:
            link = "URL not specified"
        
        # Extract the number of rooms
        rooms_tag = listing.find('li', class_='illustrated-features__item--number-of-rooms')
        rooms = rooms_tag.get_text(strip=True) if rooms_tag else 'Not specified'

        # Extract the square meters (surface area)
        surface_area_tag = listing.find('li', class_='illustrated-features__item--surface-area')
        surface_area = surface_area_tag.get_text(strip=True) if surface_area_tag else 'Not specified'

        # Append listing details to result list
        result.append({
            "Address": address,
            "Price": price,
            "Rooms": rooms,
            "Surface Area": surface_area,
            "URL": link
        })
    
    return result

# Function to handle pagination by clicking the "Volgende" button
def fetch_all_pages_huurwoningen(driver):
    listings = []
    while True:
        # Parse the current page
        page_source = driver.page_source
        listings.extend(parse_listings_huurwoningen(page_source, driver))

        # Find the "Next" button using the arrow
        next_buttons = driver.find_elements(By.XPATH, '//li[@class="pagination__item pagination__item--next"]/a')
        
        # If the "Next" button is not found, break the loop (last page reached)
        if not next_buttons:
            print("Reached the last page, no more pages to navigate.")
            break

        try:
            # Scroll into view and click the button
            next_button = next_buttons[0]
            driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", next_button)
            time.sleep(2)  # Pause to mimic human interaction
            
            # Click the "Next" button
            next_button.click()
            print("Next button clicked, moving to the next page...")
            time.sleep(5)  # Delay for page to load

        except Exception as e:
            print("An error occurred while clicking the 'Next' button:", e)
            break
    return listings

# Main function to load cookies and fetch listings across multiple pages
def fetch_huurwoningen_with_pagination(url):
    #url = "https://www.huurwoningen.nl/in/amsterdam/?price=900-2500"

    # Set up Chrome WebDriver
    options = Options()
    if runheadless == 1:
        options.add_argument("--headless") # Headless mode can be disabled for debugging purposes
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")

    driver = webdriver.Chrome(options=options)

    # Load a generic URL first to load cookies
    driver.get("https://www.huurwoningen.com")
    driver.implicitly_wait(6)  # Wait for the page to load

    try:
        # Wait for the button to be present and clickable
        essential_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "onetrust-reject-all-handler"))
        )
    
        # Scroll into view to make sure it is visible
        driver.execute_script("arguments[0].scrollIntoView(true);", essential_button)
    
        # Attempt to click the button
        essential_button.click()
        print("Clicked on 'Alleen essentiële cookies' button.")
    except Exception as e:
        # Fallback to clicking using JavaScript in case standard click fails
        try:
            print("Standard click failed, trying JavaScript click.")
            essential_button = driver.find_element(By.ID, "onetrust-reject-all-handler")
            driver.execute_script("arguments[0].click();", essential_button)
            print("Clicked on 'Alleen essentiële cookies' button using JavaScript.")
        except Exception as js_e:
            print("Alleen essentiële cookies button not found or clickable after JavaScript attempt:", js_e)


    # Load cookies from a JSON file
    try:
        with open('huur_cookies.json', 'r') as cookies_file:
            cookies = json.load(cookies_file)
            for cookie in cookies:
                # Adjust the cookie format for Selenium
                cookie_dict = {
                    'name': cookie['name'],
                    'value': cookie['value'],
                    'domain': cookie['domain'],
                    'path': cookie['path'],
                    'secure': cookie.get('secure', False),
                    'httpOnly': cookie.get('httpOnly', False)
                }
                if 'expirationDate' in cookie:
                    cookie_dict['expiry'] = int(cookie['expirationDate'])
                driver.add_cookie(cookie_dict)
        print("Cookies loaded successfully!")
    except Exception as e:
        print("Failed to load cookies:", e)
        driver.quit()
        return []

    # Refresh the page to apply cookies
    driver.get(url)
    driver.implicitly_wait(5)
    print("Page loaded successfully! Title:", driver.title)

    # Fetch listings from all pages
    listings = fetch_all_pages_huurwoningen(driver)

    # Close the browser
    driver.quit()
    return listings



# Function to parse and return listings from the page
def parse_listings_pararius(page_source, driver):
    soup = BeautifulSoup(page_source, 'html.parser')
    
    # Find all listing containers
    listings = soup.find_all('section', class_='listing-search-item')
    result = []

    if not listings:
        print("No listings found. Please check the HTML structure or class name.")
        return result

    # Loop through listings and collect relevant details
    for idx, listing in enumerate(listings):
        try:
            # Extract the address using Selenium XPath
            address_xpath = f"(//div[contains(@class, 'listing-search-item__sub-title')])[{idx+1}]"
            address_element = driver.find_element(By.XPATH, address_xpath)
            address = address_element.text.strip() if address_element else "Address not specified"
        except Exception:
            # Fallback to BeautifulSoup extraction
            address_tag = listing.find('div', class_='listing-search-item__sub-title')
            address = address_tag.get_text(strip=True) if address_tag else "Address not specified"

        # Extract the price
        price_tag = listing.find('div', class_='listing-search-item__price')
        price = price_tag.get_text(strip=True) if price_tag else "Price not specified"
        
        # Extract the listing URL
        link_tag = listing.find('a', class_='listing-search-item__link--title')
        if link_tag:
            link = link_tag['href']
            if not link.startswith('http'):
                link = "https://www.pararius.com" + link
        else:
            link = "URL not specified"
        
        # Extract the number of rooms
        rooms_tag = listing.find('li', class_='illustrated-features__item--number-of-rooms')
        rooms = rooms_tag.get_text(strip=True) if rooms_tag else 'Not specified'

        # Extract the square meters (surface area)
        surface_area_tag = listing.find('li', class_='illustrated-features__item--surface-area')
        surface_area = surface_area_tag.get_text(strip=True) if surface_area_tag else 'Not specified'

        # Append listing details to result list
        result.append({
            "Address": address,
            "Price": price,
            "Rooms": rooms,
            "Surface Area": surface_area,
            "URL": link
        })
    
    return result

# Function to handle pagination by clicking the "Volgende" button
def fetch_all_pages_pararius(driver):
    listings = []
    while True:
        # Parse the current page
        page_source = driver.page_source
        listings.extend(parse_listings_pararius(page_source, driver))

        # Find the "Next" button using the arrow
        next_buttons = driver.find_elements(By.XPATH, '//li[@class="pagination__item pagination__item--next"]/a')
        
        # If the "Next" button is not found, break the loop (last page reached)
        if not next_buttons:
            print("Reached the last page, no more pages to navigate.")
            break

        try:
            # Scroll into view and click the button
            next_button = next_buttons[0]
            driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", next_button)
            time.sleep(2)  # Pause to mimic human interaction
            
            # Click the "Next" button
            next_button.click()
            print("Next button clicked, moving to the next page...")
            time.sleep(5)  # Delay for page to load

        except Exception as e:
            print("An error occurred while clicking the 'Next' button:", e)
            break
    return listings

# Main function to load cookies and fetch listings across multiple pages
def fetch_pararius_with_pagination(url):
    #url = "https://www.pararius.com/apartments/amsterdam/900-2500"

    # Set up Chrome WebDriver
    options = Options()
    if runheadless == 1:
        options.add_argument("--headless") # Headless mode can be disabled for debugging purposes
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")

    driver = webdriver.Chrome(options=options)

    # Load a generic URL first to load cookies
    driver.get("https://www.pararius.com")
    time.sleep(5)  # Wait for the page to load completely

    # Load cookies from a JSON file
    try:
        with open('pararius_cookies.json', 'r') as cookies_file:
            cookies = json.load(cookies_file)
            for cookie in cookies:
                driver.add_cookie(cookie)
        print("Cookies loaded successfully!")
    except Exception as e:
        print("Failed to load cookies:", e)
        driver.quit()
        return []

    # Refresh the page to apply cookies
    driver.get(url)
    time.sleep(5)  # Wait for the page to load completely
    print("Page loaded successfully! Title:", driver.title)

    # Fetch listings from all pages
    listings = fetch_all_pages_pararius(driver)

    # Close the browser
    driver.quit()
    return listings


def job():
    start_time = time.time()

    #valid_zipcodes = {"1011", "1012", "1015", "1016", "1017", "1018", "1072", "1073", "1074", "1091", "1092"}
    valid_zipcodes = {
    "1010", "1011", "1012", "1013", "1014", "1015", "1016", "1017", "1018", "1019",
    "1050", "1051", "1052", "1053", "1054",
    "1070", "1071", "1072", "1073", "1074", "1075", "1076", "1077", "1078", "1079",
    "1090", "1091", "1092", "1093", "1094", "1095", "1096", "1097", "1098", "1099"
    }
    funda_listings = fetch_funda_with_pagination(FUNDA_URL)
    huurwoningen_listings = fetch_huurwoningen_with_pagination(HUURWONINGEN_URL)
    pararius_listings = fetch_pararius_with_pagination(PARARIUS_URL)

    # Combine all listings into a master list
    #master_list = funda_listings
    master_list = funda_listings + huurwoningen_listings + pararius_listings

    # Process master list
    cleaned_list = []
    for listing in master_list:
        # Extract numeric values from price, rooms, and surface area
        price = re.sub(r'[^\d]', '', listing['Price'])
        rooms = re.sub(r'[^\d]', '', listing['Rooms'])
        surface_area = re.sub(r'[^\d]', '', listing['Surface Area'])
        
        # Extract zip code from address
        address = listing['Address']
        zip_code = address[:4] if address[:4].isdigit() else ""

        # Only include listings with valid zip codes
        if zip_code in valid_zipcodes and price.isdigit() and int(price) <= 2600:
            cleaned_list.append({
                "Zip Code": zip_code,
                "Address": address,
                "Price": int(price),
                "Rooms": int(rooms) if rooms.isdigit() else 0,
                "Surface Area": int(surface_area) if surface_area.isdigit() else 0,
                "URL": listing['URL']
            })

    # Check if cleaned_list is empty
    if not cleaned_list:
        print("No valid listings found.")
    else:
        # Sort the cleaned list according to the specified criteria
        sorted_list = sorted(cleaned_list, key=lambda x: (
            -x['Rooms'],
            list(valid_zipcodes).index(x['Zip Code']),
            x['Price'],
            -x['Surface Area']
        ))


        # Load the previous sorted list from file
        try:
            with open('sorted_list.json', 'r') as file:
                previous_sorted_list = json.load(file)
        except FileNotFoundError:
            previous_sorted_list = []

        # Compare new sorted list to the previous sorted list
        new_entries = [entry for entry in sorted_list if entry not in previous_sorted_list]

        #print(new_entries)
        # If there are new entries, update the sorted list file and send an email
        if new_entries:
            print("sending email")
            # Update the stored sorted list
            with open('sorted_list.json', 'w') as file:
                json.dump(sorted_list, file, indent=4)

            # Send email notification
            subject = "New Rental Listings Available"
            body = "The following new rental listings have been found:\n\n"
            for entry in new_entries:
                body += f"Address: {entry['Address']}\nPrice: {entry['Price']}\nRooms: {entry['Rooms']}\nSurface Area: {entry['Surface Area']}\nURL: {entry['URL']}\n{'-' * 40}\n"

            msg = MIMEMultipart()
            msg['From'] = SENDER_EMAIL
            msg['To'] = RECEIVER_EMAIL
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

        try:
            # Establish a secure session with Mailjet's SMTP server
            with smtplib.SMTP('in-v3.mailjet.com', 587) as server:
                server.starttls()  # Secure the connection using TLS
                server.login(MAILJET_API_KEY, MAILJET_SECRET_KEY)
                server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
            print("Email sent successfully.")
        except Exception as e:
            print(f"Failed to send email: {e}")


        # Print combined listings
        #for listing in sorted_list:
        #    print(f"Address: {listing['Address']}")
        #    print(f"Price: {listing['Price']}")
        #    print(f"Rooms: {listing['Rooms']}")
        #    print(f"Surface Area: {listing['Surface Area']}")
        #    print(f"URL: {listing['URL']}")
        #    print("-" * 40)

    # Print the total time taken
    end_time = time.time()
    print(f"Time taken to run the program: {end_time - start_time:.2f} seconds")

# Run the job once when the program starts
job()

schedule.every(5).minutes.do(lambda: (print("restarting job now"), job()))

while True:
    schedule.run_pending()
    time.sleep(1)    

