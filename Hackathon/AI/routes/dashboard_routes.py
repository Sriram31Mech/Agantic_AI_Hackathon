from fastapi import APIRouter, Depends
from typing import List, Dict, Any
from datetime import datetime, timedelta

from storage import MemStorage, IStorage
from shared.schemas import Okr, Task, Reminder

dashboard_router = APIRouter()

def get_storage() -> IStorage:
    return MemStorage()

@dashboard_router.get("/dashboard/stats", response_model=Dict[str, Any])
async def get_dashboard_stats(storage: IStorage = Depends(get_storage)):
    okrs: List[Okr] = await storage.get_okrs()
    tasks: List[Task] = await storage.get_tasks()
    reminders: List[Reminder] = await storage.get_upcoming_reminders()

    now = datetime.now()

    # Active OKRs (treat missing status as inactive)
    active_okrs = len([
        okr for okr in okrs
        if (okr.status or "").lower() == "active"
    ])
    print(f"Active OKRs: {tasks}")

    # Completed tasks (treat missing status as not completed)
    completed_tasks = len([
        task for task in tasks
        if (task.status or "").lower() == "completed"
    ])

    # Overall OKR progress
    valid_progress_okrs = [okr for okr in okrs if hasattr(okr, "progress") and isinstance(okr.progress, (int, float))]
    overall_progress = round(sum(okr.progress for okr in valid_progress_okrs) / len(valid_progress_okrs)) if valid_progress_okrs else 0

    # Weekly tasks
    week_start = now - timedelta(days=now.weekday())
    weekly_tasks = [task for task in tasks if task.createdAt >= week_start]
    weekly_completed = len([task for task in weekly_tasks if getattr(task, "status", "").lower() == "completed"])
    weekly_percentage = round((weekly_completed / len(weekly_tasks)) * 100) if weekly_tasks else 0

    # Monthly tasks
    month_start = now.replace(day=1)
    monthly_tasks = [task for task in tasks if task.createdAt >= month_start]
    monthly_completed = len([task for task in monthly_tasks if getattr(task, "status", "").lower() == "completed"])
    monthly_percentage = round((monthly_completed / len(monthly_tasks)) * 100) if monthly_tasks else 0

    return {
        "activeOkrs": active_okrs,
        "completedTasks": completed_tasks,
        "overallProgress": overall_progress,
        "weeklyProgress": {
            "completed": weekly_completed,
            "total": len(weekly_tasks),
            "percentage": weekly_percentage,
        },
        "monthlyProgress": {
            "completed": monthly_completed,
            "total": len(monthly_tasks),
            "percentage": monthly_percentage,
        },
        "upcomingReminders": len(reminders),
    }
