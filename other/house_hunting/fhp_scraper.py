from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests
import time
import schedule
import json
import os
import re
import smtplib
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))

# Email configuration - set these in your shell env or a local .env file (see .env.example)
SENDER_EMAIL = os.environ['SENDER_EMAIL']
RECEIVER_EMAIL = os.environ['RECEIVER_EMAIL']
MAILJET_API_KEY = os.environ['MAILJET_API_KEY']
MAILJET_SECRET_KEY = os.environ['MAILJET_SECRET_KEY']

# In Amsterdam only specific neighbourhoods are wanted, so those are pinned down by
# 4-digit postcode (PC4). Order here is preference order: it also ranks the email listings.
AMSTERDAM_ZIPCODES = (
    [str(z) for z in range(1011, 1020)]    # Centrum incl. Jordaan
    + [str(z) for z in range(1071, 1080)]  # Zuid + De Pijp, incl. 1079 (Buitenveldert edge)
    + ['1082']                             # Buitenveldert/Zuidas - rest of Buitenveldert (1080-1081, 1083+) still excluded
    + [str(z) for z in range(1051, 1060)]  # West incl. Oud-West / Bos en Lommer / De Baarsjes
    + [str(z) for z in range(1091, 1100)]  # Oost - IJburg (1086-1088) deliberately excluded
)                                          # Noord deliberately excluded

# These towns are wanted in full, so they are searched by name rather than by postcode.
OTHER_CITIES = ('haarlem', 'weesp', 'muiden')
OTHER_CITY_ZIPCODES = (
    [str(z) for z in range(2011, 2038)]    # Haarlem
    + ['1380', '1381', '1382', '1383']     # Weesp
    + ['1398']                             # Muiden
)


def build_funda_url(areas):
    # Funda takes postcodes and city names as search areas and mixes them freely.
    # It silently caps at 100 areas, so keep any one query well under that.
    return (
        'https://www.funda.nl/zoeken/huur?selected_area=['
        + ','.join(f'%22{area}%22' for area in areas)
        + ']&price=%221000-2000%22&object_type=[%22house%22,%22apartment%22]'
        + '&publication_date=%223%22&floor_area=%220-100%22&rooms=%220-2%22&bedrooms=%220-3%22'
    )


def build_huurwoningen_urls(cities):
    # Huurwoningen has no postcode search - "/in/1011/" silently returns nationwide
    # results - so search per city and let the zipcode filter narrow it down.
    return [
        f'https://www.huurwoningen.com/in/{city}/?price=900-2000&since=3'
        for city in cities
    ]


# Kamernet listing-type codes (searchCategories) - 1 is Room, which we don't want.
KAMERNET_TYPE_SLUGS = {2: 'apartment', 4: 'studio'}


def build_kamernet_urls(cities):
    # searchCategories=2,4 (comma-separated, not repeated/bracketed query keys) is
    # the only format Kamernet's Next.js route actually parses into multiple values.
    return [
        f'https://kamernet.nl/en/for-rent/properties-{city}?searchCategories=2,4'
        for city in cities
    ]


# The Amsterdam search runs continuously; the other-towns search is run on demand
# with "--other". They keep separate state files so neither resets the other's history.
AMSTERDAM_PROFILE = {
    'name': 'Amsterdam',
    'funda_areas': AMSTERDAM_ZIPCODES,
    'huurwoningen_cities': ('amsterdam',),
    'kamernet_cities': ('amsterdam',),
    'pararius_url': 'https://www.pararius.com/apartments/amsterdam/apartment/900-2000/since-3',
    'zipcodes': AMSTERDAM_ZIPCODES,
    'state_file': 'sorted_list.json',
}

OTHER_PROFILE = {
    'name': 'Haarlem/Weesp/Muiden',
    'funda_areas': OTHER_CITIES,
    'huurwoningen_cities': OTHER_CITIES,
    'kamernet_cities': OTHER_CITIES,
    'pararius_url': None,
    'zipcodes': OTHER_CITY_ZIPCODES,
    'state_file': 'sorted_list_other.json',
}

runheadless = 0

# Funda (Akamai) and Pararius (Cloudflare) serve a bot wall - "Access Denied" /
# "Just a moment..." - to anything that looks automated. A spoofed user agent that
# doesn't match the real browser is the biggest giveaway, so keep Chrome's own UA
# and hide the automation flags instead.
def make_driver():
    options = Options()
    if runheadless == 1:
        options.add_argument("--headless") # Headless mode can be disabled for debugging purposes
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(options=options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument",
                           {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"})
    driver.set_page_load_timeout(90)  # never hang indefinitely on a dead/stalled browser
    return driver

# Function to parse and return listings from the page
# NOTE: Funda redesigned their search page (Tailwind-based, no more data-test-id
# attributes like "street-name-house-number"/"price-rent"/"object-image-link").
# The only stable hook left is the a[data-testid="listingDetailsAddress"] anchor.
def parse_listings_funda(page_source):
    soup = BeautifulSoup(page_source, 'html.parser')

    address_links = soup.find_all('a', attrs={'data-testid': 'listingDetailsAddress'})
    result = []

    if not address_links:
        print("No listings found. Please check the HTML structure or class name.")
        return result

    # Loop through listings and collect relevant details
    for link_tag in address_links:
        # Extract the postal code and city (used downstream as "Address")
        location_tag = link_tag.find('div', class_='text-neutral-80')
        location = location_tag.get_text(strip=True) if location_tag else "Location not specified"

        # Extract the price (sibling block rendered just before the address anchor)
        price_container = link_tag.parent.find('div', class_='font-semibold') if link_tag.parent else None
        price_tag = price_container.find('div', class_='truncate') if price_container else None
        price = price_tag.get_text(strip=True) if price_tag else "Price not specified"

        # Extract the listing URL
        link = link_tag.get('href')
        if link:
            if not link.startswith('http'):
                link = "https://www.funda.nl" + link
        else:
            link = "URL not specified"

        # Extract the number of bedrooms and surface area from the feature list
        # that follows the address anchor (icon + text per <li>, no stable class name)
        bedrooms = 'Not specified'
        surface_area = 'Not specified'

        features_list = link_tag.find_next_sibling('ul')
        if features_list:
            for detail in features_list.find_all('li'):
                span = detail.find('span')
                text = span.get_text(strip=True) if span else detail.get_text(strip=True)
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

# Funda pagination is now driven by a "search_result=<page>" URL query param -
# there's no more clickable "Volgende" button in the rendered page.
# Akamai lets the first request of a fresh browser through, then blocks the session
# with "Access Denied" once its sensor script flags the browser as automated. So
# every page gets its own browser, and no homepage visit or stored cookies first.
def fetch_funda_with_pagination(url):
    listings = []
    page = 1
    while True:
        page_url = url if page == 1 else f"{url}&search_result={page}"
        driver = make_driver()
        try:
            driver.get(page_url)
            time.sleep(5)  # Wait for the page to load completely
            print("Page loaded successfully! Title:", driver.title)
            if driver.title == "Access Denied":
                print("Funda blocked the request (Akamai) - skipping Funda this run.")
                break
            page_listings = parse_listings_funda(driver.page_source)
        finally:
            driver.quit()

        # Past the last page Funda serves the last page again rather than an empty one
        seen = {l['URL'] for l in listings}
        page_listings = [l for l in page_listings if l['URL'] not in seen]
        if not page_listings:
            print("Reached the last page, no more pages to navigate.")
            break

        listings.extend(page_listings)
        page += 1
        if page > 50:  # safety cap against an accidental infinite loop
            print("Hit pagination safety cap (50 pages).")
            break
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
    page = 0
    while True:
        # When a town has no listings at all (Weesp, Muiden), Huurwoningen serves a
        # "no search results" page filled with nationwide suggestions instead. Crawling
        # those just wastes minutes on listings the zipcode filter throws away.
        page_source = driver.page_source
        if 'no-search-results' in page_source:
            print("No listings for this area - skipping the suggested alternatives.")
            break

        # Parse the current page
        listings.extend(parse_listings_huurwoningen(page_source, driver))

        page += 1
        if page > 50:  # safety cap against an accidental infinite loop
            print("Hit pagination safety cap (50 pages).")
            break

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
def fetch_huurwoningen_with_pagination(urls):
    # One search per city (no postcode search available), all in a single browser session.

    # Set up Chrome WebDriver
    driver = make_driver()

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

    # Search each city in turn, reusing the same session
    listings = []
    for url in urls:
        driver.get(url)
        driver.implicitly_wait(5)
        print("Page loaded successfully! Title:", driver.title)
        listings.extend(fetch_all_pages_huurwoningen(driver))

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
    driver = make_driver()

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


# Kamernet server-renders a Next.js "__NEXT_DATA__" JSON blob with the full listing
# set on every page (search results and listing detail alike) - no bot wall here,
# so plain requests is enough and there's no need for Selenium.
KAMERNET_HEADERS = {
    'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
                    '(KHTML, like Gecko) Chrome/130.0 Safari/537.36')
}


def fetch_kamernet_next_data(url):
    response = requests.get(url, headers=KAMERNET_HEADERS, timeout=30)
    match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', response.text, re.S)
    return json.loads(match.group(1)) if match else None


# The search-results JSON has no postal code (only street/city names), so the
# zipcode filter in job() needs a second request per listing - the detail page's
# JSON does carry "postalCode" - to resolve the neighbourhood.
def fetch_kamernet_listing_detail(item):
    type_slug = KAMERNET_TYPE_SLUGS.get(item['listingType'], 'properties')
    url = (f"https://kamernet.nl/en/for-rent/{type_slug}-{item['citySlug']}"
           f"/{item['streetSlug']}/{type_slug}-{item['listingId']}")

    postal_code = ''
    bedrooms = None
    try:
        data = fetch_kamernet_next_data(url)
        details = data['props']['pageProps']['targetPageProps']['listingDetails']
        postal_code = details.get('postalCode') or ''
        bedrooms = details.get('numOfBedrooms')
    except Exception as e:
        print(f"Kamernet: failed to load listing detail {url}: {e}")

    return {
        "Address": f"{postal_code} {item['street']}, {item['city']}".strip(),
        "Price": f"€{item['totalRentalPrice']}",
        "Rooms": str(bedrooms) if bedrooms is not None else 'Not specified',
        "Surface Area": f"{item['surfaceArea']} m²",
        "URL": url
    }


def fetch_kamernet_with_pagination(urls):
    listings = []
    for url in urls:
        page = 1
        while True:
            page_url = url if page == 1 else f"{url}&pageNo={page}"
            try:
                data = fetch_kamernet_next_data(page_url)
            except Exception as e:
                print(f"Kamernet: failed to load {page_url}: {e}")
                break
            if not data:
                print("Kamernet: couldn't find page data - skipping.")
                break

            raw_listings = data['props']['pageProps']['targetPageProps']['findListingsResponse']['listings']
            if not raw_listings:
                print("Reached the last page, no more pages to navigate.")
                break

            for item in raw_listings:
                listings.append(fetch_kamernet_listing_detail(item))
                time.sleep(0.3)  # one request per listing for the detail page - stay polite

            page += 1
            if page > 50:  # safety cap against an accidental infinite loop
                print("Hit pagination safety cap (50 pages).")
                break
    return listings


def job(profile):
    start_time = time.time()
    print(f"=== Searching: {profile['name']} ===")

    zipcodes = profile['zipcodes']
    valid_zipcodes = set(zipcodes)

    master_list = fetch_funda_with_pagination(build_funda_url(profile['funda_areas']))
    master_list += fetch_huurwoningen_with_pagination(
        build_huurwoningen_urls(profile['huurwoningen_cities'])
    )
    master_list += fetch_kamernet_with_pagination(
        build_kamernet_urls(profile['kamernet_cities'])
    )
    if profile['pararius_url']:
        master_list += fetch_pararius_with_pagination(profile['pararius_url'])

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
        if (zip_code in valid_zipcodes and price.isdigit() and int(price) <= 2000
                and (not rooms.isdigit() or int(rooms) <= 2)):
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
            zipcodes.index(x['Zip Code']),
            x['Price'],
            -x['Surface Area']
        ))


        # Load the previous sorted list from file
        try:
            with open(profile['state_file'], 'r') as file:
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
            with open(profile['state_file'], 'w') as file:
                json.dump(sorted_list, file, indent=4)

            # Send email notification
            subject = f"New Rental Listings Available - {profile['name']}"
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

if __name__ == '__main__':
    if '--other' in sys.argv:
        # One-off search of Haarlem / Weesp / Muiden, then exit.
        job(OTHER_PROFILE)
    else:
        # Amsterdam: run once at startup, then every 30 minutes.
        job(AMSTERDAM_PROFILE)
        schedule.every(30).minutes.do(
            lambda: (print("restarting job now"), job(AMSTERDAM_PROFILE))
        )
        while True:
            schedule.run_pending()
            time.sleep(1)

