from geopy.distance import geodesic
from selenium import webdriver
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from webdriver_manager.chrome import ChromeDriverManager
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta

def dms_to_decimal(dms_str: str) -> float:
    parts = re.split('[°\'"]+', dms_str)
    degrees = float(parts[0])
    minutes = float(parts[1]) / 60
    seconds = float(parts[2]) / 3600
    decimal = degrees + minutes + seconds
    if 'S' in dms_str or 'W' in dms_str:
        decimal = -decimal
    return decimal

def extract_coordinates(driver, room_url: str) -> tuple:
    try:
        driver.get(room_url)
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "loadMap"))
        ).click()
        iframe = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "iframe"))
        )
        src = iframe.get_attribute("src")
        coordinates = src.split("q=")[1].split(",")
        latitude = float(coordinates[0])
        longitude = float(coordinates[1])
        return (latitude, longitude)
    except (TimeoutException, NoSuchElementException, Exception):
        return None

def get_room_coordinates(driver, room_url):
    coordinates = extract_coordinates(driver, room_url)
    if coordinates is None:
        return None
    reference_point = (3.12217, 101.65656)  # University coordinates
    distance = geodesic(reference_point, coordinates).kilometers
    return distance

room_data = []

base_url = "https://www.ibilik.my/rooms/petaling_jaya?location_search=8&location_search_name=Petaling+Jaya%2C+Selangor&max=500&min=&order_by=&room_preferences[0]=&room_preferences[1]=34&room_preferences[2]=p_39&room_types[0]=Single+Room&sort_by=&page="
page_number = 1
max_price = 1000  # Set the maximum price threshold

# Convert the university coordinates from DMS to decimal
reference_point = (dms_to_decimal("3°07'18.8\"N"), dms_to_decimal("101°39'24.3\"E"))

current_date = datetime.now()
one_week_ago = current_date - timedelta(weeks=1)
chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

try:
    while True:
        url = f'{base_url}{page_number}'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        rooms = soup.find_all('a', {'data-list-type': 'Room Rental Search'})
        if not rooms:
            break

        for room in rooms:
            title = room['title']
            rental_price = float(room['data-content-rental'])

            if rental_price > max_price:
                continue

            link = room['href']
            location_element = room.find_next('div', class_='lightblue')
            location = location_element.get_text(strip=True) if location_element else "N/A"

            publish_date_element = room.find_next('i')
            if publish_date_element:
                publish_date_str = publish_date_element.text.replace('Publish Date: ', '')
                try:
                    publish_date = datetime.strptime(publish_date_str, '%d %b %Y')
                except ValueError:
                    publish_date = None
            else:
                publish_date = None

            if publish_date and publish_date < one_week_ago:
                break

            room_details_element = room.find_next('div', class_='room-details')
            room_details = room_details_element.get_text(separator=' | ', strip=True) if room_details_element else "N/A"

            distance = get_room_coordinates(driver, link)
            if distance is None or distance > 10:
                continue

            room_data.append({
                'Title': title,
                'Price (RM)': rental_price,
                'Link': link,
                'Location': location,
                'Publish Date': publish_date_str if publish_date else "N/A",
                'Details': room_details,
                'Distance (km)': distance
            })

        page_number += 1
finally:
    driver.quit()

df = pd.DataFrame(room_data)
df.to_excel('ibilik_rooms.xlsx', index=False)
df.to_csv('ibilik_rooms.csv', index=False)
