from datetime import datetime
from typing import List, Optional
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

# Pydantic Models (Schemas)

class OkrBase(BaseModel):
    title: str
    description: str
    target_date: str

class OkrCreate(OkrBase):
    pass

class Okr(OkrBase):
    id: str = Field(..., alias="_id")
    status: Optional[str] = Field("inactive")
    progress: Optional[int] = Field(0)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    

    model_config = ConfigDict(populate_by_name=True)

class TaskBase(BaseModel):
    okr_id: str = Field(..., alias="okrId") # Changed from int to str for MongoDB ObjectId
    title: str
    description: Optional[str] = None
    deadline: str # Changed from datetime to str for ISO 8601 string

class TaskStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    deadline: Optional[str] = None # Changed from datetime to str for ISO 8601 string
    status: Optional[str] = None
    micro_status: Optional[TaskStatus] = None
    completed_at: Optional[datetime] = Field(None, alias="completedAt")
    proof_url: Optional[str] = Field(None, alias="proofUrl")

class Task(TaskBase):
    id: str = Field(..., alias="_id") # Changed from int to str for MongoDB ObjectId
    status: str
    micro_status: str = "pending"
    completed_at: Optional[datetime] = Field(None, alias="completedAt")
    proof_url: Optional[str] = Field(None, alias="proofUrl")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow, alias="updatedAt")

    model_config = ConfigDict(populate_by_name=True)

class ReminderBase(BaseModel):
    task_id: str = Field(..., alias="taskId") # Changed from int to str for MongoDB ObjectId
    message: str
    delivery_method: str = Field(..., alias="deliveryMethod")

class ReminderCreate(ReminderBase):
    scheduled_for: str = Field(..., alias="scheduledFor") # Changed from datetime to str for ISO 8601 string

class Reminder(ReminderBase):
    id: str = Field(..., alias="_id") # Changed from int to str for MongoDB ObjectId
    status: str
    scheduled_for: str = Field(..., alias="scheduledFor") # Changed from datetime to str for ISO 8601 string
    sent_at: Optional[datetime] = Field(None, alias="sentAt")
    created_at: datetime = Field(..., alias="createdAt")

    model_config = ConfigDict(populate_by_name=True)

# Extended types with relations

class OkrWithTasks(Okr):
    tasks: List["Task"] = []
    completed_tasks: int = Field(0, alias="completedTasks")
    total_tasks: int = Field(0, alias="totalTasks")

    model_config = ConfigDict(populate_by_name=True)

class TaskWithReminders(Task):
    reminders: List[Reminder] = []

    model_config = ConfigDict(populate_by_name=True)