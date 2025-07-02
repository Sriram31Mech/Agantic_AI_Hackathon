import sys
import os

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from datetime import date
from pymongo import MongoClient
from dotenv import load_dotenv
from storage import IStorage
from typing import List
from shared.schemas import OkrWithTasks
from bson import ObjectId


# Dependency to get storage instance
def get_storage() -> IStorage:
    # Return a dummy storage or adapt if a real storage implementation is needed
    # For now, as the direct MongoDB collection is used elsewhere, this might not be fully utilized
    raise NotImplementedError("Storage implementation not provided as per new plan. Direct MongoDB access is used.")

sys.path.append(os.path.dirname(__file__))  # Ensure mongo_client is in the path
from mongo_clients import okr_collection

# --- Logging Setup ---
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Load Environment Variables ---
load_dotenv()

# Add backend folder to path
sys.path.append(r'D:\Agantic_AI_Hackathon\Hackathon\AI')

# DEBUG: Import check
logger.info("✅ Imported sys.path and added backend")
try:
    from agents.okr_parser import parse_okr
    from agents.micro_okr import create_micro_tasks
    logger.info("✅ Successfully imported okr_parser and micro_okr")
except Exception as e:
    logger.info("❌ Error importing backend modules:", e)
    raise e

from fastapi.middleware.cors import CORSMiddleware  # 👈 Import CORS middleware

from routes.task_routes import task_router
from routes.reminder_routes import reminder_router
from routes.dashboard_routes import dashboard_router
from routes.okr_routes import okr_router

app = FastAPI(
    title="OKR Management AI Backend",
    description="AI-powered backend for managing OKRs, tasks, and reminders.",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(okr_router, prefix="/api")
app.include_router(task_router, prefix="/api")
app.include_router(reminder_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Welcome to the OKR Management AI Backend!"}

# --- Request and Response Models ---
class OKRInput(BaseModel):
    title: str = Field(..., min_length=1, example="Publish AI Articles")
    description: str = Field(..., min_length=10, example="I want to publish 3 AI articles this quarter.")
    targetDate: date = Field(..., example="2025-07-10T00:00:00.000Z")

class MicroTask(BaseModel):
    task: str
    due: str
    evidence_hint: str
    level: str
    micro_status: str = "pending"

class OKRResponse(BaseModel):
    parsed: dict
    micro_tasks: list[MicroTask]

# --- Endpoint to Process OKRs ---
@app.post("/api/process_okr", response_model=OKRResponse)
def process_okr(input_data: OKRInput):
    deadline = input_data.targetDate
    okr_input = f"{input_data.description} by {deadline}"

    try:
        parsed = parse_okr(okr_input)
        parsed["key_results"] = parsed.get("deliverables", [])
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parsing OKR: {e}")

    try:
        micro_tasks = create_micro_tasks(parsed, deadline=str(deadline))
        if not micro_tasks:
            raise HTTPException(status_code=204, detail="No micro-tasks generated.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating micro-tasks: {e}")

    # Store everything in MongoDB
    response_data = {
        "title": input_data.title,
        "description": input_data.description,
        "targetDate": str(input_data.targetDate),
        "parsed": parsed,
        "micro_tasks": micro_tasks,
        "status": "active"
    }

    try:
        okr_collection.insert_one(response_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving to MongoDB: {e}")

    return OKRResponse(parsed=parsed, micro_tasks=micro_tasks)


# Helper to serialize MongoDB documents
def serialize_document(doc):
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return doc

@app.get("/api/get-okrs")  # get all OKRs
async def get_micro_tasks():
    try:
        docs = list(okr_collection.find())
        serialized = [serialize_document(d) for d in docs]
        return {"result": serialized}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/get-okr/{id}") # get OKR by ID
async def get_okr_by_id(id: str):
    try:
        doc = okr_collection.find_one({"_id": ObjectId(id)})
        if not doc:
            return {"error": "OKR not found"}
        serialized = serialize_document(doc)
        return {"result": serialized}
    except Exception as e:
        return {"error": str(e)}