import os
import pymongo
import logging
from config import Config

logger = logging.getLogger(__name__)

# Initialize MongoDB connection
mongo_db = None

def setup_mongo():
    """Setup MongoDB connection"""
    global mongo_db
    
    try:
        # Connect to MongoDB
        client = pymongo.MongoClient(Config.MONGO_URI)
        
        # Check connection
        client.admin.command('ping')
        
        # Get database name from connection string
        db_name = Config.MONGO_URI.split('/')[-1]
        
        # Set database
        mongo_db = client[db_name]
        
        logger.info(f"Connected to MongoDB: {db_name}")
        
        # Ensure text indexes exist for search
        if "name_text" not in mongo_db.recipes.index_information():
            mongo_db.recipes.create_index([
                ("name", "text"), 
                ("description", "text"),
                ("ingredients.name", "text")
            ])
            logger.info("Created text indexes for recipe search")
            
        return mongo_db
    except Exception as e:
        logger.error(f"MongoDB connection error: {e}")
        raise
