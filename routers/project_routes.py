from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
from models import User, Project, ProjectMember, RoleEnum
from dependencies import get_current_user, get_project_membership, require_admin
from datetime import datetime
import uuid

router = APIRouter(tags=["projects"])
templates = Jinja2Templates(directory="templates")


@router.get("/projects", response_class=HTMLResponse)
def projects_page(request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    memberships = db.query(ProjectMember).filter(ProjectMember.user_id == current_user.id).all()
    projects_data = []
    for m in memberships:
        project = m.project
        member_count = db.query(ProjectMember).filter(ProjectMember.project_id == project.id).count()
        task_count = len(project.tasks)
        projects_data.append({
            "project": project,
            "role": m.role,
            "member_count": member_count,
            "task_count": task_count
        })
    error = request.session.pop("error", None)
    success = request.session.pop("success", None)
    return templates.TemplateResponse("projects.html", {
        "request": request,
        "current_user": current_user,
        "projects_data": projects_data,
        "error": error,
        "success": success
    })


@router.post("/projects")
def create_project(
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not name.strip():
        request.session["error"] = "Project name is required"
        return RedirectResponse(url="/projects", status_code=302)
    
    project = Project(
        name=name.strip(),
        description=description.strip(),
        created_by_id=current_user.id
    )
    db.add(project)
    db.flush()
    
    membership = ProjectMember(
        project_id=project.id,
        user_id=current_user.id,
        role=RoleEnum.admin
    )
    db.add(membership)
    db.commit()
    
    request.session["success"] = f"Project '{name}' created successfully!"
    return RedirectResponse(url=f"/projects/{project.id}", status_code=302)


@router.get("/projects/{project_id}", response_class=HTMLResponse)
def project_detail(
    project_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        pid = uuid.UUID(project_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = db.query(Project).filter(Project.id == pid).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    membership = get_project_membership(project_id, current_user, db)
    members = db.query(ProjectMember).filter(ProjectMember.project_id == pid).all()
    
    # Group tasks by status
    todo_tasks = [t for t in project.tasks if t.status.value == "todo"]
    in_progress_tasks = [t for t in project.tasks if t.status.value == "in_progress"]
    done_tasks = [t for t in project.tasks if t.status.value == "done"]
    
    error = request.session.pop("error", None)
    success = request.session.pop("success", None)
    
    return templates.TemplateResponse("project_detail.html", {
        "request": request,
        "current_user": current_user,
        "project": project,
        "membership": membership,
        "members": members,
        "todo_tasks": todo_tasks,
        "in_progress_tasks": in_progress_tasks,
        "done_tasks": done_tasks,
        "error": error,
        "success": success,
        "all_members": members,
        "now": datetime.utcnow()
    })


@router.post("/projects/{project_id}/members")
def add_member(
    project_id: str,
    request: Request,
    email: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    require_admin(project_id, current_user, db)
    
    user_to_add = db.query(User).filter(User.email == email).first()
    if not user_to_add:
        request.session["error"] = f"No user found with email: {email}"
        return RedirectResponse(url=f"/projects/{project_id}", status_code=302)
    
    pid = uuid.UUID(project_id)
    existing = db.query(ProjectMember).filter(
        ProjectMember.project_id == pid,
        ProjectMember.user_id == user_to_add.id
    ).first()
    
    if existing:
        request.session["error"] = "User is already a member of this project"
        return RedirectResponse(url=f"/projects/{project_id}", status_code=302)
    
    membership = ProjectMember(
        project_id=pid,
        user_id=user_to_add.id,
        role=RoleEnum.member
    )
    db.add(membership)
    db.commit()
    
    request.session["success"] = f"{user_to_add.name} added as member"
    return RedirectResponse(url=f"/projects/{project_id}", status_code=302)


@router.post("/projects/{project_id}/members/{user_id}/remove")
def remove_member(
    project_id: str,
    user_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    require_admin(project_id, current_user, db)
    
    pid = uuid.UUID(project_id)
    uid = uuid.UUID(user_id)
    
    if uid == current_user.id:
        request.session["error"] = "You cannot remove yourself from the project"
        return RedirectResponse(url=f"/projects/{project_id}", status_code=302)
    
    membership = db.query(ProjectMember).filter(
        ProjectMember.project_id == pid,
        ProjectMember.user_id == uid
    ).first()
    
    if membership:
        db.delete(membership)
        db.commit()
        request.session["success"] = "Member removed successfully"
    
    return RedirectResponse(url=f"/projects/{project_id}", status_code=302)
