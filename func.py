from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from drive_authenticate import write_results_to_csv1, upload_csv_to_drive
import os
import time
from urllib.parse import quote
from bs4 import BeautifulSoup

import time
static_folder = os.path.join(os.path.dirname(__file__), 'static')
file_path = os.path.join(static_folder, 'details_.csv')

def scroll_extract(driver, items):
    results = []
    
    for item in items:
        try:
            # Name extraction
            name = item.select_one('span.t-16').get_text(strip=True)

            
            # Profile link
            profile_link = item.select_one('a[data-test-app-aware-link]')['href']
            if profile_link.startswith('/'):
                profile_link = f"https://www.linkedin.com{profile_link}"
            
            # Current role (using multiple class identifiers)
            current_role = item.select_one('div.t-14.t-black.t-normal').get_text(strip=True)
            
            # Location (using multiple class identifiers)
            location = item.select_one('div.t-14.t-normal:last-child').get_text(strip=True)
            # print(f"Extracted: {name}, {current_role}, {location}, {profile_link}")
            results.append({
                'Name': name,
                'Current Role': current_role,
                'Location': location,
                'Profile Link': profile_link
            })
            
        except Exception as e:
            print(f"Error processing item: {str(e)}")
            continue
    
    return write_results_to_csv1(results, file_path)

def scrape_results_page(driver, scraping_status):
    """Scrapes data with proper element selection"""
    scraping_status.update({'in_progress': True, 'completed': False})
    
    try:
        for _ in range(2):
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div[data-chameleon-result-urn]")
                )
            )
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  
            # time.sleep(10)  # Wait for the page to load
            soup = BeautifulSoup(driver.page_source, 'lxml')
            profiles = soup.select('div[data-chameleon-result-urn]')
            print(f"Found {len(profiles)} profiles")  # Will now show actual count
            scroll_extract(driver, profiles)

            # Pagination with improved selector
            try:
                next_button = WebDriverWait(driver, 40).until(
    EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Next']"))
)
                if next_button.is_enabled():
                    next_button.click()
                    # time.sleep(5)
            except Exception as e:
                print(f"Pagination error: {str(e)}")
                break
                
    finally:
        scraping_status.update({'in_progress': False, 'completed': True})
        return upload_csv_to_drive(file_path)

def apply_filters2(driver, name, surname, title, keywords,scraping_status):
  
    base_url = "https://www.linkedin.com/search/results/people/?"

    query_params = []

    if name:
        query_params.append(f"firstName={name}")
    if surname:
        query_params.append(f"lastName={surname}")
    if title:
        query_params.append(f"titleFreeText={title.replace(' ', '%20')}")
    if keywords:
        query_params.append(f"keywords={keywords.replace(' ', '%20')}")

    query_params.append("origin=FACETED_SEARCH")
    query_params.append("sid=n1.")

    final_url = base_url + "&".join(query_params)
    print(final_url)  

    driver.get(final_url)
    time.sleep(5)  

    
    return scrape_results_page(driver,scraping_status)

