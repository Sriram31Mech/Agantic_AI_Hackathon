from typing import List, Optional, Dict, Union
from datetime import datetime
from shared.schemas import Okr, OkrCreate, Task, TaskCreate, TaskUpdate, Reminder, ReminderCreate, OkrWithTasks, TaskWithReminders, TaskStatus
import uuid
import os
from pymongo.database import Database
from bson import ObjectId
from mongo_clients import db, okr_collection, task_collection, reminder_collection # Import existing MongoDB client and collections

class IStorage:
    # OKR methods
    async def create_okr(self, okr: OkrCreate) -> Okr:
        pass

    async def get_okrs(self) -> List[OkrWithTasks]:
        pass

    async def get_okr(self, id: str) -> Optional[OkrWithTasks]:
        pass

    async def update_okr_progress(self, id: str, progress: int) -> None:
        pass

    async def update_okr_status(self, okr_id: str, status: str) -> None:
        pass
    
    # Task methods
    async def create_task(self, task: TaskCreate) -> Task:
        pass

    async def get_tasks(self) -> List[Task]:
        pass

    async def get_tasks_by_okr(self, okr_id: str) -> List[Task]:
        pass

    async def get_task(self, id: str) -> Optional[TaskWithReminders]:
        pass

    async def update_task(self, id: str, updates: TaskUpdate) -> Optional[Task]:
        pass

    async def update_task_status(self, task_id: str, status: Union[str, TaskStatus]) -> None:
        pass

    async def complete_task(self, id: str, proof_url: Optional[str] = None) -> Optional[Task]:
        pass
    
    # Reminder methods
    async def create_reminder(self, reminder: ReminderCreate) -> Reminder:
        pass

    async def get_reminders(self) -> List[Reminder]:
        pass

    async def get_upcoming_reminders(self) -> List[Reminder]:
        pass

    async def update_reminder_status(self, id: str, status: str) -> None:
        pass

class MemStorage(IStorage):
    def __init__(self):
        self.okrs: Dict[str, Okr] = {}
        self.tasks: Dict[str, Task] = {}
        self.reminders: Dict[str, Reminder] = {}

    async def create_okr(self, insert_okr: OkrCreate) -> Okr:
        id = str(uuid.uuid4())
        okr = Okr(
            id=id,
            title=insert_okr.title,
            description=insert_okr.description,
            target_date=insert_okr.target_date,
            status="active",
            progress=0,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        self.okrs[id] = okr
        return okr

    async def get_okrs(self) -> List[OkrWithTasks]:
        okrs_with_tasks: List[OkrWithTasks] = []
        
        for okr in self.okrs.values():
            tasks = [task for task in self.tasks.values() if task.okr_id == okr.id]
            completed_tasks = len([task for task in tasks if task.status == "completed"])
            
            okrs_with_tasks.append(
                OkrWithTasks(
                    **okr.model_dump(),
                    tasks=tasks,
                    completed_tasks=completed_tasks,
                    total_tasks=len(tasks),
                )
            )
        
        return okrs_with_tasks

    async def get_okr(self, id: str) -> Optional[OkrWithTasks]:
        okr = self.okrs.get(id)
        if not okr: return None
        
        tasks = [task for task in self.tasks.values() if task.okr_id == id]
        completed_tasks = len([task for task in tasks if task.status == "completed"])
        
        return OkrWithTasks(
            **okr.model_dump(),
            tasks=tasks,
            completed_tasks=completed_tasks,
            total_tasks=len(tasks),
        )

    async def update_okr_progress(self, id: str, progress: int) -> None:
        okr = self.okrs.get(id)
        if okr:
            okr.progress = progress
            okr.updated_at = datetime.now()
            self.okrs[id] = okr

    async def update_okr_status(self, okr_id: str, status: str) -> None:
        okr = self.okrs.get(okr_id)
        if okr:
            okr.status = status
            okr.updated_at = datetime.now()
            self.okrs[okr_id] = okr

    async def create_task(self, insert_task: TaskCreate) -> Task:
        id = str(uuid.uuid4())
        task = Task(
            id=id,
            okrId=insert_task.okr_id,
            title=insert_task.title,
            description=insert_task.description,
            deadline=insert_task.deadline,
            status="pending",
            micro_status=TaskStatus.PENDING,
            completedAt=None,
            proofUrl=None,
            createdAt=datetime.now(),
        )
        self.tasks[id] = task
        return task

    async def get_tasks(self) -> List[Task]:
        return list(self.tasks.values())

    async def get_tasks_by_okr(self, okr_id: str) -> List[Task]:
        return [task for task in self.tasks.values() if task.okr_id == okr_id]

    async def get_task(self, id: str) -> Optional[TaskWithReminders]:
        task = self.tasks.get(id)
        if not task: return None
        
        reminders = [reminder for reminder in self.reminders.values() if reminder.task_id == id]
        
        return TaskWithReminders(
            **task.model_dump(),
            reminders=reminders,
        )

    async def update_task(self, id: str, updates: TaskUpdate) -> Optional[Task]:
        task = self.tasks.get(id)
        if not task: return None

        updated = False
        if updates.title is not None: task.title = updates.title; updated = True
        if updates.description is not None: task.description = updates.description; updated = True
        if updates.deadline is not None: task.deadline = updates.deadline; updated = True
        if updates.status is not None: task.status = updates.status; updated = True
        if updates.micro_status is not None: task.micro_status = updates.micro_status; updated = True
        if updates.completed_at is not None: task.completed_at = updates.completed_at; updated = True
        if updates.proof_url is not None: task.proof_url = updates.proof_url; updated = True

        if updated:
            self.tasks[id] = task
        return task

    async def update_task_status(self, task_id: str, status: Union[str, TaskStatus]) -> None:
        task = self.tasks.get(task_id)
        if task:
            if isinstance(status, str):
                # Convert string status to TaskStatus enum
                if status.lower() == "completed":
                    status_enum = TaskStatus.COMPLETED
                elif status.lower() == "pending":
                    status_enum = TaskStatus.PENDING
                elif status.lower() == "active":
                    status_enum = TaskStatus.ACTIVE
                else:
                    # Handle unknown string status, perhaps raise an error or log a warning
                    print(f"WARNING: Unknown task status string: {status}")
                    status_enum = TaskStatus.PENDING # Default to pending
            else:
                status_enum = status
            
            task.status = status_enum.value
            task.micro_status = status_enum
            task.updated_at = datetime.now()
            self.tasks[task_id] = task

    async def complete_task(self, id: str, proof_url: Optional[str] = None) -> Optional[Task]:
        task = self.tasks.get(id)
        if not task: return None

        task.status = "completed"
        task.micro_status = TaskStatus.COMPLETED
        task.completed_at = datetime.now()
        task.proof_url = proof_url
        self.tasks[id] = task
        return task

    async def create_reminder(self, insert_reminder: ReminderCreate) -> Reminder:
        id = str(uuid.uuid4())
        reminder = Reminder(
            id=id,
            taskId=insert_reminder.task_id,
            message=insert_reminder.message,
            deliveryMethod=insert_reminder.delivery_method,
            status="pending",
            scheduledFor=insert_reminder.scheduled_for,
            sentAt=None,
            createdAt=datetime.now(),
        )
        self.reminders[id] = reminder
        return reminder

    async def get_reminders(self) -> List[Reminder]:
        return list(self.reminders.values())

    async def get_upcoming_reminders(self) -> List[Reminder]:
        now = datetime.now()
        return [r for r in self.reminders.values() if r.status == "pending" and r.scheduled_for > now]

    async def update_reminder_status(self, id: str, status: str) -> None:
        reminder = self.reminders.get(id)
        if reminder:
            reminder.status = status
            if status == "sent":
                reminder.sent_at = datetime.now()
            self.reminders[id] = reminder

class MongoStorage(IStorage):
    def __init__(self):
        # Use the global db and collections imported from mongo_clients.py
        self.db = db
        self.okr_collection_mongo = self.db["okrs"] # For actual OKRs
        self.task_collection_mongo = okr_collection # This is the user's 'micro_tasks' collection for tasks
        self.reminder_collection_mongo = reminder_collection

    async def create_okr(self, okr_data: OkrCreate) -> Okr:
        # MongoDB will generate _id automatically
        insert_data = okr_data.model_dump(by_alias=True, exclude_none=True)
        insert_data["status"] = "active"
        insert_data["progress"] = 0
        insert_data["created_at"] = datetime.now()
        insert_data["updated_at"] = datetime.now()

        result = self.okr_collection_mongo.insert_one(insert_data)
        new_okr = self.okr_collection_mongo.find_one({"_id": result.inserted_id})
        return Okr.model_validate(new_okr)

    async def get_okrs(self) -> List[OkrWithTasks]:
        okrs_with_tasks = []
        for okr_doc in self.okr_collection_mongo.find():
            okr = Okr.model_validate(okr_doc)
            # Assuming tasks related to OKRs are in task_collection_mongo (micro_tasks)
            tasks = []
            for task_doc in self.task_collection_mongo.find({"okrId": okr.id}):
                tasks.append(Task.model_validate(task_doc))

            completed_tasks = len([task for task in tasks if task.status == "completed"])
            okrs_with_tasks.append(
                OkrWithTasks(
                    **okr.model_dump(),
                    tasks=tasks,
                    completed_tasks=completed_tasks,
                    total_tasks=len(tasks),
                )
            )
        return okrs_with_tasks

    async def get_okr(self, id: str) -> Optional[OkrWithTasks]:
        okr_doc = self.okr_collection_mongo.find_one({"_id": ObjectId(id)})
        if not okr_doc: return None
        okr = Okr.model_validate(okr_doc)

        tasks = []
        for task_doc in self.task_collection_mongo.find({"okrId": okr.id}):
            tasks.append(Task.model_validate(task_doc))

        completed_tasks = len([task for task in tasks if task.status == "completed"])
        return OkrWithTasks(
            **okr.model_dump(),
            tasks=tasks,
            completed_tasks=completed_tasks,
            total_tasks=len(tasks),
        )

    async def update_okr_progress(self, id: str, progress: int) -> None:
        self.okr_collection_mongo.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"progress": progress, "updated_at": datetime.now()}}
        )

    async def update_okr_status(self, okr_id: str, status: str) -> None:
        self.okr_collection_mongo.update_one(
            {"_id": ObjectId(okr_id)},
            {"$set": {"status": status, "updated_at": datetime.now()}}
        )

    async def create_task(self, insert_task: TaskCreate) -> Task:
        insert_data = insert_task.model_dump(by_alias=True, exclude_none=True)
        insert_data["status"] = "pending"
        insert_data["micro_status"] = TaskStatus.PENDING.value
        insert_data["completedAt"] = None
        insert_data["proofUrl"] = None
        insert_data["createdAt"] = datetime.now()
        insert_data["updatedAt"] = datetime.now() # Add updatedAt for tasks

        result = self.task_collection_mongo.insert_one(insert_data)
        new_task = self.task_collection_mongo.find_one({"_id": result.inserted_id})
        return Task.model_validate(new_task)

    async def get_tasks(self) -> List[Task]:
        tasks = []
        for task_doc in self.task_collection_mongo.find():
            tasks.append(Task.model_validate(task_doc))
        return tasks

    async def get_tasks_by_okr(self, okr_id: str) -> List[Task]:
        tasks = []
        for task_doc in self.task_collection_mongo.find({"okrId": okr_id}):
            tasks.append(Task.model_validate(task_doc))
        return tasks

    async def get_task(self, id: str) -> Optional[TaskWithReminders]:
        task_doc = self.task_collection_mongo.find_one({"_id": ObjectId(id)})
        if not task_doc: return None
        task = Task.model_validate(task_doc)

        reminders = []
        for reminder_doc in self.reminder_collection_mongo.find({"taskId": task.id}):
            reminders.append(Reminder.model_validate(reminder_doc))
        
        return TaskWithReminders(
            **task.model_dump(),
            reminders=reminders,
        )

    async def update_task(self, id: str, updates: TaskUpdate) -> Optional[Task]:
        update_fields = updates.model_dump(by_alias=True, exclude_none=True)
        if "micro_status" in update_fields: # Convert enum to value for storage
            update_fields["micro_status"] = update_fields["micro_status"].value
        update_fields["updatedAt"] = datetime.now() # Ensure updatedAt is updated

        result = self.task_collection_mongo.update_one(
            {"_id": ObjectId(id)},
            {"$set": update_fields}
        )
        if result.modified_count == 0: return None
        updated_task_doc = self.task_collection_mongo.find_one({"_id": ObjectId(id)})
        return Task.model_validate(updated_task_doc)

    async def update_task_status(self, task_id: str, status: Union[str, TaskStatus]) -> None:
        # Validate if task_id is a valid ObjectId string before proceeding
        if not ObjectId.is_valid(task_id):
            print(f"WARNING: Invalid ObjectId string for task_id: {task_id}. Cannot update task status.")
            return

        if isinstance(status, str):
            if status.lower() == "completed":
                status_enum = TaskStatus.COMPLETED
            elif status.lower() == "pending":
                status_enum = TaskStatus.PENDING
            elif status.lower() == "active":
                status_enum = TaskStatus.ACTIVE
            else:
                print(f"WARNING: Unknown task status string: {status}")
                status_enum = TaskStatus.PENDING # Default to pending
        else:
            status_enum = status
        
        self.task_collection_mongo.update_one(
            {"_id": ObjectId(task_id)},
            {"$set": {
                "status": status_enum.value,
                "micro_status": status_enum.value,
                "updatedAt": datetime.now()
            }}
        )

    async def complete_task(self, id: str, proof_url: Optional[str] = None) -> Optional[Task]:
        update_fields = {
            "status": "completed",
            "micro_status": TaskStatus.COMPLETED.value,
            "completedAt": datetime.now(),
            "proofUrl": proof_url,
            "updatedAt": datetime.now()
        }
        result = self.task_collection_mongo.update_one(
            {"_id": ObjectId(id)},
            {"$set": update_fields}
        )
        if result.modified_count == 0: return None
        updated_task_doc = self.task_collection_mongo.find_one({"_id": ObjectId(id)})
        return Task.model_validate(updated_task_doc)

    async def create_reminder(self, insert_reminder: ReminderCreate) -> Reminder:
        insert_data = insert_reminder.model_dump(by_alias=True, exclude_none=True)
        insert_data["status"] = "pending"
        insert_data["sentAt"] = None
        insert_data["createdAt"] = datetime.now()

        result = self.reminder_collection_mongo.insert_one(insert_data)
        new_reminder = self.reminder_collection_mongo.find_one({"_id": result.inserted_id})
        return Reminder.model_validate(new_reminder)

    async def get_reminders(self) -> List[Reminder]:
        reminders = []
        for reminder_doc in self.reminder_collection_mongo.find():
            reminders.append(Reminder.model_validate(reminder_doc))
        return reminders

    async def get_upcoming_reminders(self) -> List[Reminder]:
        now = datetime.now()
        reminders = []
        for reminder_doc in self.reminder_collection_mongo.find({"status": "pending", "scheduledFor": {"$gt": now.isoformat()}}): # Assuming scheduledFor is ISO string
            reminders.append(Reminder.model_validate(reminder_doc))
        return reminders

    async def update_reminder_status(self, id: str, status: str) -> None:
        update_fields = {"status": status}
        if status == "sent":
            update_fields["sentAt"] = datetime.now()
        
        self.reminder_collection_mongo.update_one(
            {"_id": ObjectId(id)},
            {"$set": update_fields}
        )