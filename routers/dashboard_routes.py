from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models import User, Task, Project, ProjectMember, StatusEnum
from dependencies import get_current_user
from datetime import datetime

router = APIRouter(tags=["dashboard"])
templates = Jinja2Templates(directory="templates")


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Get all project IDs the user is in
    memberships = db.query(ProjectMember).filter(ProjectMember.user_id == current_user.id).all()
    project_ids = [m.project_id for m in memberships]
    
    # All tasks in those projects
    all_tasks = db.query(Task).filter(Task.project_id.in_(project_ids)).all()
    
    total_tasks = len(all_tasks)
    todo_count = len([t for t in all_tasks if t.status == StatusEnum.todo])
    in_progress_count = len([t for t in all_tasks if t.status == StatusEnum.in_progress])
    done_count = len([t for t in all_tasks if t.status == StatusEnum.done])
    
    now = datetime.utcnow()
    overdue_count = len([
        t for t in all_tasks
        if t.due_date and t.due_date < now and t.status != StatusEnum.done
    ])
    
    # Tasks per user across those projects
    tasks_per_user = {}
    for task in all_tasks:
        if task.assignee:
            name = task.assignee.name
            tasks_per_user[name] = tasks_per_user.get(name, 0) + 1
    
    tasks_per_user_list = sorted(
        [{"name": k, "count": v} for k, v in tasks_per_user.items()],
        key=lambda x: x["count"],
        reverse=True
    )
    
    # Recent tasks (last 5)
    recent_tasks = sorted(all_tasks, key=lambda t: t.created_at, reverse=True)[:5]
    
    # Overdue tasks list
    overdue_tasks = [
        t for t in all_tasks
        if t.due_date and t.due_date < now and t.status != StatusEnum.done
    ]
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "current_user": current_user,
        "total_tasks": total_tasks,
        "todo_count": todo_count,
        "in_progress_count": in_progress_count,
        "done_count": done_count,
        "overdue_count": overdue_count,
        "tasks_per_user_list": tasks_per_user_list,
        "recent_tasks": recent_tasks,
        "overdue_tasks": overdue_tasks,
        "project_count": len(project_ids)
    })
