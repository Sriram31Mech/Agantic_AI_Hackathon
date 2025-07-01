import os
from pymongo import MongoClient, errors
from dotenv import load_dotenv
from pathlib import Path

# Load .env with explicit path for reliability
dotenv_path = Path(__file__).parent / ".env" # Adjust path to find .env at project root
load_dotenv(dotenv_path)
print(f"🔍 Looking for .env at: {dotenv_path}")

# Read environment variables
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("MONGO_DB_NAME")

# Define collection names (can be configured in .env or hardcoded if consistent)
OKR_COLLECTION_NAME = "micro_tasks"
TASK_COLLECTION_NAME = "tasks"
REMINDER_COLLECTION_NAME = "reminders"

# Debug: Print loaded environment variables
print(f"🧪 MONGO_URI: {MONGO_URI}")
print(f"🧪 DB_NAME: {DB_NAME}")
print(f"🧪 OKR_COLLECTION_NAME: {OKR_COLLECTION_NAME}")
print(f"🧪 TASK_COLLECTION_NAME: {TASK_COLLECTION_NAME}")
print(f"🧪 REMINDER_COLLECTION_NAME: {REMINDER_COLLECTION_NAME}")

# Validate environment variable presence
if not MONGO_URI:
    raise RuntimeError("❌ MONGO_URI not found in .env file!")
if not DB_NAME:
    raise RuntimeError("❌ MONGO_DB_NAME not found in .env file!")

# Try connecting to MongoDB
try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
    client.admin.command('ping')  # Test connection
    print("✅ Successfully connected to MongoDB!")
except errors.ServerSelectionTimeoutError as err:
    print("❌ Could not connect to MongoDB:", err)
    exit(1)

# Access DB and Collections
try:
    db = client[DB_NAME]
    okr_collection = db[OKR_COLLECTION_NAME]
    task_collection = db[TASK_COLLECTION_NAME]
    reminder_collection = db[REMINDER_COLLECTION_NAME]
    print(f"✅ Connected to database: {DB_NAME}, collections: {OKR_COLLECTION_NAME}, {TASK_COLLECTION_NAME}, {REMINDER_COLLECTION_NAME}")
except Exception as e:
    print(f"❌ Error accessing DB or Collections: {e}")
    exit(1)
