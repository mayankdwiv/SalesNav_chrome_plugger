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

def save_search(section, keywords, industry, company_headcount, link,Geography):
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

def get_recent_searches(limit=5):
    """Fetch the most recent searches from MongoDB."""
    searches = searches_collection.find().sort("timestamp", -1).limit(limit)
    search_list = []
    for search in searches:
        search_list.append({
            "keywords": search["keywords"],
            "industry": search["industry"],
            "company_headcount": search["company_headcount"],
            "link": search["link"],
            "timestamp": time_ago(search["timestamp"]),
            "section": search.get("section", "Leads"),
            "Geography": search.get("Geography", None)
        })
    
    return search_list
