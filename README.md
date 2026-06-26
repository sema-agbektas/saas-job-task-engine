# SaaS Job & Task Engine

A production-ready asynchronous task processing backend built with Clean Architecture principles.

## What It Does

Handles long-running background operations (reporting, data processing, email sending)
without blocking users — using async task queues powered by PostgreSQL and Redis.

## Tech Stack

- **FastAPI** — Async REST API
- **PostgreSQL** — Task & user persistence
- **Redis** — Message broker / task queue
- **SQLAlchemy** — Async ORM
- **Alembic** — Database migrations
- **Docker & Docker Compose** — Containerization
- **JWT** — Authentication

## Architecture

Clean Architecture with clear separation of concerns:

```
src/
├── domain/         # Core entities, enums, exceptions
├── application/    # Use cases & repository interfaces
├── infrastructure/ # PostgreSQL repositories
├── api/            # FastAPI endpoints
└── worker.py       # Async task processor
```

## Quick Start

```bash
# Clone the repo
git clone https://github.com/sema-agbektas/saas-job-task-engine.git
cd saas-job-task-engine

# Create .env file
cp .env.example .env

# Start all services (API + Worker + PostgreSQL + Redis)
docker-compose up --build -d

# Run migrations
docker-compose exec api alembic upgrade head
```

API docs: http://localhost:8000/docs

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | /auth/register | No | Register a new user |
| POST | /auth/login | No | Login, get JWT token |
| POST | /tasks/ | Yes | Create a new task |
| GET | /tasks/ | No | List all tasks |
| GET | /tasks/{task_id} | No | Get task status |
| DELETE | /tasks/{task_id} | No | Cancel a task |

## Task Lifecycle

```
PENDING → RUNNING → SUCCESS
                 → FAILED (retries: 3)
                 → RETRYING
```

## Environment Variables

```
POSTGRES_USER=taskuser
POSTGRES_PASSWORD=taskpass
POSTGRES_DB=taskengine
POSTGRES_HOST=db
POSTGRES_PORT=5432
REDIS_URL=redis://redis:6379
APP_PORT=8000
```
