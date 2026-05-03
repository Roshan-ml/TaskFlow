from fastapi import Request, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from auth import decode_token
from models import User, ProjectMember, RoleEnum
import uuid


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=302, headers={"Location": "/login"})
    
    email = decode_token(token)
    if not email:
        raise HTTPException(status_code=302, headers={"Location": "/login"})
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=302, headers={"Location": "/login"})
    
    return user


def get_current_user_optional(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        return None
    email = decode_token(token)
    if not email:
        return None
    return db.query(User).filter(User.email == email).first()


def get_project_membership(project_id: str, current_user: User, db: Session):
    try:
        pid = uuid.UUID(project_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Project not found")
    
    membership = db.query(ProjectMember).filter(
        ProjectMember.project_id == pid,
        ProjectMember.user_id == current_user.id
    ).first()
    
    if not membership:
        raise HTTPException(status_code=403, detail="You are not a member of this project")
    
    return membership


def require_admin(project_id: str, current_user: User, db: Session):
    membership = get_project_membership(project_id, current_user, db)
    if membership.role != RoleEnum.admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return membership
