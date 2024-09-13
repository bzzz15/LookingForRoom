

# Room Rental Scraper for ibilik.my (Petaling Jaya)

[![Python Version](https://img.shields.io/badge/python-3.6%2B-blue)](https://www.python.org/downloads/)


This script is designed to scrape room rental listings from the [ibilik.my](https://www.ibilik.my/) website, specifically for the area of Petaling Jaya. It extracts relevant information about room rentals, filters them based on specified criteria, removes duplicates, and saves the data to Excel and CSV files.

---

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Code Explanation](#code-explanation)
- [Important Notes](#important-notes)
- [Troubleshooting](#troubleshooting)
- [License](#license)
- [Contact](#contact)
- [Acknowledgments](#acknowledgments)

---

## Features

- **Scrapes room listings** from ibilik.my for Petaling Jaya.
- **Extracts detailed information** such as:
  - Title
  - Price
  - Location
  - Publish Date
  - Details
  - Distance from a reference point
- **Filters listings** based on:
  - Maximum price
  - Maximum distance from a reference point (e.g., a university)
  - Publish date (only rooms posted within the last week)
- **Removes duplicate listings** based on location coordinates.
- **Utilizes multithreading** to improve performance.
- **Saves data** to `ibilik_rooms.xlsx` and `ibilik_rooms.csv`.

---

## Requirements

- **Python 3.6 or higher**
- **Google Chrome browser** installed on your system.
- **ChromeDriver** compatible with your version of Chrome (managed automatically by `webdriver-manager`).

### Python Packages:

- `selenium`
- `webdriver-manager`
- `beautifulsoup4`
- `pandas`
- `geopy`

---

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/LookingForRoom/ibilik-room-scraper.git
   cd ibilik-room-scraper
   ```

2. **Set Up a Virtual Environment (Optional but Recommended)**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Required Python Packages**

   ```bash
   pip install -r requirements.txt
   ```

   If you don't have a `requirements.txt`, install the packages directly:

   ```bash
   pip install selenium webdriver-manager beautifulsoup4 pandas geopy
   ```

---

## Usage

1. **Ensure Google Chrome is Installed**

   - Download and install Google Chrome from [here](https://www.google.com/chrome/).

2. **Run the Script**

   ```bash
   python ibilik_scraper.py
   ```

3. **Wait for the Script to Complete**

   - The script will output progress messages in the console.
   - It will process pages of listings, extract data, and save the results.

4. **Check the Output Files**

   - After completion, the data will be saved in:
     - `ibilik_rooms.xlsx`
     - `ibilik_rooms.csv`

---

## Configuration

You can adjust several parameters in the script to suit your needs:

- **Maximum Price (`max_price`)**

  ```python
  max_price = 10000  # Set your desired maximum price
  ```

- **Maximum Distance (`max_distance`)**

  ```python
  max_distance = 50  # Set your desired maximum distance in kilometers
  ```

- **Reference Point Coordinates (`reference_point`)**

  ```python
  reference_point = (
      dms_to_decimal("3°07'18.8\"N"),
      dms_to_decimal("101°39'24.3\"E")
  )
  ```

  - Replace the DMS coordinates with your reference location.

- **Number of Threads (`max_workers`)**

  ```python
  max_workers = 4  # Adjust based on your system capabilities
  ```

- **Start Page Number (`page_number`)**

  ```python
  page_number = 1  # Start from the first page
  ```

---

## Code Explanation

The script performs the following steps:

1. **Imports Necessary Libraries**

   - Handles web interactions, data parsing, calculations, and multithreading.

2. **Defines Helper Functions**

   - `dms_to_decimal(dms_str)`: Converts DMS coordinates to decimal degrees.
   - `extract_coordinates(driver, room_url)`: Extracts latitude and longitude from a room's detail page.
   - `get_room_coordinates(driver, room_url)`: Gets coordinates and calculates the distance from the reference point.
   - `process_room(room_url, publish_date_str)`: Processes a single room listing to extract data.

3. **Main Function (`main()`)**

   - Initializes variables and settings.
   - Uses Selenium to navigate through listing pages.
   - Uses BeautifulSoup to parse HTML content.
   - Utilizes multithreading to process multiple rooms concurrently.
   - Filters rooms based on publish date, price, and distance.
   - Removes duplicate listings based on coordinates.
   - Saves the collected data to Excel and CSV files.

4. **Execution Entry Point**

   - The script starts executing from the `main()` function when run directly.

---

## Important Notes

- **Google Chrome Requirement**

  - **Google Chrome must be installed** on your system for the script to work.
  - The script uses ChromeDriver to automate Chrome browser actions.

- **Website Structure Changes**

  - The script relies on specific HTML structures and class names.
  - If the website updates its layout, you may need to update the selectors in the script.
  - Use browser developer tools to inspect elements and find the correct class names.

- **Ethical Considerations**

  - **Respect the website's terms of service and robots.txt file.**
  - Use the script responsibly and avoid overloading the website with requests.
  - Consider adding delays or adjusting threading if necessary.

---

## Troubleshooting

- **Common Issues and Solutions**

  - **TimeoutException**

    - If you encounter a `TimeoutException`, the script may not be finding elements within the specified time.
    - **Solution:** Increase the timeout duration or check if the selectors match the website's current structure.

  - **No Data Collected**

    - If the script runs but no data is saved, it may not be finding any listings.
    - **Solution:** Verify that the CSS selectors in the script match the website's HTML elements.

  - **Selenium Errors**

    - Ensure that all required packages are installed and up to date.
    - Check for any typos or syntax errors in the script.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Contact

For any questions or issues, please contact [coolbadrtv1@gmail.com](mailto:coolbadrtv1@gmail.com).

---

## Acknowledgments

- **Selenium** for browser automation.
- **BeautifulSoup** for HTML parsing.
- **Geopy** for geographical calculations.
- **ibilik.my** for providing the data.
