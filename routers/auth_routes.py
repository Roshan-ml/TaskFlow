from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
from models import User
from auth import get_password_hash, verify_password, create_access_token
from dependencies import get_current_user_optional

router = APIRouter(tags=["auth"])
templates = Jinja2Templates(directory="templates")


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request, current_user=Depends(get_current_user_optional)):
    if current_user:
        return RedirectResponse(url="/dashboard", status_code=302)
    error = request.session.pop("error", None)
    return templates.TemplateResponse("login.html", {"request": request, "error": error})


@router.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        request.session["error"] = "Invalid email or password"
        return RedirectResponse(url="/login", status_code=302)
    
    token = create_access_token(data={"sub": user.email})
    response = RedirectResponse(url="/dashboard", status_code=302)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=86400,
        samesite="lax"
    )
    return response


@router.get("/signup", response_class=HTMLResponse)
def signup_page(request: Request, current_user=Depends(get_current_user_optional)):
    if current_user:
        return RedirectResponse(url="/dashboard", status_code=302)
    error = request.session.pop("error", None)
    return templates.TemplateResponse("signup.html", {"request": request, "error": error})


@router.post("/signup")
def signup(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    if len(password) < 6:
        request.session["error"] = "Password must be at least 6 characters"
        return RedirectResponse(url="/signup", status_code=302)
    
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        request.session["error"] = "Email already registered"
        return RedirectResponse(url="/signup", status_code=302)
    
    user = User(
        name=name,
        email=email,
        hashed_password=get_password_hash(password)
    )
    db.add(user)
    db.commit()
    
    token = create_access_token(data={"sub": user.email})
    response = RedirectResponse(url="/dashboard", status_code=302)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=86400,
        samesite="lax"
    )
    return response


@router.get("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("access_token")
    return response
