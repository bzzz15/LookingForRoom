import re
import time
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
from bs4 import BeautifulSoup
from geopy.distance import geodesic
from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def dms_to_decimal(dms_str: str) -> float:
    # Function to convert DMS (Degrees, Minutes, Seconds) format to decimal degrees
    dms_str = dms_str.strip()
    dms_regex = re.compile(
        r'(\d+)[°\s]+(\d+)[\'\s]+(\d+(?:\.\d+)?)[\"\s]*([NSEW])',
        re.IGNORECASE
    )
    match = dms_regex.match(dms_str)
    if not match:
        return None
    degrees, minutes, seconds, direction = match.groups()
    decimal = float(degrees) + float(minutes) / 60 + float(seconds) / 3600
    if direction.upper() in ['S', 'W']:
        decimal = -decimal
    return decimal

def extract_coordinates(driver, room_url: str) -> tuple:
    try:
        driver.get(room_url)
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "loadMap"))
        ).click()
        time.sleep(2)
        iframe = driver.find_element(By.TAG_NAME, "iframe")
        src = iframe.get_attribute("src")

        # Attempt to extract coordinates using regex patterns
        patterns = [
            r"q=([-.\d]+),([-.\d]+)",
            r"center=([-.\d]+)%2C([-.\d]+)",
            r"@([-.\d]+),([-.\d]+),",
        ]

        for pattern in patterns:
            match = re.search(pattern, src)
            if match:
                latitude = float(match.group(1))
                longitude = float(match.group(2))
                return (latitude, longitude)

        print(f"Could not find coordinates in src URL: {src}")
        return None

    except Exception as e:
        print(f"Error extracting coordinates from {room_url}: {e}")
        return None

def get_room_coordinates(driver, room_url):
    coordinates = extract_coordinates(driver, room_url)
    if coordinates is None:
        return None, None
    distance = geodesic(reference_point, coordinates).kilometers
    return coordinates, distance

def process_room(args):
    room, publish_date_str = args
    room_url = room['href']
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("user-agent=Mozilla/5.0")
    driver = webdriver.Chrome(service=Service(driver_path), options=chrome_options)
    try:
        title = room['title']
        rental_price = float(room['data-content-rental'])
        if rental_price > max_price:
            return None
        location_element = room.find_next('div', class_='lightblue')
        location = location_element.get_text(strip=True) if location_element else "N/A"
        room_details_element = room.find_next('div', class_='room-details')
        room_details = room_details_element.get_text(separator=' | ', strip=True) if room_details_element else "N/A"
        coordinates, distance = get_room_coordinates(driver, room_url)
        if coordinates is None or distance is None or distance > max_distance:
            return None
        rounded_coords = (round(coordinates[0], 5), round(coordinates[1], 5))
        return {
            'Title': title,
            'Price (RM)': rental_price,
            'Link': room_url,
            'Location': location,
            'Publish Date': publish_date_str,
            'Details': room_details,
            'Distance (km)': round(distance, 2),
            'Coordinates': rounded_coords
        }
    except Exception as e:
        print(f"Error processing room at {room_url}: {e}")
        return None
    finally:
        driver.quit()

def main():
    global reference_point, max_price, max_distance, driver_path
    room_data = []
    base_url = "https://www.ibilik.my/rooms/petaling_jaya?location_search=8&location_search_name=Petaling+Jaya%2C+Selangor&max=500&min=&order_by=&room_preferences[0]=&room_preferences[1]=34&room_preferences[2]=p_39&room_types[0]=Single+Room&sort_by=&page="
    page_number = 1
    max_price = 1000  # Adjust as needed
    max_distance = 10  # Adjust as needed
    reference_point = (
        dms_to_decimal("3°07'18.8\"N"),
        dms_to_decimal("101°39'24.3\"E")
    )
    current_date = datetime.now()
    one_week_ago = current_date - timedelta(weeks=1)
    driver_path = ChromeDriverManager().install()
    seen_coordinates = set()
    max_workers = 4  # Adjust based on your system capabilities
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("user-agent=Mozilla/5.0")
    main_driver = webdriver.Chrome(service=Service(driver_path), options=chrome_options)
    try:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            while True:
                url = f'{base_url}{page_number}'
                print(f"Processing page: {page_number}")
                main_driver.get(url)
                try:
                    WebDriverWait(main_driver, 20).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'a[data-list-type="Room Rental Search"]'))
                    )
                except TimeoutException:
                    print(f"No listings found on page {page_number}.")
                    break
                page_source = main_driver.page_source
                soup = BeautifulSoup(page_source, 'html.parser')
                rooms = soup.find_all('a', {'data-list-type': 'Room Rental Search'})
                print(f"Found {len(rooms)} rooms on page {page_number}.")
                if not rooms:
                    break
                futures = []
                all_rooms_old = True
                for room in rooms:
                    link = room['href']
                    publish_date_element = room.find_next('i')
                    if publish_date_element:
                        publish_date_str = publish_date_element.text.replace('Publish Date: ', '').strip()
                        try:
                            publish_date = datetime.strptime(publish_date_str, '%d %b %Y')
                        except ValueError:
                            publish_date = None
                    else:
                        publish_date = None
                        publish_date_str = "N/A"
                    if publish_date and publish_date >= one_week_ago:
                        all_rooms_old = False
                    elif publish_date and publish_date < one_week_ago:
                        continue
                    futures.append(executor.submit(process_room, (room, publish_date_str)))
                for future in as_completed(futures):
                    try:
                        result = future.result()
                        if result is None:
                            continue
                        rounded_coords = result['Coordinates']
                        if rounded_coords in seen_coordinates:
                            continue
                        seen_coordinates.add(rounded_coords)
                        del result['Coordinates']
                        room_data.append(result)
                    except Exception as e:
                        print(f"An error occurred: {e}")
                if all_rooms_old:
                    print("All rooms on this page are older than one week. Stopping.")
                    break
                page_number += 1
                time.sleep(2)
    finally:
        main_driver.quit()
    if room_data:
        df = pd.DataFrame(room_data)
        df.to_excel('ibilik_rooms.xlsx', index=False)
        df.to_csv('ibilik_rooms.csv', index=False)
        print("Data has been saved to 'ibilik_rooms.xlsx' and 'ibilik_rooms.csv'.")
    else:
        print("No data was collected.")

if __name__ == "__main__":
    main()
