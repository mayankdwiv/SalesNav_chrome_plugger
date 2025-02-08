# mongo_db.py
from pymongo import MongoClient
import os
from pymongo.errors import ConnectionFailure, OperationFailure

# MongoDB connection
mongo_uri = os.getenv("MONGO_URI")  # Your MongoDB Atlas connection string

try:
    # Attempt to connect to MongoDB
    client = MongoClient(mongo_uri)
    
    # Verify the connection
    client.admin.command('ping')
    print("Successfully connected to MongoDB!")
    
    # Access the database and collection
    db = client['search_history']
    searches_collection = db['searches']
    
    # Data to be inserted
    data = {
        "keywords": "Python",
        "industry": "Software",
        "company_headcount": "100-500",
        "link": "https://www.linkedin.com/jobs/search/?keywords=Python&location=Worldwide",
    }
    
    # Attempt to insert data
    try:
        store_id = searches_collection.insert_one(data).inserted_id
        print(f"Data inserted with ID: {store_id}")
    except OperationFailure as e:
        print(f"Failed to insert data: {e}")
    
except ConnectionFailure as e:
    print(f"Failed to connect to MongoDB: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
finally:
    # Ensure the client is closed properly
    if 'client' in locals():
        client.close()
        print("MongoDB connection closed.")