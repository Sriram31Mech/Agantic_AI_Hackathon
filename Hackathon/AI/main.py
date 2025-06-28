import sys
import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from datetime import date
from pymongo import MongoClient
from dotenv import load_dotenv

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

app = FastAPI(title="OKR Action Tracker API")

# 👇 Add CORS middleware here
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
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

class OKRResponse(BaseModel):
    parsed: dict
    micro_tasks: list[MicroTask]

# --- Endpoint to Process OKRs ---
@app.post("/process_okr", response_model=OKRResponse)
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
        "micro_tasks": micro_tasks
    }

    try:
        okr_collection.insert_one(response_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving to MongoDB: {e}")

    return OKRResponse(parsed=parsed, micro_tasks=micro_tasks)

