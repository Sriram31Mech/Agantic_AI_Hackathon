from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional

from shared.schemas import Task, TaskCreate, TaskUpdate, TaskWithReminders
from storage import MemStorage, IStorage

task_router = APIRouter()

# Dependency to get storage instance
def get_storage() -> IStorage:
    return MemStorage()

@task_router.get("/tasks", response_model=List[Task])
async def get_all_tasks(storage: IStorage = Depends(get_storage)):
    return await storage.get_tasks()

@task_router.get("/tasks/{task_id}", response_model=TaskWithReminders)
async def get_task_by_id(task_id: int, storage: IStorage = Depends(get_storage)):
    task = await storage.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@task_router.post("/tasks", response_model=Task)
async def create_new_task(task_create: TaskCreate, storage: IStorage = Depends(get_storage)):
    task = await storage.create_task(task_create)
    return task

@task_router.patch("/tasks/{task_id}", response_model=Task)
async def update_existing_task(task_id: int, task_update: TaskUpdate, storage: IStorage = Depends(get_storage)):
    task = await storage.update_task(task_id, task_update)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@task_router.post("/tasks/{task_id}/complete", response_model=Task)
async def complete_existing_task(task_id: int, proof_url: Optional[str] = None, storage: IStorage = Depends(get_storage)):
    task = await storage.complete_task(task_id, proof_url)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task 