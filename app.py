from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from login import login_to_site
from drive_authenticate import write_results_to_csv, upload_csv_to_drive
import os
import time
import threading
import json
import queue
import re
import time
from urllib.parse import quote

link_queue1 = queue.Queue()
link_queue2 = queue.Queue()
app = Flask(__name__)
app.secret_key = 'supersecretkey'  
SCRAPED_FILE = 'scraped_data.csv'
static_folder = os.path.join(os.path.dirname(__file__), 'static')
print(f"Static folder path: {static_folder}")

os.makedirs(static_folder, exist_ok=True) 
print(f"Static folder created: {os.path.exists(static_folder)}")

file_path = os.path.join(static_folder, 'details_.csv')
print(f"File path: {file_path}")

# Create an empty file to ensure it is created
with open(file_path, 'w') as f:
    f.write('')

print(f"File created: {os.path.exists(file_path)}")
# Load config
with open("C:\\Users\\mayan\\OneDrive\\Desktop\\Linkedin_Scraped\\config.json", 'r') as config_file:
    config = json.load(config_file)

# Thread-safe status tracker
scraping_status = {'in_progress': False}
scraping_status['completed'] = False

google_sheets_link = None
# file_path = None


def get_lk_url_from_sales_lk_url1(url):
    parsed = re.search(r"/lead/(.*?),", url, re.IGNORECASE)
    return f"https://www.linkedin.com/in/{parsed.group(1)}" if parsed else None


def scroll_extract(driver, items):
    """Extracts person details from the given items on the page."""
    results = []
    for index, item in enumerate(items):
        # initialize variables
        person_name = "NA"
        person_title = "NA"
        person_company = "NA"
        person_location = "NA"
        person_link = "NA"
        linkedin_url = "NA"
        
        try:
            # Scroll the item into view using JavaScript
            driver.execute_script("arguments[0].scrollIntoView(true);", item)
            print(f"Scrolled to item {index + 1}")
            # wait till visible
            WebDriverWait(driver, 10).until(EC.visibility_of(item))

            item = driver.find_elements(By.CSS_SELECTOR, "li.artdeco-list__item.pl3.pv3")[index]

            # Extract person's name safely
            name_element = item.find_element(By.CSS_SELECTOR, "span[data-anonymize='person-name']")
            person_name = name_element.text if name_element else "NA"

            link_element = name_element.find_element(By.XPATH, "..")
            person_link = link_element.get_attribute('href') if link_element else "NA"
            print(f'the person link is {person_link}')
            
            # Extract LinkedIn URL from Sales Navigator URL
            linkedin_url = get_lk_url_from_sales_lk_url1(person_link)
             
            
            # Extract person's title safely
            title_element = item.find_element(By.CSS_SELECTOR, "span[data-anonymize='title']")
            person_title = title_element.text if title_element else "NA"

            # Extract company name safely
            company_element = item.find_element(By.CSS_SELECTOR, "a[data-anonymize='company-name']")
            person_company = company_element.text if company_element else "NA"

            # Extract location safely
            location_element = item.find_element(By.CSS_SELECTOR, "span[data-anonymize='location']")
            person_location = location_element.text if location_element else "NA"

            # Append results
            results.append({
                'person_name': person_name,
                'person_title': person_title,
                'person_company': person_company,
                'person_location': person_location,
                'person_link': person_link,
                'linkedin_url': linkedin_url,
            })

            # Wait for 1 second to allow any dynamic content to load
            time.sleep(1)
        except Exception as e:
            print(f"Failed to process item at index {index}: {str(e)}")
            # Append NA values if an error occurred
            results.append({
                'person_name': person_name,
                'person_title': person_title,
                'person_company': person_company,  # Default NA for company as the error occurred here
                'person_location': person_location,
                'person_link': person_link,
                'linkedin_url': linkedin_url,
            })

   
    
    return write_results_to_csv(results, file_path)

def scrape_results_page(driver):
    """Scrapes data from multiple pages of LinkedIn Sales Navigator."""
    scraping_status['in_progress'] = True

    for i in range(1):  # Loop through all pages
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".artdeco-list__item.pl3.pv3")))
            time.sleep(6)

            # Find elements on the page
            li_elements_no_soup = driver.find_elements(By.CSS_SELECTOR, "li.artdeco-list__item.pl3.pv3")
            # Scroll and extract information from the current page
            scroll_extract(driver, li_elements_no_soup)

            # Try to find the 'Next' button; if it's there and clickable, click it
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

    # Update scraping status

    link=upload_csv_to_drive(file_path)
    scraping_status['in_progress'] = False
    scraping_status['completed'] = True
    return link

def apply_filters(driver, changed_jobs, posted_on_linkedin, selected_Industry, Keywords, Company_headcount):
    """Applies filters using the Selenium driver."""
    filters = []
    Industry_IDS = {
    "Sales": "25",
    "Marketing": "15",
    "Engineering": "8",
}
    # Add filters based on user input
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
        # Map the Company_headcount values to their corresponding LinkedIn filter IDs and text
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
        
        # Create a list of selected headcount filters
        headcount_filters = []
        for headcount in Company_headcount:
            if headcount in headcount_mapping:
                id, text = headcount_mapping[headcount]
                headcount_filters.append(f"(id%3A{id}%2Ctext%3A{text.replace(' ', '%20')}%2CselectionType%3AINCLUDED)")
        
        # Add the COMPANY_HEADCOUNT filter if any headcount ranges are selected
        if headcount_filters:
            filters.append(
                f"(type%3ACOMPANY_HEADCOUNT%2Cvalues%3AList({','.join(headcount_filters)}))"
            )
    
    base_url = "https://www.linkedin.com/sales/search/people?query=("
    
    # Add the recentSearchParam
    recent_search_param = "recentSearchParam%3A(id%3A4379678420%2CdoLogHistory%3Atrue)"
    
    # Add keywords if provided
    keywords_param = f",keywords%3A{Keywords.replace(' ', '%20')}" if Keywords else ""
    
    # Add filters if any
    filter_section = f",filters%3AList({','.join(filters)})" if filters else ""
    
    # Construct the final URL
    final_url = f"{base_url}{recent_search_param}{keywords_param}{filter_section})&viewAllFilters=true"
    
    # Navigate to the final URL
    # final_url = "https://www.linkedin.com/sales/search/people?query=(spellCorrectionEnabled%3Atrue%2CrecentSearchParam%3A(id%3A3479457505%2CdoLogHistory%3Atrue)%2Cfilters%3AList((type%3ACURRENT_TITLE%2Cvalues%3AList((text%3AProduct%2520Marketing%2520Leader%2CselectionType%3AINCLUDED))))%2Ckeywords%3AGen%2520AI)&sessionId=m0yyfnqYSL%2By5ONrJMITrw%3D%3D"
    driver.get(final_url)
    time.sleep(5) 
    
    return scrape_results_page(driver)


def apply_filters_account(driver, Keywords, Company_headcount, HeadquarterLocation):
    """Applies filters for company search using the Selenium driver."""
    filters = []
    print(f"HeadquarterLocation input: {HeadquarterLocation}")  # Debugging

  
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
    if Company_headcount:
        for headcount in Company_headcount:
            if headcount in headcount_mapping:
                id, text = headcount_mapping[headcount]
                headcount_filters.append(f"(id%3A{id}%2Ctext%3A{quote(text)}%2CselectionType%3AINCLUDED)")
        
        if headcount_filters:
            filters.append(f"(type%3ACOMPANY_HEADCOUNT%2Cvalues%3AList({','.join(headcount_filters)}))")

    
    location_mapping = {
        "EMEA": ("91000007", "EMEA"),
        "North America": ("102221843", "North America"),
        "Asia": ("102393603", "Asia")
    }

    location_filters = []

    
    if isinstance(HeadquarterLocation, str):  
        HeadquarterLocation = [HeadquarterLocation]  

    if HeadquarterLocation:
        for location in HeadquarterLocation:
            if location in location_mapping:
                id, text = location_mapping[location]
                location_filters.append(f"(id%3A{id}%2Ctext%3A{quote(text)}%2CselectionType%3AINCLUDED)")

    print(f"location_filters: {location_filters}")  # Debugging

    if location_filters:
        filters.append(f"(type%3AREGION%2Cvalues%3AList({','.join(location_filters)}))")

    print(f"filters: {filters}")  # Debugging

    base_url = "https://www.linkedin.com/sales/search/company?query=("

    # Add spell correction and filters
    spell_correction = "spellCorrectionEnabled%3Atrue"
    filter_section = f",filters%3AList({','.join(filters)})" if filters else ""

    
    keywords_param = f",keywords%3A{quote(Keywords)}" if Keywords else ""

     
    final_url = f"{base_url}{spell_correction}{filter_section}{keywords_param})&viewAllFilters=true"
    print(f"Final URL: {final_url}")  # Debugging

  
    driver.get(final_url)
    time.sleep(5)  # Simulate browsing
    
    return scrape_results_page(driver)



@app.route('/')
def index():
    return render_template('demo.html')

@app.route('/Lead', methods=['POST'])
def lead():
    return render_template('lead.html')

@app.route('/Account', methods=['POST'])
def account():
    return render_template('account.html')

@app.route('/apply-filters', methods=['POST'])
def apply_filters_route():
    """Route to handle filter application."""
    changed_jobs = 'changedJobs' in request.form
    posted_on_linkedin = 'postedOnLinkedIn' in request.form
    selected_industry = request.form.get('INDUSTRY')
    Company_headcount = request.form.getlist('Company_headcount')
    Keywords = request.form.get('keywords')

    def background_task(changed_jobs, posted_on_linkedin, selected_industry, Keywords, Company_headcount):
        driver = login_to_site()
        link = apply_filters(driver, changed_jobs, posted_on_linkedin, selected_industry, Keywords, Company_headcount)
        link_queue1.put(link)  # Put the link into the queue
        scraping_status['completed'] = True

    thread = threading.Thread(
        target=background_task,
        args=(changed_jobs, posted_on_linkedin, selected_industry, Keywords, Company_headcount)
    )
    thread.daemon = True
    thread.start()

    scraping_status['in_progress'] = True
    return render_template('status.html')


@app.route('/apply-filters2', methods=['POST'])
def apply_filters_account_route():
    """Route to handle filter application."""
    
    HeadquarterLocation= request.form.get('HeadquarterLocation')
    Company_headcount = request.form.getlist('Company_headcount')
    Keywords = request.form.get('keywords')

    def background_task(Keywords, Company_headcount,HeadquarterLocation):
        driver = login_to_site()
        link = apply_filters_account(driver,Keywords, Company_headcount,HeadquarterLocation)
        link_queue2.put(link)  # Put the link into the queue
        scraping_status['completed'] = True

    thread = threading.Thread(
        target=background_task,
        args=(Keywords, Company_headcount,HeadquarterLocation)
    )
    thread.daemon = True
    thread.start()

    scraping_status['in_progress'] = True
    return render_template('status.html')

@app.route('/get-link', methods=['GET'])
def get_link():
    """Retrieve the Google Sheets link from the queue and store it in the session."""
    try:
        google_sheets_link = link_queue1.get(timeout=10)  # Wait for the link to be available
        session['google_sheets_link'] = google_sheets_link
        session.modified = True  # Ensure the session is saved
        return jsonify({"status": "success", "link": google_sheets_link})
    except queue.Empty:
        return jsonify({"status": "error", "message": "Link not available yet"}), 404

@app.route('/check-status', methods=['GET'])
def check_status():
    return jsonify(scraping_status)

@app.route('/download')
def download():
    """Serves the download page after scraping is completed."""
    google_sheets_link = session.get('google_sheets_link', None)
    if google_sheets_link:
        return render_template('download.html', google_sheets_link=google_sheets_link)
    else:
        return "Scraping is not yet completed or no link available."

if __name__ == '__main__':
    app.run(debug=True)