# ⚡ TaskFlow – Team Task Manager

A full-stack team task management web app built with Python FastAPI, PostgreSQL, and Jinja2 templates.


## Features
- JWT-based authentication (httpOnly cookies)
- Create and manage projects
- Role-based access: Admin and Member roles
- Kanban task board (To Do / In Progress / Done)
- Priority levels (High / Medium / Low) with color coding
- Assign tasks to team members
- Overdue task detection and dashboard alerts
- Real-time status updates via dropdown forms

## Tech Stack
| Layer | Technology |
|---|---|
| Backend | Python 3.11 + FastAPI |
| Templating | Jinja2 |
| Styling | Tailwind CSS (CDN) |
| Database | PostgreSQL |
| ORM | SQLAlchemy 2.0 |
| Migrations | Alembic |
| Auth | JWT + passlib/bcrypt |
| Deployment | Railway |

## Local Setup

```bash
# 1. Clone the repo
git clone https://github.com/Roshan-ml/team-task-manager
cd team-task-manager

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your PostgreSQL credentials

# 5. Run database migrations
alembic upgrade head

# 6. Start the server
uvicorn main:app --reload

# 7. Open http://localhost:8000
```

## Environment Variables
| Variable | Description |
|---|---|
| DATABASE_URL | PostgreSQL connection string |
| SECRET_KEY | JWT signing secret (min 32 chars) |
| ALGORITHM | JWT algorithm (HS256) |
| ACCESS_TOKEN_EXPIRE_MINUTES | Token expiry (default: 1440 = 24h) |

## Deployment (Railway)
1. Push code to GitHub
2. Create new project on railway.app
3. Add PostgreSQL plugin
4. Connect GitHub repo
5. Add environment variables (DATABASE_URL is auto-set by Railway plugin)
6. Deploy — Railway auto-runs migrations via Procfile

## API Endpoints
| Method | Route | Description |
|---|---|---|
| POST | /signup | Create account |
| POST | /login | Login |
| GET | /logout | Logout |
| GET | /dashboard | Dashboard stats |
| GET | /projects | List projects |
| POST | /projects | Create project |
| GET | /projects/{id} | Project detail + kanban |
| POST | /projects/{id}/members | Add member (admin) |
| POST | /projects/{id}/tasks | Create task (admin) |
| POST | /tasks/{id}/status | Update task status |
| POST | /tasks/{id}/edit | Edit task (admin) |
| POST | /tasks/{id}/delete | Delete task (admin) |
