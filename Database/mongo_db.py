from datetime import datetime, timedelta
from pymongo import MongoClient
import os

# MongoDB connection
mongo_uri = os.getenv("MONGO_URI")  # Your MongoDB Atlas connection string
client = MongoClient(mongo_uri)
db = client['search_history']
searches_collection = db['searches']

def time_ago(timestamp):
    """Convert timestamp to a human-friendly 'time ago' format."""
    now = datetime.now()
    diff = now - timestamp

    if diff < timedelta(minutes=1):
        return "Just now"
    elif diff < timedelta(hours=1):
        return f"{diff.seconds // 60} minutes ago"
    elif diff < timedelta(days=1):
        return f"{diff.seconds // 3600} hours ago"
    elif diff < timedelta(days=7):
        return f"{diff.days} days ago"
    else:
        return timestamp.strftime("%Y-%m-%d")  # Show date for older entries

def save_search1(section, keywords, industry, company_headcount, link,Geography):
    """Save a search entry to MongoDB."""
    search_entry = {
        "keywords": keywords,
        "industry": industry,
        "company_headcount": company_headcount,
        "link": link,
        "timestamp": datetime.now(),
        "section": section,
        "Geography": Geography

    }
    inserted_id = searches_collection.insert_one(search_entry).inserted_id
    print(f"Search saved with ID {inserted_id}")

def save_search2(section, Keywords,title,name, link):
    """Save a search entry to MongoDB."""
    search_entry = {
        "keywords": Keywords,
        "title": title,
        "name": name,
        "link": link,
        "timestamp": datetime.now(),
        "section": section
    }
    inserted_id = searches_collection.insert_one(search_entry).inserted_id
    print(f"Search saved with ID {inserted_id}")

def get_recent_searches(section=None, limit=5):
    """Fetch the most recent searches from MongoDB based on the section."""
    searches = searches_collection.find().sort("timestamp", -1).limit(limit)
    search_list = []

    for search in searches:
        if search["section"] == "Sales-Navigator":
            search_entry = {
                "keywords": search["keywords"],
                "industry": search.get("industry", None),
                "company_headcount": search.get("company_headcount", None),
                "link": search["link"],
                "timestamp": time_ago(search["timestamp"]),
                "section": search.get("section"),
                "Geography": search.get("Geography", None)
            }
        else:
            search_entry = {
                "keywords": search["keywords"],
                "title": search.get("title", None),
                "name": search.get("name", None),
                "link": search["link"],
                "timestamp": time_ago(search["timestamp"]),
                "section": search.get("section")
            }
       

        search_list.append(search_entry)

    return search_list
