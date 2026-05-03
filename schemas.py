from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
import uuid


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None


class AddMember(BaseModel):
    email: EmailStr


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = "medium"
    due_date: Optional[str] = None
    assigned_to_id: Optional[str] = None


class TaskStatusUpdate(BaseModel):
    status: str
