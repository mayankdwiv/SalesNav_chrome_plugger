import time
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import csv
def authenticate_drive():
    """Authenticate with Google Drive API."""
    SCOPES = ["https://www.googleapis.com/auth/drive.file"]
    SERVICE_ACCOUNT_FILE = "service-account.json"
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return build("drive", "v3", credentials=creds)

def upload_csv_to_drive(csv_filename):
    """Uploads CSV file to Google Drive and returns shareable link."""
    service = authenticate_drive()

   
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    unique_filename = f"{csv_filename.split('.')[0]}_{timestamp}.csv"

    file_metadata = {
        "name": unique_filename,
        "mimeType": "application/vnd.google-apps.spreadsheet"
    }
    
    media = MediaFileUpload(csv_filename, mimetype="text/csv")

    file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()
    file_id = file.get("id")
    
    service.permissions().create(
        fileId=file_id,
        body={"role": "writer", "type": "anyone"},
    ).execute()

    shareable_link = f"https://docs.google.com/spreadsheets/d/{file_id}"
    # print(f"Uploaded CSV to Google Drive: {shareable_link}")
    
    return shareable_link

def write_results_to_csv(results, filename):
    """Appends scraped data to a CSV file."""
    with open(filename, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
   
        if file.tell() == 0:
            writer.writerow(['person_name', 'person_title', 'person_company', 'person_location', 'person_link', 'linkedin_url'])

        for result in results:
            writer.writerow([result['person_name'], result['person_title'], result['person_company'], result['person_location'], result['person_link'], result['linkedin_url']])
    return 