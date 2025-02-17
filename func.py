from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from drive_authenticate import write_results_to_csv1, upload_csv_to_drive
import os
import time
from urllib.parse import quote
from bs4 import BeautifulSoup

import time

# Define the path to the static folder and the CSV file where results will be saved
static_folder = os.path.join(os.path.dirname(__file__), 'static')
file_path = os.path.join(static_folder, 'details_.csv')

def scroll_extract(driver, items):
    """
    Extracts profile details from the list of items (profiles) and writes them to a CSV file.
    
    Args:
        driver: The Selenium WebDriver instance.
        items: A list of BeautifulSoup elements representing individual profiles.
    
    Returns:
        The result of writing the extracted data to a CSV file.
    """
    results = []
    
    for item in items:
        try:
            # Extract the name of the profile
            name = item.select_one('span.t-16').get_text(strip=True)

            # Extract the profile link and ensure it's a full URL
            profile_link = item.select_one('a[data-test-app-aware-link]')['href']
            if profile_link.startswith('/'):
                profile_link = f"https://www.linkedin.com{profile_link}"
            
            # Extract the current role of the profile
            current_role = item.select_one('div.t-14.t-black.t-normal').get_text(strip=True)
            
            # Extract the location of the profile
            location = item.select_one('div.t-14.t-normal:last-child').get_text(strip=True)
            
            # Append the extracted data to the results list
            results.append({
                'Name': name,
                'Current Role': current_role,
                'Location': location,
                'Profile Link': profile_link
            })
            
        except Exception as e:
            print(f"Error processing item: {str(e)}")
            continue
    
    # Write the results to a CSV file
    return write_results_to_csv1(results, file_path)

def scrape_results_page(driver, scraping_status):
    """
    Scrapes profile data from the LinkedIn search results page, handles pagination, and uploads the results to Google Drive.
    
    Args:
        driver: The Selenium WebDriver instance.
        scraping_status: A dictionary to track the scraping progress.
    
    Returns:
        The result of uploading the CSV file to Google Drive.
    """
    # Update the scraping status to indicate that scraping is in progress
    scraping_status.update({'in_progress': True, 'completed': False})
    
    try:
        # Scroll through the page twice to load more profiles
        for _ in range(2):
            # Wait for the profiles to load
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div[data-chameleon-result-urn]")
                )
            )
            # Scroll to the bottom of the page to load more profiles
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  
            
            # Parse the page source with BeautifulSoup
            soup = BeautifulSoup(driver.page_source, 'lxml')
            profiles = soup.select('div[data-chameleon-result-urn]')
            print(f"Found {len(profiles)} profiles")  # Print the number of profiles found
            
            # Extract data from the profiles
            scroll_extract(driver, profiles)

            # Handle pagination by clicking the "Next" button
            try:
                next_button = WebDriverWait(driver, 40).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Next']"))
                )
                if next_button.is_enabled():
                    next_button.click()
            except Exception as e:
                print(f"Pagination error: {str(e)}")
                break
                
    finally:
        # Update the scraping status to indicate that scraping is complete
        scraping_status.update({'in_progress': False, 'completed': True})
        # Upload the CSV file to Google Drive
        return upload_csv_to_drive(file_path)

def apply_filters2(driver, name, surname, title, keywords, scraping_status):
    """
    Applies search filters on LinkedIn and initiates the scraping process.
    
    Args:
        driver: The Selenium WebDriver instance.
        name: First name filter for the search.
        surname: Last name filter for the search.
        title: Job title filter for the search.
        keywords: Keywords filter for the search.
        scraping_status: A dictionary to track the scraping progress.
    
    Returns:
        The result of the scraping process.
    """
    # Construct the base URL for LinkedIn search with query parameters
    base_url = "https://www.linkedin.com/search/results/people/?"
    query_params = []

    # Add filters to the query parameters
    if name:
        query_params.append(f"firstName={name}")
    if surname:
        query_params.append(f"lastName={surname}")
    if title:
        query_params.append(f"titleFreeText={title.replace(' ', '%20')}")
    if keywords:
        query_params.append(f"keywords={keywords.replace(' ', '%20')}")

    # Add additional parameters for the search
    query_params.append("origin=FACETED_SEARCH")
    query_params.append("sid=n1.")

    # Combine the base URL and query parameters to form the final URL
    final_url = base_url + "&".join(query_params)
    print(final_url)  

    # Navigate to the constructed URL
    driver.get(final_url)
    time.sleep(5)  

    # Start scraping the results page
    return scrape_results_page(driver, scraping_status)