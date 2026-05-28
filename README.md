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

FastAPI handles routing, request validation, and auth middleware. Route handlers are organized by resource (`auth`, `todos`, `notifications`) using `APIRouter`. Pydantic schemas define what shape data is accepted and returned.

### Database: SQLAlchemy + SQLite

SQLAlchemy is used as the ORM with SQLite as the database. Rather than introducing Alembic for migrations, the schema is created on startup via `Base.metadata.create_all()`. This is appropriate for a locally-run exercise with a fixed schema. In production, I would use Alembic migrations with PostgreSQL.

SQLite was chosen over PostgreSQL specifically to eliminate local setup friction. The only trade-off is that SQLite has limited concurrency under write-heavy load — not a concern at this scale.  In production, we would switch to PostgreSQL with Celery for better performance and reliability under concurrent access.

### Authentication: JWT + bcrypt

On login, the server issues a signed JWT token. The client stores it in `localStorage` and sends it as a `Bearer` header on subsequent requests. A FastAPI `Depends()` guard decodes and validates the token on every protected route.

Passwords are hashed with bcrypt directly. Raw passwords are never stored or logged.

### Reminder System: APScheduler

When a todo is created or updated with a due date, a background job is scheduled using APScheduler's `BackgroundScheduler`. The job runs outside the request cycle — the HTTP response returns immediately and the reminder fires separately in the background.

**Timing:** Jobs fire 24 hours before the due date. If the due date is already within 24 hours, the job fires 3 seconds after scheduling (for local demo visibility).

**Persistence:** APScheduler is configured with a SQLite-backed job store (`scheduler.db`). This means scheduled jobs survive application restarts — the scheduler reloads them automatically on startup. Jobs are configured with `misfire_grace_time=None` so that any job whose scheduled time passed while the server was down fires immediately on restart, rather than being silently discarded by APScheduler's default 1-second grace window.

**Race condition handling:** Each todo's reminder job uses `reminder_{todo_id}` as its job ID, combined with `replace_existing=True`. This makes scheduling idempotent — if a due date changes, the existing job is atomically replaced rather than duplicated. No separate deduplication logic is needed.

**Failure handling:** The job function re-checks the todo's current state before acting. If the todo was deleted or marked complete after the job was scheduled, the job exits silently without creating a notification.

**Production note:** For a production system I would replace APScheduler with Celery + Redis — a dedicated worker process with a proper message broker. APScheduler running in-process is simpler for local development but ties job execution to the web process lifetime.

### Frontend

React with Vite. The frontend is intentionally minimal — this is not a design exercise — but several deliberate architectural choices are worth noting.

**Auth state via React Context.** `AuthContext` holds the JWT token and exposes `login`/`logout` to any component via `useAuth()`, without prop drilling. Token is initialized from `localStorage` so page refreshes don't log the user out. Global auth state without adding Redux as a dependency.

**Centralized API layer.** All network calls go through a single `request()` function in `src/api.js` that handles auth headers, JSON serialization, error throwing, and the 204 no-content edge case. No raw `fetch` calls are scattered across components.

**Polling for async results.** The dashboard runs `setInterval` every 10 seconds to surface notifications as background reminder jobs complete. `useCallback` + `useEffect` + `clearInterval` on cleanup is the correct React pattern — no memory leaks on unmount.

**Optimistic local state on mark-read.** Dismissing a notification updates local state in-place rather than refetching everything from the server, avoiding an unnecessary round-trip.

Additional decisions: successful registration immediately logs the user in (no redundant login step); notifications are displayed at the top of the dashboard since reminders are time-sensitive; delete requires a browser confirmation prompt since it's a destructive action with no undo.

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

- **APScheduler over Celery.** The default AI suggestion trended toward Celery + Redis as the "correct" background job answer. I chose APScheduler specifically because it eliminates the Redis dependency for local setup, and the persistent job store still satisfies the spec's restart-recovery requirement.

- **No router-level class structure.** AI initially suggested class-based route organization. I kept it as flat functions — easier to read and explain in an interview context, and there's no complexity here that warrants the abstraction.

### Bugs caught during end-to-end testing

Three bugs surfaced while running the app locally for the first time — each found through actual execution, not static analysis:

1. **`passlib` incompatible with Python 3.13 + bcrypt 4.x** — `passlib` ships a bcrypt wrap-detection routine that fails with the newer `bcrypt` library under Python 3.13. Fixed by removing `passlib` entirely and calling the `bcrypt` library directly. The interface is identical; `passlib` was just an unnecessary wrapper.

2. **APScheduler scheduled jobs in local time instead of UTC** — `datetime.utcnow()` returns a naive datetime (no timezone info). APScheduler interprets naive datetimes as local time. On a machine set to UTC-6, this caused every job to be scheduled 6 hours later than intended. Fixed by pinning the scheduler to UTC (`timezone="UTC"`) and switching all datetime calls to `datetime.now(timezone.utc)`.

3. **Deleting a todo raised a NOT NULL constraint error** — SQLAlchemy's default cascade behaviour tries to null out foreign keys on child records before deleting the parent. Since `notifications.todo_id` was non-nullable, this crashed with an integrity error. Initially fixed with `ondelete="SET NULL"` to preserve notification history — later revised (see human decisions) to cascade-delete notifications with their todo instead.

A second pass of end-to-end testing surfaced additional issues fixed before submission:

1. **`datetime.utcnow()` is deprecated in Python 3.12+** — Used throughout models, auth, and tests. Replaced with `datetime.now(timezone.utc)` everywhere. SQLAlchemy column defaults require a callable, so these were wrapped in a `_utcnow` helper rather than called inline.

2. **Clearing a todo's due date via PUT silently failed** — The update logic used `body.due_date is not None` to detect a change, which meant sending `due_date: null` was indistinguishable from omitting the field entirely. The scheduled reminder was never cancelled. Fixed by checking `"due_date" in body.model_fields_set` (Pydantic tracks which fields were explicitly included in the request), so an explicit null correctly triggers `cancel_reminder()`.

### Human architectural decisions

- Chose `replace_existing=True` on APScheduler jobs as the explicit race condition solution — using the todo ID as the job ID makes scheduling idempotent; editing a due date atomically replaces the existing job rather than risking duplicates or requiring a separate lock/dedup table
- Set `misfire_grace_time=None` on all scheduled jobs — APScheduler's default 1-second grace window silently discards jobs whose run time passed while the server was down; `None` ensures they always fire on restart regardless of delay
- Chose `model_fields_set` to detect an explicit `null` on `due_date` during PUT — a `None`-check alone can't distinguish "field was omitted" from "field was explicitly cleared", which matters for correctly cancelling the scheduled reminder
- Added compound index `(user_id, created_at)` on both `todos` and `notifications` — covers the common list query pattern and makes `ORDER BY created_at DESC` free without a separate index. Also added a `todo_id` index on `notifications` so SQLAlchemy's cascade-delete lookup doesn't full-scan the table
- Notifications cascade-delete with their todo — a reminder for a deleted todo is noise, not useful history. The due date is stored directly on the notification record so it's available at fire time, independent of the todo's lifecycle
- Chose SQLite over PostgreSQL to keep local setup to a single command; the only trade-off is write concurrency under load, which doesn't apply at this scale
- Chose APScheduler over Celery — eliminates the Redis dependency for local setup, and the SQLite-backed job store satisfies the restart-recovery requirement. Documented trade-off: in production, Celery + Redis provides worker isolation and built-in retry
- Decided reminder timing (24h before due date, 3s fallback for demo) — the fallback makes the reminder flow observable in a demo session without waiting a day
- Due dates are stored as UTC midnight and displayed with `timeZone: "UTC"` — treats the date as timezone-invariant so the same calendar date is shown regardless of where the app is viewed
- Auto-login after registration — user already provided credentials, redirecting to the login page to type them again is unnecessary friction
- Notifications surfaced at the top of the dashboard — a reminder is time-sensitive and should be the first thing a user sees
- Delete requires a browser confirmation prompt — destructive action with no undo, the extra click is worth it
- Kept the frontend deliberately minimal — this is not a design exercise
