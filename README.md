# Todo List App

Full-stack todo application with due date reminders. Built as a Lennar engineering interview exercise.

## Stack

- **Backend:** Python / FastAPI / SQLAlchemy / APScheduler
- **Frontend:** React (Vite)
- **Database:** SQLite

---

## Running Locally

### 1. Backend

```bash
cd backend

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and set a real SECRET_KEY value

# Start the server
uvicorn app.main:app --reload
```

Backend runs at `http://localhost:8000`.
Auto-generated API docs available at `http://localhost:8000/docs`.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`.

### 3. Database

No setup required. SQLite database files (`todo.db`, `scheduler.db`) are created automatically on first run.

### 4. Running Tests

```bash
cd backend
source venv/bin/activate
pytest tests/ -v
```

---

## Architecture

### Backend Framework: FastAPI

FastAPI handles routing, request validation, and auth middleware. Route handlers are organized by resource (`auth`, `todos`, `notifications`) using `APIRouter` — the same separation-of-concerns you'd apply in a Rails controller structure. Pydantic schemas define what shape data is accepted and returned, functioning like Rails strong params and serializers combined.

### Database: SQLAlchemy + SQLite

SQLAlchemy is used as the ORM with SQLite as the database. Rather than introducing Alembic for migrations, the schema is created on startup via `Base.metadata.create_all()`. This is appropriate for a locally-run exercise with a fixed schema. In production I would use Alembic migrations (the Python equivalent of `rails db:migrate`).

SQLite was chosen over PostgreSQL specifically to eliminate local setup friction. The only trade-off is that SQLite has limited concurrency under write-heavy load — not a concern at this scale.

### Authentication: JWT + bcrypt

On login, the server issues a signed JWT token. The client stores it in `localStorage` and sends it as a `Bearer` header on subsequent requests. A FastAPI `Depends()` guard decodes and validates the token on every protected route — equivalent to `before_action :authenticate_user!` in Rails.

Passwords are hashed with bcrypt directly. Raw passwords are never stored or logged.

### Reminder System: APScheduler

When a todo is created or updated with a due date, a background job is scheduled using APScheduler's `BackgroundScheduler`. The job runs outside the request cycle — the HTTP response returns immediately and the reminder fires separately.

**Timing:** Jobs fire 24 hours before the due date. If the due date is already within 24 hours, the job fires 15 seconds after scheduling (for local demo visibility).

**Persistence:** APScheduler is configured with a SQLite-backed job store (`scheduler.db`). This means scheduled jobs survive application restarts — the scheduler reloads them automatically on startup.

**Race condition handling:** Each todo's reminder job uses `reminder_{todo_id}` as its job ID, combined with `replace_existing=True`. This makes scheduling idempotent — if a due date changes, the existing job is atomically replaced rather than duplicated. No separate deduplication logic is needed.

**Failure handling:** The job function re-checks the todo's current state before acting. If the todo was deleted or marked complete after the job was scheduled, the job exits silently without creating a notification. Failures are logged with enough context to diagnose.

**Production note:** For a production system I would replace APScheduler with Celery + Redis — a dedicated worker process with a proper message broker. APScheduler running in-process is simpler for local development but ties job execution to the web process lifetime. The Celery equivalent in the Rails world is Sidekiq + Redis.

### Frontend

React with Vite. Auth state is held in React context backed by `localStorage`. The dashboard polls the API every 10 seconds to surface new notifications as reminder jobs complete. All API calls are centralized in `src/api.js`. Notifications can be marked as read via `PATCH /api/notifications/{id}/read`, which the frontend uses to distinguish new vs already-seen items. Successful registration immediately logs the user in (no redundant login step). Delete requires a confirmation prompt. Notifications are displayed at the top of the dashboard and rendered in local time.

---

## AI Usage

This project was built with Claude Code (Anthropic) as the primary AI tool.

### Where AI assisted

- Initial scaffolding of FastAPI project structure and boilerplate (models, schemas, routers)
- APScheduler configuration and job store setup
- JWT auth implementation pattern
- React component structure and wiring

### Where I made different choices than AI suggested

- **No Alembic.** Claude's initial suggestion included Alembic for migrations. I pushed back — for a locally-run SQLite exercise with no schema evolution needed, `create_all()` is simpler and easier to explain. Using Alembic here would add complexity without adding value.

- **APScheduler over Celery.** The default AI suggestion trended toward Celery + Redis as the "correct" background job answer. I chose APScheduler specifically because it eliminates the Redis dependency for local setup, and the persistent job store still satisfies the spec's restart-recovery requirement. The trade-off is documented and I can defend it.

- **No router-level class structure.** AI initially suggested class-based route organization. I kept it as flat functions — easier to read and explain in an interview context, and there's no complexity here that warrants the abstraction.

### Bugs caught during end-to-end testing

Three bugs surfaced while running the app locally for the first time — each found through actual execution, not static analysis:

1. **`passlib` incompatible with Python 3.13 + bcrypt 4.x** — `passlib` ships a bcrypt wrap-detection routine that fails with the newer `bcrypt` library under Python 3.13. Fixed by removing `passlib` entirely and calling the `bcrypt` library directly. The interface is identical; `passlib` was just an unnecessary wrapper.

2. **APScheduler scheduled jobs in local time instead of UTC** — `datetime.utcnow()` returns a naive datetime (no timezone info). APScheduler interprets naive datetimes as local time. On a machine set to UTC-6, this caused every job to be scheduled 6 hours later than intended. Fixed by pinning the scheduler to UTC (`timezone="UTC"`) and switching all datetime calls to `datetime.now(timezone.utc)`.

3. **Deleting a todo raised a NOT NULL constraint error** — SQLAlchemy's default cascade behaviour tries to null out foreign keys on child records before deleting the parent. Since `notifications.todo_id` was non-nullable, this crashed with an integrity error. The correct fix (per the spec, which says notifications should remain as history) was to make `todo_id` nullable with `ondelete="SET NULL"`, so the notification record is preserved but the link to the deleted todo is cleared.

A second pass of end-to-end testing surfaced additional issues fixed before submission:

1. **`datetime.utcnow()` is deprecated in Python 3.12+** — Used throughout models, auth, and tests. Replaced with `datetime.now(timezone.utc)` everywhere. SQLAlchemy column defaults require a callable, so these were wrapped in a `_utcnow` helper rather than called inline.

2. **Clearing a todo's due date via PUT silently failed** — The update logic used `body.due_date is not None` to detect a change, which meant sending `due_date: null` was indistinguishable from omitting the field entirely. The scheduled reminder was never cancelled. Fixed by checking `"due_date" in body.model_fields_set` (Pydantic tracks which fields were explicitly included in the request), so an explicit null correctly triggers `cancel_reminder()`.

### Human architectural decisions

- Chose SQLite over PostgreSQL to keep local setup to a single command
- Decided reminder timing (24h before due date, 15s fallback for demo) rather than accepting a generic suggestion
- Chose `replace_existing=True` on APScheduler jobs as the explicit race condition solution rather than a separate lock/dedup table
- Kept the frontend deliberately minimal — this is not a design exercise
- Chose a compound index on `(user_id, created_at)` over a simple `user_id` index — covers the common `list_todos` query pattern and makes the `ORDER BY created_at DESC` free, without needing a separate index for sorting
- Chose `model_fields_set` to detect an explicit `null` on `due_date` during PUT — a `None`-check alone can't distinguish "field was omitted" from "field was explicitly cleared", which matters for cancelling the scheduled reminder correctly
- Auto-login after registration rather than redirecting to the login page — user already provided their credentials, making them type again is unnecessary friction
- Notifications surfaced at the top of the dashboard rather than the bottom — a reminder is time-sensitive and should be the first thing a user sees
- Delete requires a browser confirmation prompt — destructive action with no undo, the extra click is worth it
