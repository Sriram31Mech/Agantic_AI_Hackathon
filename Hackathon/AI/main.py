from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from datetime import date
import sys
import os
from pymongo import MongoClient
from dotenv import load_dotenv

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

app = FastAPI(title="OKR Action Tracker API")

# --- MongoDB Setup ---
MONGO_URI = os.getenv("MONGODB_URL")
if not MONGO_URI:
    raise RuntimeError("❌ MONGO_URI not found in .env file!")

client = MongoClient(MONGO_URI)

def test_mongo_connection():
    try:
        client.admin.command("ping")  # Pings MongoDB server
        return {"status": "success", "message": "MongoDB is connected."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MongoDB connection failed: {e}")

# --- Request and Response Models ---
class OKRInput(BaseModel):
    title: str = Field(..., min_length=1, example="Publish AI Articles")
    description: str = Field(..., min_length=10, example="I want to publish 3 AI articles this quarter.")
    deadline: date = Field(..., example="2025-09-30")

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
    okr_input = f"{input_data.description} by {input_data.deadline}"

    try:
        parsed = parse_okr(okr_input)
        parsed["key_results"] = parsed.get("deliverables", [])
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parsing OKR: {e}")

    try:
        micro_tasks = create_micro_tasks(parsed, deadline=str(input_data.deadline))
        if not micro_tasks:
            raise HTTPException(status_code=204, detail="No micro-tasks generated.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating micro-tasks: {e}")

    return OKRResponse(parsed=parsed, micro_tasks=micro_tasks)

# --- Endpoint to Check MongoDB Connection ---
@app.get("/check_db")
def check_db_connection():
    return test_mongo_connection()
