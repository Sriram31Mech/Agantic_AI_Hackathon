from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from datetime import datetime, timedelta
import re
import requests
from pydantic import BaseModel

from shared.schemas import Okr, OkrCreate, Task, TaskCreate, OkrWithTasks, TaskStatus
from storage import MemStorage, IStorage
from agents.okr_parser import parse_okr
from agents.okr_validator import validate_submission

okr_router = APIRouter()

# Pydantic model for validation request
class ValidationRequest(BaseModel):
    submission_id: str
    okr_id: str
    submission_content: str
    submission_type: str

# Dependency to get storage instance
def get_storage() -> IStorage:
    return MemStorage()

async def generate_micro_tasks(okr_id: str, description: str, storage: IStorage) -> List[Task]:
    tasks = []
    now = datetime.now()
    
    parsed_okr = parse_okr(description)
    
    # Basic pattern matching for common OKR types
    if "article" in description.lower() or "blog" in description.lower():
        article_count_match = re.search(r'(\d+)\s*(?:article|blog)', description.lower())
        article_count = int(article_count_match.group(1)) if article_count_match else 3
        
        for i in range(1, article_count + 1):
            task_create_data_write = TaskCreate(
                okrId=okr_id,
                title=f"Write article {i}",
                description=f"Research, write, and publish article {i}",
                deadline=str(now + timedelta(weeks=i)),
            )
            tasks.append(await storage.create_task(task_create_data_write))
            
            task_create_data_research = TaskCreate(
                okrId=okr_id,
                title=f"Research for article {i}",
                description=f"Gather information and sources for article {i}",
                deadline=str(now + timedelta(weeks=i) - timedelta(days=2)),
            )
            tasks.append(await storage.create_task(task_create_data_research))
            
    elif "project" in description.lower() or "coding" in description.lower():
        project_count_match = re.search(r'(\d+)\s*(?:project|coding)', description.lower())
        project_count = int(project_count_match.group(1)) if project_count_match else 5
        
        for i in range(1, project_count + 1):
            task_create_data = TaskCreate(
                okrId=okr_id,
                title=f"Complete project {i}",
                description=f"Build and deploy project {i}",
                deadline=str(now + timedelta(weeks=i*2)),
            )
            tasks.append(await storage.create_task(task_create_data))
    else:
        # Generic task breakdown
        task_create_data_plan = TaskCreate(
            okrId=okr_id,
            title="Plan and research",
            description="Break down the objective and research requirements",
            deadline=str(now + timedelta(weeks=1)),
        )
        tasks.append(await storage.create_task(task_create_data_plan))
        
        task_create_data_execute = TaskCreate(
            okrId=okr_id,
            title="Execute core work",
            description="Complete the main deliverables",
            deadline=str(now + timedelta(weeks=3)),
        )
        tasks.append(await storage.create_task(task_create_data_execute))
        
        task_create_data_review = TaskCreate(
            okrId=okr_id,
            title="Review and finalize",
            description="Review progress and finalize deliverables",
            deadline=str(now + timedelta(weeks=4)),
        )
        tasks.append(await storage.create_task(task_create_data_review))

    return tasks


@okr_router.get("/okrs", response_model=List[OkrWithTasks])
async def get_all_okrs(storage: IStorage = Depends(get_storage)):
    print("Fetching all OKRs with tasks")
    return await storage.get_okrs()

@okr_router.get("/okrs/{okr_id}", response_model=OkrWithTasks)
async def get_okr_by_id(okr_id: str, storage: IStorage = Depends(get_storage)):
    okr = await storage.get_okr(okr_id)
    if not okr:
        raise HTTPException(status_code=404, detail="OKR not found")
    return okr

@okr_router.post("/okrs", response_model=Okr)
async def create_new_okr(okr_create: OkrCreate, storage: IStorage = Depends(get_storage)):
    okr = await storage.create_okr(okr_create)
    tasks = await generate_micro_tasks(okr.id, okr.description, storage)
    return {"okr": okr, "tasks": tasks}

@okr_router.post("/okr/validate")
async def validate_okr_submission(request: ValidationRequest, storage: IStorage = Depends(get_storage)):
    print(f"Received validation request for submission {request.submission_id} and OKR {request.okr_id}")

    # Call the validation agent with submission_content and submission_type
    validation_response = await validate_submission(
        request.submission_id,
        request.okr_id,
        request.submission_content,
        request.submission_type,
        storage
    )

    return validation_response 