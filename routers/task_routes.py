from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from database import get_db
from models import User, Task, ProjectMember, RoleEnum, PriorityEnum, StatusEnum
from dependencies import get_current_user, get_project_membership, require_admin
from datetime import datetime
import uuid

router = APIRouter(tags=["tasks"])


@router.post("/projects/{project_id}/tasks")
def create_task(
    project_id: str,
    request: Request,
    title: str = Form(...),
    description: str = Form(""),
    priority: str = Form("medium"),
    due_date: str = Form(""),
    assigned_to_id: str = Form(""),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    require_admin(project_id, current_user, db)
    
    if not title.strip():
        request.session["error"] = "Task title is required"
        return RedirectResponse(url=f"/projects/{project_id}", status_code=302)
    
    pid = uuid.UUID(project_id)
    
    due = None
    if due_date:
        try:
            due = datetime.strptime(due_date, "%Y-%m-%d")
        except ValueError:
            pass
    
    assigned_id = None
    if assigned_to_id:
        try:
            assigned_id = uuid.UUID(assigned_to_id)
        except ValueError:
            pass
    
    task = Task(
        title=title.strip(),
        description=description.strip(),
        priority=PriorityEnum(priority),
        status=StatusEnum.todo,
        due_date=due,
        project_id=pid,
        assigned_to_id=assigned_id,
        created_by_id=current_user.id
    )
    db.add(task)
    db.commit()
    
    request.session["success"] = f"Task '{title}' created!"
    return RedirectResponse(url=f"/projects/{project_id}", status_code=302)


@router.post("/tasks/{task_id}/status")
def update_task_status(
    task_id: str,
    request: Request,
    status: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        tid = uuid.UUID(task_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = db.query(Task).filter(Task.id == tid).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    project_id = str(task.project_id)
    membership = get_project_membership(project_id, current_user, db)
    
    # Members can only update tasks assigned to them
    if membership.role == RoleEnum.member and task.assigned_to_id != current_user.id:
        request.session["error"] = "You can only update tasks assigned to you"
        return RedirectResponse(url=f"/projects/{project_id}", status_code=302)
    
    try:
        task.status = StatusEnum(status)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    db.commit()
    return RedirectResponse(url=f"/projects/{project_id}", status_code=302)


@router.post("/tasks/{task_id}/delete")
def delete_task(
    task_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        tid = uuid.UUID(task_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = db.query(Task).filter(Task.id == tid).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    project_id = str(task.project_id)
    require_admin(project_id, current_user, db)
    
    db.delete(task)
    db.commit()
    
    request.session["success"] = "Task deleted"
    return RedirectResponse(url=f"/projects/{project_id}", status_code=302)


@router.post("/tasks/{task_id}/edit")
def edit_task(
    task_id: str,
    request: Request,
    title: str = Form(...),
    description: str = Form(""),
    priority: str = Form("medium"),
    due_date: str = Form(""),
    assigned_to_id: str = Form(""),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        tid = uuid.UUID(task_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = db.query(Task).filter(Task.id == tid).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    project_id = str(task.project_id)
    require_admin(project_id, current_user, db)
    
    task.title = title.strip()
    task.description = description.strip()
    task.priority = PriorityEnum(priority)
    
    if due_date:
        try:
            task.due_date = datetime.strptime(due_date, "%Y-%m-%d")
        except ValueError:
            pass
    else:
        task.due_date = None
    
    if assigned_to_id:
        try:
            task.assigned_to_id = uuid.UUID(assigned_to_id)
        except ValueError:
            task.assigned_to_id = None
    else:
        task.assigned_to_id = None
    
    db.commit()
    request.session["success"] = "Task updated"
    return RedirectResponse(url=f"/projects/{project_id}", status_code=302)
