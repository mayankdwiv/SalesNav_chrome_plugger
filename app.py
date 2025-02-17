from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from login import login_to_site, load_cookies_and_open, login
from drive_authenticate import write_results_to_csv, upload_csv_to_drive
from Database.mongo_db import save_search1, save_search2, get_recent_searches
from func import apply_filters2
import os
import time
import threading
import json
import queue
import re
from urllib.parse import quote
from bs4 import BeautifulSoup

# Queue to store the generated Google Sheets links
link_queue = queue.Queue()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Secret key for session management

# Path for the static folder and CSV file
SCRAPED_FILE = 'scraped_data.csv'
static_folder = os.path.join(os.path.dirname(__file__), 'static')
os.makedirs(static_folder, exist_ok=True)  # Create static folder if it doesn't exist
file_path = os.path.join(static_folder, 'details_.csv')

# Create an empty CSV file to store scraped data
with open(file_path, 'w') as f:
    f.write('')

# Load configuration from JSON file
with open("C:\\Users\\mayan\\OneDrive\\Desktop\\Linkedin_Scraped\\config.json", 'r') as config_file:
    config = json.load(config_file)

# Global variable to track scraping status
scraping_status = {'in_progress': False, 'completed': False}

# Function to extract LinkedIn profile URL from Sales Navigator URL
def get_lk_url_from_sales_lk_url1(url):
    parsed = re.search(r"/lead/(.*?),", url, re.IGNORECASE)
    return f"https://www.linkedin.com/in/{parsed.group(1)}" if parsed else None

# Function to extract person details from the page using Selenium
def scroll_extract(driver, items):
    """Extracts person details from the given items on the page."""
    results = []
    for index, item in enumerate(items):
        # Initialize default values for person details
        person_name = "NA"
        person_title = "NA"
        person_company = "NA"
        person_location = "NA"
        person_link = "NA"
        linkedin_url = "NA"
        
        try:
            # Scroll the item into view and wait for it to be visible
            driver.execute_script("arguments[0].scrollIntoView(true);", item)
            WebDriverWait(driver, 10).until(EC.visibility_of(item))

            # Extract person details using Selenium
            name_element = item.find_element(By.CSS_SELECTOR, "span[data-anonymize='person-name']")
            person_name = name_element.text if name_element else "NA"

            link_element = name_element.find_element(By.XPATH, "..")
            person_link = link_element.get_attribute('href') if link_element else "NA"
            linkedin_url = get_lk_url_from_sales_lk_url1(person_link)

            title_element = item.find_element(By.CSS_SELECTOR, "span[data-anonymize='title']")
            person_title = title_element.text if title_element else "NA"

            company_element = item.find_element(By.CSS_SELECTOR, "a[data-anonymize='company-name']")
            person_company = company_element.text if company_element else "NA"

            location_element = item.find_element(By.CSS_SELECTOR, "span[data-anonymize='location']")
            person_location = location_element.text if location_element else "NA"

            # Append extracted details to results
            results.append({
                'person_name': person_name,
                'person_title': person_title,
                'person_company': person_company,
                'person_location': person_location,
                'person_link': person_link,
                'linkedin_url': linkedin_url,
            })

            time.sleep(1)  # Sleep to avoid overloading the page
        except Exception as e:
            print(f"Failed to process item at index {index}: {str(e)}")
            # Append default values if extraction fails
            results.append({
                'person_name': person_name,
                'person_title': person_title,
                'person_company': person_company,  
                'person_location': person_location,
                'person_link': person_link,
                'linkedin_url': linkedin_url,
            })

    # Write results to CSV and return the file path
    return write_results_to_csv(results, file_path)

# Function to scrape data from multiple pages of LinkedIn Sales Navigator
def scrape_results_page(driver):
    """Scrapes data from multiple pages of LinkedIn Sales Navigator."""
    scraping_status['in_progress'] = True

    for i in range(1):  # Adjust the range for the number of pages to scrape
        try:
            # Wait for the initial content to load
            WebDriverWait(driver, 30).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, ".artdeco-list__item.pl3.pv3")))
            time.sleep(5)

            # Find all profile items on the page
            li_elements_no_soup = driver.find_elements(By.CSS_SELECTOR, "li.artdeco-list__item.pl3.pv3")
            for index, item in enumerate(li_elements_no_soup):
                try:
                    # Scroll each item into view
                    driver.execute_script("arguments[0].scrollIntoView(true);", item)
                except Exception as e:
                    print(f"Failed to scroll to item {index + 1}: {str(e)}")

            # Extract details from the current page
            li_elements_no_soup = driver.find_elements(By.CSS_SELECTOR, "li.artdeco-list__item.pl3.pv3")
            scroll_extract(driver, li_elements_no_soup)

            # Navigate to the next page
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, "button.artdeco-pagination__button--next")
                if next_button.is_enabled():
                    next_button.click()
                    print("Navigated to next page")
                else:
                    print("Next button not enabled, last page reached.")
                    break
            except NoSuchElementException:
                print("No more pages to navigate.")
                break
            except Exception as e:
                print(f"Error navigating to next page: {str(e)}")
                break
        except Exception as e:
            print(f"Error scraping page {i+1}: {str(e)}")
            break

    # Upload the CSV file to Google Drive and return the link
    link = upload_csv_to_drive(file_path)
    scraping_status['in_progress'] = False
    scraping_status['completed'] = True
    return link

# Function to apply filters on LinkedIn Sales Navigator
def apply_filters1(driver, Geography, changed_jobs, posted_on_linkedin, selected_Industry, Keywords, Company_headcount):
    """Applies filters using the Selenium driver."""
    filters = []
    Industry_IDS = {
        "Sales": "25",
        "Marketing": "15",
        "Engineering": "8",
        "Information Technology": "13",
        "Business Development": "4",
    }

    # Geography mapping to LinkedIn Sales Navigator filter IDs
    Geography_IDS = {
        "North America": "102221843",
        "Asia": "102393603",
        "EMEA": "91000007",
        "India": "102713980",
        "Europe": "100506914",
        "Africa": "103537801",
        "South America": "104514572",
    }

    # Add Geography filter if any regions are selected
    if Geography:
        geography_filters = []
        for region in Geography:
            if region in Geography_IDS:
                region_id = Geography_IDS[region]
                geography_filters.append(f"(id%3A{region_id}%2Ctext%3A{region.replace(' ', '%20')}%2CselectionType%3AINCLUDED)")
        
        if geography_filters:
            filters.append(
                f"(type%3AREGION%2Cvalues%3AList({','.join(geography_filters)}))"
            )

    # Add other filters
    if changed_jobs:
        filters.append(
            "(type%3ARECENTLY_CHANGED_JOBS%2Cvalues%3AList((id%3ARPC%2Ctext%3AChanged%2520jobs%2CselectionType%3AINCLUDED)))"
        )
    if posted_on_linkedin:
        filters.append(
            "(type%3APOSTED_ON_LINKEDIN%2Cvalues%3AList((id%3ARPOL%2Ctext%3APosted%2520on%2520LinkedIn%2CselectionType%3AINCLUDED)))"
        )
    if selected_Industry:
        Industry_id = Industry_IDS.get(selected_Industry)
        if Industry_id:
            filters.append(
                f"(type%3AFUNCTION%2Cvalues%3AList((id%3A{Industry_id}%2Ctext%3A{selected_Industry.replace(' ', '%20')}%2CselectionType%3AINCLUDED)))"
            )
    if Company_headcount:
        headcount_mapping = {
            "1-10": ("B", "1-10"),
            "11-50": ("C", "11-50"),
            "51-200": ("D", "51-200"),
            "201-500": ("E", "201-500"),
            "501-1000": ("F", "501-1,000"),
            "1001-5000": ("G", "1,001-5,000"),
            "5001-10000": ("H", "5,001-10,000"),
            "10000+": ("I", "10,001+")
        }
        
        headcount_filters = []
        for headcount in Company_headcount:
            if headcount in headcount_mapping:
                id, text = headcount_mapping[headcount]
                headcount_filters.append(f"(id%3A{id}%2Ctext%3A{text.replace(' ', '%20')}%2CselectionType%3AINCLUDED)")
        
        if headcount_filters:
            filters.append(
                f"(type%3ACOMPANY_HEADCOUNT%2Cvalues%3AList({','.join(headcount_filters)}))"
            )
    
    # Base URL for LinkedIn Sales Navigator
    base_url = "https://www.linkedin.com/sales/search/people?query=("
    
    # Recent search parameter
    recent_search_param = "recentSearchParam%3A(id%3A4379678420%2CdoLogHistory%3Atrue)"
    
    # Keywords parameter
    keywords_param = f",keywords%3A{Keywords.replace(' ', '%20')}" if Keywords else ""
    
    # Filters section
    filter_section = f",filters%3AList({','.join(filters)})" if filters else ""
    
    # Construct the final URL
    final_url = f"{base_url}{recent_search_param}{keywords_param}{filter_section})&viewAllFilters=true"
    print(final_url)
    
    # Navigate to the final URL
    driver.get(final_url)
    time.sleep(5)  # Wait for the page to load
    
    return scrape_results_page(driver)

# Flask routes
@app.route('/')
def index():
    """Render the home page."""
    return render_template('demo.html')

@app.route('/Sales_Navigator', methods=['POST'])
def lead():
    """Render the Sales Navigator page."""
    return render_template('Sales_Navigator.html')

@app.route('/linkedin', methods=['POST'])
def account():
    """Render the LinkedIn page."""
    return render_template('linkedin.html')

@app.route('/apply-filters1', methods=['POST'])
def apply_filters_route1():
    """Route to handle filter application for Sales Navigator."""
    changed_jobs = 'changedJobs' in request.form
    posted_on_linkedin = 'postedOnLinkedIn' in request.form
    selected_industry = request.form.get('INDUSTRY')
    Company_headcount = request.form.getlist('Company_headcount')
    Keywords = request.form.get('keywords')
    Geography = request.form.getlist('Geography')

    def background_task(Geography, changed_jobs, posted_on_linkedin, selected_industry, Keywords, Company_headcount):
        """Background task to apply filters and scrape data."""
        driver = login()
        link = apply_filters1(driver, Geography, changed_jobs, posted_on_linkedin, selected_industry, Keywords, Company_headcount)
        if link:
            link_queue.put(link)  # Put the link into the queue
            save_search1("Sales-Navigator", Keywords, selected_industry, Company_headcount, link, Geography)
        else:
            print("No link generated. Scraping may have failed.") 
        scraping_status['completed'] = True

    # Start the background task in a new thread
    thread = threading.Thread(
        target=background_task,
        args=(Geography, changed_jobs, posted_on_linkedin, selected_industry, Keywords, Company_headcount)
    )
    thread.daemon = True
    thread.start()
    
    scraping_status['in_progress'] = True
    return render_template('status.html')

@app.route('/apply-filters2', methods=['POST'])
def apply_filters_route2():
    """Route to handle filter application for LinkedIn."""
    name = request.form.get('name')
    surname = request.form.get('surname')
    Keywords = request.form.get('keywords')
    title = request.form.get('title')

    def background_task(name, surname, title, Keywords):
        """Background task to apply filters and scrape data."""
        driver = login()
        link = apply_filters2(driver, name, surname, title, Keywords, scraping_status)
        if link:
            link_queue.put(link)  # Put the link into the queue
            save_search2("Linkedin", Keywords, title, name, link)
        else:
            print("No link generated. Scraping may have failed.") 
        scraping_status['completed'] = True

    # Start the background task in a new thread
    thread = threading.Thread(
        target=background_task,
        args=(name, surname, title, Keywords)
    )
    thread.daemon = True
    thread.start()
    
    scraping_status['in_progress'] = True
    return render_template('status.html')

@app.route('/recent-searches', methods=['GET'])
def recent_searches():
    """Fetch the last 5 searches from MongoDB."""
    searches = get_recent_searches()
    return jsonify(searches)

@app.route('/get-link', methods=['GET'])
def get_link():
    """Retrieve the Google Sheets link from the queue and store it in the session."""
    try:
        google_sheets_link = link_queue.get(timeout=10)  
        session['google_sheets_link'] = google_sheets_link
        session.modified = True 
        return jsonify({"status": "success", "link": google_sheets_link})
    except queue.Empty:
        return jsonify({"status": "error", "message": "Link not available yet"}), 404

@app.route('/check-status', methods=['GET'])
def check_status():
    """Check the current scraping status."""
    return jsonify(scraping_status)

@app.route('/download')
def download():
    """Serve the download page after scraping is completed."""
    google_sheets_link = session.get('google_sheets_link', None)
    if google_sheets_link:
        return render_template('download.html', google_sheets_link=google_sheets_link)
    else:
        return "Scraping is not yet completed or no link available."

if __name__ == '__main__':
    app.run(debug=True)