# LinkedIn Scraper Project

This project scrapes LinkedIn and LinkedIn Sales Navigator data using Selenium and Flask. It allows users to apply filters, scrape profile details, and export the data to a Google Sheets document.

## Prerequisites
Before running the project, ensure you have the following installed:

- Python 3.8 or higher
- pip (Python package manager)

## Installation

### Clone the repository:
```bash
git clone https://github.com/yourusername/linkedin-scraper.git
cd linkedin-scraper
```

### Install dependencies:
```bash
pip install -r requirements.txt
```

### Set up environment variables:
Create a `.env` file inside the `database` directory and add the following environment variable:
```plaintext
MONGO_URL="mongodb+srv://lunar_dd:lunar_dd@clustere.hgaxe.mongodb.net/?retryWrite=true&w=majority&appName=Clustere"
```

### Configure `config.json`:
Create a `config.json` file in the root directory with the following content:
```json
{
    "email": "your-email@gmail.com",
    "password": "your-password"
}
```
Replace `your-email@gmail.com` and `your-password` with your LinkedIn credentials.

### Set up Google Service Account:
1. Download the `service-account.json` file from Google Cloud Console.
2. Place the `service-account.json` file in the root directory of the project.

## Running the Project

### Start the Flask application:
```bash
python app.py
```

### Access the application:
Open your web browser and navigate to `http://127.0.0.1:5000/` to access the application.

## Project Structure
```
linkedin-scraper/
│── app.py                 # Main Flask application file
│── config.json            # LinkedIn login credentials
│── service-account.json   # Google Cloud service account credentials
│── .env                   # Environment variables for MongoDB (inside database/)
│── requirements.txt       # List of Python dependencies
│── database/              # Contains MongoDB-related files
│── static/                # Static files (CSS, JS, etc.)
│── templates/             # HTML templates for the Flask application
```

## Usage

### LinkedIn Sales Navigator:
1. Navigate to the Sales Navigator page.
2. Apply filters such as Geography, Industry, and Company Headcount.
3. Click "Apply Filters" to start scraping.

### LinkedIn Search:
1. Navigate to the LinkedIn Search page.
2. Enter search criteria such as Name, Surname, and Keywords.
3. Click "Apply Filters" to start scraping.

### Download Results:
After scraping is completed, download the results as a CSV file or view them in Google Sheets.
