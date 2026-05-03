from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
import os

from database import engine, Base
from routers import auth_routes, project_routes, task_routes, dashboard_routes

load_dotenv()

# Create tables (Alembic handles migrations in prod, this is a fallback)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Team Task Manager")

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY", "fallback-secret-change-this")
)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

app.include_router(auth_routes.router)
app.include_router(project_routes.router)
app.include_router(task_routes.router)
app.include_router(dashboard_routes.router)


@app.get("/")
def root():
    return RedirectResponse(url="/dashboard")


@app.exception_handler(403)
async def forbidden_handler(request: Request, exc):
    return templates.TemplateResponse("base.html", {
        "request": request,
        "error": "You don't have permission to access this page."
    }, status_code=403)


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return templates.TemplateResponse("base.html", {
        "request": request,
        "error": "Page not found."
    }, status_code=404)
