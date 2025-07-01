from fastapi import APIRouter, Depends, HTTPException
from typing import List

from shared.schemas import Reminder, ReminderCreate
from storage import MemStorage, IStorage

reminder_router = APIRouter()

# Dependency to get storage instance
def get_storage() -> IStorage:
    return MemStorage()

@reminder_router.get("/reminders", response_model=List[Reminder])
async def get_all_reminders(storage: IStorage = Depends(get_storage)):
    return await storage.get_reminders()

@reminder_router.get("/reminders/upcoming", response_model=List[Reminder])
async def get_upcoming_reminders(storage: IStorage = Depends(get_storage)):
    return await storage.get_upcoming_reminders()

@reminder_router.post("/reminders", response_model=Reminder)
async def create_new_reminder(reminder_create: ReminderCreate, storage: IStorage = Depends(get_storage)):
    reminder = await storage.create_reminder(reminder_create)
    return reminder

@reminder_router.patch("/reminders/{reminder_id}/status")
async def update_reminder_status(reminder_id: str, status: str, storage: IStorage = Depends(get_storage)):
    await storage.update_reminder_status(reminder_id, status)
    return {"success": True} 