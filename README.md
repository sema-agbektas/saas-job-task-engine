# SaaS Job & Task Engine
A production-ready asynchronous task processing backend built with Clean Architecture principles.

## 🚀 What It Does
Handles long-running background operations (reporting, data processing, email sending) 
without blocking users — using async task queues powered by PostgreSQL and Redis.

## 🛠 Tech Stack
- Python / FastAPI — Async REST API
- PostgreSQL — Task persistence
- Redis — Message broker
- SQLAlchemy — Async ORM
- Alembic — Database migrations
- Docker & Docker Compose — Containerization

## 🏗 Architecture
![System Architecture](./architecture-diagram.svg)

Clean Architecture with clear separation of concerns:
- `domain/` — Core entities, enums, exceptions
- `application/` — Use cases & repository interfaces
- `infrastructure/` — PostgreSQL implementation
- `api/` — FastAPI endpoints
- `worker.py` — Async task processor

## ⚡ Quick Start

# Clone the repo
git clone https://github.com/sema-agbektas/saas-job-task-engine.git

# Copy environment variables
cp .env.example .env

# Start services
docker-compose up -d

# Terminal 1 — API
uvicorn src.api.app:app --reload

# Terminal 2 — Worker
python -m src.worker

API docs: http://localhost:8000/docs

## 📡 API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /tasks/ | Create a new task |
| GET | /tasks/{task_id} | Get task status |
| DELETE | /tasks/{task_id} | Cancel a task |

## ⚙️ Task Lifecycle
PENDING → RUNNING → SUCCESS
                  → FAILED (retries: 3)
