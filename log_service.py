from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import datetime
import os
import logging
from pymongo import MongoClient
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("log_service")

# Load variables from .env file
load_dotenv()

# MongoDB connection details
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.environ.get("MONGO_DB_NAME", "analysis_db")
COLLECTION_NAME = os.environ.get("MONGO_COLLECTION_NAME", "analysis_logs")

# Ensure MongoDB URI has correct protocol
if MONGO_URI and not (MONGO_URI.startswith("mongodb://") or MONGO_URI.startswith("mongodb+srv://")):
    MONGO_URI = f"mongodb://{MONGO_URI}"
    logger.warning(f"Added missing protocol to MongoDB URI: {MONGO_URI}")

# MongoDB collection
collection = None

# Try different addresses for MongoDB connection
def connect_mongodb():
    global collection
    possible_hosts = [
        MONGO_URI,  # Value from .env file (priority)
        "mongodb://mongodb:27017",  # MongoDB container in Docker network
        "mongodb://host.docker.internal:27017",
        "mongodb://localhost:27017",
        "mongodb://127.0.0.1:27017",
        "mongodb://172.17.0.1:27017"
    ]
    
    for uri in possible_hosts:
        try:
            logger.info(f"Trying MongoDB connection: {uri}")
            client = MongoClient(uri, serverSelectionTimeoutMS=3000)  # 3 second timeout
            # Quick connection test
            client.admin.command('ping')
            db = client[DATABASE_NAME]
            collection = db[COLLECTION_NAME]
            logger.info(f"MongoDB connection successful: {uri}")
            
            # If connection is successful and original URI is different, update .env file
            if uri != MONGO_URI:
                logger.info(f"Updating MongoDB URI: {uri}")
                # This process may not be necessary when running in Docker container
                # because the entrypoint script already updates .env
                
            # Exit the loop if connection is successful
            return True
        except Exception as e:
            logger.warning(f"MongoDB connection failed ({uri}): {str(e)}")
            continue
    
    logger.error("All MongoDB connection attempts failed")
    return False

# Try MongoDB connection
connect_mongodb()

app = FastAPI()

class LogData(BaseModel):
    """
    Data model for logging analysis results.
    
    This class defines the structure of the log data that will be stored
    in the MongoDB database, including the timestamp, analyzed text, and
    the sentiment/intent analysis results.
    """
    timestamp: datetime.datetime
    text: str
    analysis: dict

def write_log(log_data: LogData) -> None:
    """
    Write log data to MongoDB database.
    
    This function handles the actual database operation to store
    the log data in MongoDB, with basic error handling.
    
    Args:
        log_data (LogData): The log data to be stored.
    """
    if collection is None:
        logger.warning("MongoDB connection not available, log not saved")
        return
        
    try:
        collection.insert_one(log_data.dict())
        logger.info("Log successfully saved to MongoDB.")
    except Exception as e:
        logger.error(f"Error saving log to MongoDB: {e}")


@app.post("/log")
async def log_endpoint(data: LogData, background_tasks: BackgroundTasks):
    """
    API endpoint for receiving log data.
    
    This endpoint receives log data from the sentiment analysis service
    and processes it asynchronously using background tasks to avoid
    blocking the response.
    
    Args:
        data (LogData): The log data received from the client.
        background_tasks (BackgroundTasks): FastAPI's background task handler.
        
    Returns:
        dict: A confirmation message indicating the log was submitted.
    """
    # Using background task to write log data to MongoDB without blocking
    background_tasks.add_task(write_log, data)
    logger.debug(f"Log submission received for text: {data.text[:50]}...")
    return {"message": "Log submitted successfully"}
