import time
import pandas as pd

from io import BytesIO
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from scrapper.models import RegionMapping

from .region import get_continent

country_dic = {
    
    "Argentina": "South America",
    "Chile": "South America",
    "Canary Islands": "Europe",
    "King George Island": "Antarctica",
    "Norway": "South America"
}


def get_combined_continent(location1, location2, get_continent_func):
    """
    Determines the continent(s) based on two locations.
    Extracts the last part of the location (e.g., "South Africa" from "Johannesburg, South Africa").
    If both locations map to the same continent, returns the single continent.
    If they map to different continents, returns both as a comma-separated string.

    Args:
        location1 (str): The first location (city or country).
        location2 (str): The second location (city or country).
        get_continent_func (callable): Function to determine continent from location.

    Returns:
        str: Continent name or comma-separated continent names.
    """
    # Extract the last part of the location (after the last comma)
    # country1 = location1.split(",")[-1].strip()
    # country2 = location2.split(",")[-1].strip()
    # Determine continents 
    continent1 = get_continent_func.get(location1,'')
    continent2 = get_continent_func.get(location2,'')

    # Compare continents and return the result
    if continent1 == continent2:
        return continent1
    else:
        return f"{continent1}, {continent2}"   


# Helper Functions
def click_interline_tab(driver):
    """Clicks on the 'Interline' tab."""
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, "//a[text()='Interline']"))
    ).click()
    print("Clicked 'Interline' tab.")


def click_more_search_options(driver):
    """Clicks on the 'More Search Options' link."""
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, "//a[text()='more search options']"))
    ).click()
    print("Clicked 'More Search Options' link.")


def login_if_needed(driver):
    """Checks if login is required and logs in if necessary."""
    try:
        email_input = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//input[@name='LogEmail']"))
        )
        if email_input.is_displayed():
            print("Login page detected. Logging in...")
            email_input.send_keys("test@example.com")
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "button[type='submit']"))
            ).click()
            print("Logged in successfully.")
    except Exception as e:
        print("No login required or error during login check:", e)
        

not_found_cruise_lines = []  # Global list to track not-found cruise line

def select_cruise_line(driver, cruise_line):
    """Selects a cruise line from the dropdown menu and tracks not-found cruise lines."""
    dropdown = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, "//select[@id='LineID']"))
    )
    select = Select(dropdown)
    found = False  # Flag to track if cruise line is found
    for option in select.options:
        if cruise_line in option.text:  # Check if the cruise line matches
            select.select_by_visible_text(option.text)
            print(f"Selected cruise line: {cruise_line}")
            found = True
            break
    if not found:  # If cruise line is not found
        print(f"Cruise line not found: {cruise_line}")
        not_found_cruise_lines.append(cruise_line)


def select_stateroom(driver, stateroom):
    """Selects a stateroom type from the dropdown menu."""
    dropdown = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, "//select[@id='Stateroom']"))
    )
    select = Select(dropdown)
    for option in select.options:
        if stateroom in option.text:
            select.select_by_visible_text(option.text)
            print(f"Selected stateroom: {stateroom}")
            break


not_found_cruise_lines = []
def check_cruise_line(driver, cruise_line):
    """Selects a cruise line from the dropdown menu."""
    dropdown = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, "//select[@id='LineID']"))
    )
    select = Select(dropdown)
    found = False
    for option in select.options:
        if cruise_line in option.text:
            select.select_by_visible_text(option.text)
            print(f"Selected cruise line: {cruise_line}")
            found = True
            break
    if not found:
        print(f"Cruise line not found: {cruise_line}")
        not_found_cruise_lines.append(cruise_line)

import pandas as pd

# Function to read the Excel file and return a mapping of continent to region
def load_continent_region_mapping(file_path):
    # Read the Excel file using pandas
    df = pd.read_excel(file_path)
    # Ensure the 'port' column values are lowercase
    df['port'] = df['port'].str.lower()
   
    # Create a dictionary mapping each continent to its corresponding region
    continent_region_mapping = dict(zip(df['port'], df['Region']))
    country_mapping = dict(zip(df['port'], df['Country']))
    return continent_region_mapping, country_mapping

def convert_date(date_str):
    """Converts date string to the format 'MM/DD/YYYY'."""
    try:
        # Clean up the date string by removing extra spaces and commas
        date_str = date_str.replace(",", " ")  # Remove any commas
        date_parts = date_str.split(" ")

        # Check if the year exists in the date string
        if len(date_parts) == 2:  # Date without year
            current_year = datetime.now().year
            date_str = f"{date_str} {current_year}"  # Add current year

        # Convert to datetime object
        date_obj = datetime.strptime(date_str, "%b %d %Y")
        
        # Return the formatted date
        return date_obj.strftime("%m/%d/%Y")
    
    except Exception as e:
        print(f"Error in date conversion: {e}")
        return date_str


def extract_data_from_results(driver):
    """Extracts cruise deal data from the results table."""
    results_container = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, "//div[@id='bodyContainer']"))
    )
    html_content = results_container.get_attribute('outerHTML')
    soup = BeautifulSoup(html_content, 'html.parser')
    rows = soup.select('table.ticker.deals tr')
    data = []

    region_file = RegionMapping.objects.all().first()
    # If no RegionMapping object exists, use the default file path
    if not region_file:
        region_file = "scrapper/cruise_line_files/Regions.xlsx"  # Path to your default Excel file
    else:
        # If a RegionMapping object exists, use the file from the object
        region_file = region_file.file.path
    continent_region_mapping, country_mapping = load_continent_region_mapping(region_file)
    for row in rows:
        cols = row.find_all('td')

        if cols:
            cruise_line = cols[5].text.strip().replace("\n", " / ")
            deal = [
                cols[1].text.strip(),  # Length
                convert_date(cols[2].text.strip()),  # Month
                cols[3].text.strip(),  # Port From
                cols[4].text.strip(),  # Port To
                get_combined_continent(cols[3].text.strip().lower(), cols[4].text.strip().lower(), continent_region_mapping),  # Region
                country_mapping.get(cols[4].text.strip().lower(), ''),  #Country (Placeholder)
                cruise_line,  # Cruise Line
                cruise_line.split(" / ")[-1].strip(),  # Ship (Placeholder)
                cols[6].text.strip() if cols[6].text.strip() == "-" else '',  # Stars
                cols[7].text.strip() if cols[7].text.strip() == "-" else '',  # Was
                cols[8].text.strip() if cols[8].text.strip() == "-" else '',  # Price
                cols[9].text.strip(),  # Save
                cols[0].text.strip(),  # Ref
                ""  # Notes (Placeholder)
                # get_combined_continent(cols[3].text.strip(), cols[4].text.strip(), get_continent)
                # f"{country_dic.get(cols[3].text.strip(), "Asia")},{country_dic.get(cols[4].text.strip(), "Asia")}"
            ]
            data.append(deal)

    print(f"Extracted {len(data)} rows of data.")
    return data


def generate_excel_file(data, not_found_cruise_lines, file_name="cruise_deals.xlsx"):
    """
    Generates an Excel file with two sheets: one for extracted data and another for not-found cruise lines.
    """
    # Create a Pandas DataFrame for the main data
    columns = [
        "Length", "Month", "Port From", "Port To", "Region",
        "Country", "Cruise Line", "Ship", "Stars", "Was",
        "Price", "Save", "Ref", "Notes"
    ]
    df_data = pd.DataFrame(data, columns=columns)

    # Create a DataFrame for the not-found cruise lines
    df_not_found = pd.DataFrame(not_found_cruise_lines, columns=["Not Found Cruise Lines"])

    # Write to an Excel file in memory with two sheets
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_data.to_excel(writer, index=False, sheet_name="file_name", na_rep="")
        df_not_found.to_excel(writer, index=False, sheet_name="Not Found Cruise Lines")
    
    # Set the pointer to the beginning of the BytesIO object
    output.seek(0)

    return output


def get_cruise_lines_from_excel(file):
    """Reads cruise lines from an Excel file."""
    df = pd.read_excel(file)
    return df['Cruise Line'].tolist()

# Main Processing Function
def process_script(driver, cruise_lines, script_type):
    """
    Processes the script based on the specified type.

    Args:
        driver (webdriver): Selenium WebDriver instance.
        cruise_lines (list): List of cruise lines to process.
        script_type (str): The type of script to run ("script1", "script2", "script3").

    Returns:
        list: A list of extracted data from the results.
    """
    data = []

    if script_type in ["script2"]:
        click_interline_tab(driver)

    if script_type == "script3":
        click_more_search_options(driver)
        stateroom_types = ['Cheapest oceanview', 'Cheapest balcony']
    else:
        stateroom_types = None

    for cruise_line in cruise_lines:
        select_cruise_line(driver, cruise_line)
        time.sleep(3)

        staterooms_to_process = stateroom_types if stateroom_types else [None]
        for stateroom in staterooms_to_process:
            if stateroom:
                select_stateroom(driver, stateroom)

            WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.ID, "fabShowMeTheDeals"))
            ).click()
            print(f"Clicked 'Show me the deals' for cruise line: {cruise_line}, stateroom: {stateroom}")

            login_if_needed(driver)
            cruise_data = extract_data_from_results(driver)
            data.extend(cruise_data)

            if script_type == "script3":
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.XPATH, "//a[text()='Custom Search']"))
                ).click()

    return data


# Main Function
def main(file, script_type="script1", filename="cruiseline"):
    """Main function to execute the script."""

    # Configure Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run without GUI
    chrome_options.add_argument("--no-sandbox")  # Recommended for Linux servers
    chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome resource issues
    chrome_options.add_argument("--disable-gpu")  # Disable GPU (not needed for headless)

    # Initialize WebDriver
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        driver.get("https://www.vacationstogo.com/")
        print("Page Title:", driver.title)
        login_if_needed(driver)
        cruise_lines = get_cruise_lines_from_excel(file)
        data = process_script(driver, cruise_lines, script_type)
        
        # Generate Excel file with not-found cruise lines
        return generate_excel_file(data, not_found_cruise_lines, file_name=filename)
    finally:
        driver.quit()

