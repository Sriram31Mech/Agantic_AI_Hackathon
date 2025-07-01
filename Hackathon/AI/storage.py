from typing import List, Optional, Dict
from datetime import datetime
from shared.schemas import Okr, OkrCreate, Task, TaskCreate, TaskUpdate, Reminder, ReminderCreate, OkrWithTasks, TaskWithReminders

class IStorage:
    # OKR methods
    async def create_okr(self, okr: OkrCreate) -> Okr:
        pass

    async def get_okrs(self) -> List[OkrWithTasks]:
        pass

    async def get_okr(self, id: int) -> Optional[OkrWithTasks]:
        pass

    async def update_okr_progress(self, id: int, progress: int) -> None:
        pass
    
    # Task methods
    async def create_task(self, task: TaskCreate) -> Task:
        pass

    async def get_tasks(self) -> List[Task]:
        pass

    async def get_tasks_by_okr(self, okr_id: int) -> List[Task]:
        pass

    async def get_task(self, id: int) -> Optional[TaskWithReminders]:
        pass

    async def update_task(self, id: int, updates: TaskUpdate) -> Optional[Task]:
        pass

    async def complete_task(self, id: int, proof_url: Optional[str] = None) -> Optional[Task]:
        pass
    
    # Reminder methods
    async def create_reminder(self, reminder: ReminderCreate) -> Reminder:
        pass

    async def get_reminders(self) -> List[Reminder]:
        pass

    async def get_upcoming_reminders(self) -> List[Reminder]:
        pass

    async def update_reminder_status(self, id: int, status: str) -> None:
        pass

class MemStorage(IStorage):
    def __init__(self):
        self.okrs: Dict[int, Okr] = {}
        self.tasks: Dict[int, Task] = {}
        self.reminders: Dict[int, Reminder] = {}
        self.current_okr_id: int = 1
        self.current_task_id: int = 1
        self.current_reminder_id: int = 1

    async def create_okr(self, insert_okr: OkrCreate) -> Okr:
        id = self.current_okr_id
        self.current_okr_id += 1
        okr = Okr(
            id=id,
            title=insert_okr.title,
            description=insert_okr.description,
            targetDate=insert_okr.target_date,
            status="active",
            progress=0,
            createdAt=datetime.now(),
            updatedAt=datetime.now(),
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
                    completedTasks=completed_tasks,
                    totalTasks=len(tasks),
                )
            )
        
        return okrs_with_tasks

    async def get_okr(self, id: int) -> Optional[OkrWithTasks]:
        okr = self.okrs.get(id)
        if not okr: return None
        
        tasks = [task for task in self.tasks.values() if task.okr_id == id]
        completed_tasks = len([task for task in tasks if task.status == "completed"])
        
        return OkrWithTasks(
            **okr.model_dump(),
            tasks=tasks,
            completedTasks=completed_tasks,
            totalTasks=len(tasks),
        )

    async def update_okr_progress(self, id: int, progress: int) -> None:
        okr = self.okrs.get(id)
        if okr:
            okr.progress = progress
            okr.updated_at = datetime.now()
            self.okrs[id] = okr

    async def create_task(self, insert_task: TaskCreate) -> Task:
        id = self.current_task_id
        self.current_task_id += 1
        task = Task(
            id=id,
            okrId=insert_task.okr_id,
            title=insert_task.title,
            description=insert_task.description,
            deadline=insert_task.deadline,
            status="pending",
            completedAt=None,
            proofUrl=None,
            createdAt=datetime.now(),
        )
        self.tasks[id] = task
        return task

    async def get_tasks(self) -> List[Task]:
        return list(self.tasks.values())

    async def get_tasks_by_okr(self, okr_id: int) -> List[Task]:
        return [task for task in self.tasks.values() if task.okr_id == okr_id]

    async def get_task(self, id: int) -> Optional[TaskWithReminders]:
        task = self.tasks.get(id)
        if not task: return None
        
        reminders = [reminder for reminder in self.reminders.values() if reminder.task_id == id]
        
        return TaskWithReminders(
            **task.model_dump(),
            reminders=reminders,
        )

    async def update_task(self, id: int, updates: TaskUpdate) -> Optional[Task]:
        task = self.tasks.get(id)
        if not task: return None

        updated = False
        if updates.title is not None: task.title = updates.title; updated = True
        if updates.description is not None: task.description = updates.description; updated = True
        if updates.deadline is not None: task.deadline = updates.deadline; updated = True
        if updates.status is not None: task.status = updates.status; updated = True
        if updates.completed_at is not None: task.completed_at = updates.completed_at; updated = True
        if updates.proof_url is not None: task.proof_url = updates.proof_url; updated = True

        if updated:
            self.tasks[id] = task
        return task

    async def complete_task(self, id: int, proof_url: Optional[str] = None) -> Optional[Task]:
        task = self.tasks.get(id)
        if not task: return None

        task.status = "completed"
        task.completed_at = datetime.now()
        task.proof_url = proof_url
        self.tasks[id] = task
        return task

    async def create_reminder(self, insert_reminder: ReminderCreate) -> Reminder:
        id = self.current_reminder_id
        self.current_reminder_id += 1
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

    async def update_reminder_status(self, id: int, status: str) -> None:
        reminder = self.reminders.get(id)
        if reminder:
            reminder.status = status
            if status == "sent":
                reminder.sent_at = datetime.now()
            self.reminders[id] = reminder