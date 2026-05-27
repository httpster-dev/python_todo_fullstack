# Feature Request: Todo List Application with Due Date Reminders

## Overview

Build a full-stack todo list application demonstrating:

- Full-stack engineering fundamentals
- Authentication and authorization
- Database persistence
- Background job processing
- Basic reliability considerations
- Thoughtful AI-assisted development practices

Application should run locally and remain intentionally scoped to fit interview expectations.

---

# Functional Requirements

## Authentication

### User Registration

Users can create an account by providing:

- Email address
- Password

Requirements:

- Validate required fields
- Prevent duplicate accounts
- Store passwords securely (hashed)
- Return appropriate validation errors

### User Login

Users can log in using:

- Email
- Password

Requirements:

- Authenticate credentials
- Return session token / authentication state
- Reject invalid credentials
- Protect authenticated routes

---

## Todo Management

Authenticated users can:

### Create Todo

Todo fields:

- Title (required)
- Description (optional)
- Due date (optional)
- Completion state

Validation:

- Title cannot be empty
- Due date must be valid datetime format if provided

### View Todos

Users can:

- View all todos belonging only to themselves
- See:
  - Title
  - Description
  - Completion status
  - Due date
  - Reminder status (if applicable)

### Update Todo

Users can edit:

- Title
- Description
- Due date
- Completion state

Behavior:

- Updating due date should update reminder scheduling
- Completed items should remain editable

### Delete Todo

Users can remove todos.

Behavior:

- Associated reminders should not execute after deletion
- Related notification records may remain for history

### Mark Complete

Users can:

- Toggle completion status

Behavior:

- Reminder system should verify completion state before generating notifications

---

# Reminder System

## Reminder Scheduling

When:

- Todo is created with a due date
- Todo due date changes

System should:

1. Persist todo
2. Schedule background reminder work
3. Execute reminder outside request cycle

Reminder execution may:

- Insert notification record
- Write log entry
- Display in-app notification

No external integrations required:

- No email
- No SMS
- No push notifications

---

## Reminder Rules

Reminder job should:

- Check current todo state before notification
- Avoid notifying completed todos
- Avoid duplicate notifications where possible

Recommended handling:

- Rebuild reminder state after application restart
- Persist notification state

## Race Conditions

The reminder system must handle concurrent scenarios:

- Two requests updating a todo's due date simultaneously should not result in double-scheduled reminders
- Cancel/reschedule operations must be atomic where possible
- Use database-level constraints or locking to prevent duplicate notification records

## Background Job Failure Handling

The reminder system should account for failures:

- Log failures with enough context to diagnose
- Avoid silent swallowing of errors
- Define a clear policy: retry, skip, or dead-letter on failure
- Ensure a failed reminder does not leave the system in an inconsistent state (e.g., scheduled but never executed without record)

---

# Authorization Rules

Users must only access:

- Their own todos
- Their own notifications
- Their own reminder state

Forbidden:

- Viewing another user's data
- Updating another user's todos
- Deleting another user's records

---

# Persistence Layer

Database options:

- SQLite (preferred for local simplicity)
OR
- PostgreSQL

Suggested entities:

## Users

Fields:

- id
- email
- password_hash
- created_at

## Todos

Fields:

- id
- user_id
- title
- description
- completed
- due_date
- reminder_scheduled_at
- created_at
- updated_at

## Notifications

Fields:

- id
- user_id
- todo_id
- message
- status
- created_at

---

# Frontend Requirements

Technology:

- React

UI expectations:

- Functional over visual polish

Required screens:

## Registration

- Email field
- Password field
- Submit action

## Login

- Email field
- Password field
- Submit action

## Todo Dashboard

Display:

- Todo list
- Completion state
- Due dates
- Edit actions
- Delete actions
- Reminder / notification history

Actions:

- Create todo
- Edit todo
- Mark complete
- Delete todo

---

# Backend Requirements

Technology:

- Python

Responsibilities:

- Authentication
- CRUD endpoints
- Validation
- Reminder scheduling
- Notification persistence
- Error handling

Suggested API areas:

- Auth endpoints
- Todo endpoints
- Notification endpoints

---

# Validation Requirements

Required:

- Input validation
- Authentication checks
- Ownership enforcement
- Error responses

Examples:

- Empty title rejection
- Invalid login rejection
- Unauthorized access rejection
- Invalid due date rejection

## Security Requirements

- Use parameterized queries or an ORM — no raw string interpolation in SQL (SQL injection prevention)
- Store secrets (JWT secret, DB credentials) in environment variables, never hardcoded
- Do not commit `.env` files; provide a `.env.example` instead
- Passwords must be hashed (e.g., bcrypt) — never stored in plaintext

---

# Testing Requirements

Provide tests for at least one critical path.

Recommended critical path:

Create todo with due date:

Create Todo
→ Persist Todo
→ Schedule Reminder
→ Execute Reminder
→ Create Notification

Testing goals:

- Persistence works
- Reminder flow works
- Notification created correctly

---

# Documentation Deliverables

README should include:

## Setup

- Backend install instructions
- Frontend install instructions
- Database setup
- Local run steps

## Architecture Notes

Describe:

- Backend framework choices
- Reminder implementation approach
- Database decisions
- Tradeoffs made

## AI Usage

Document:

- Tools used
- Areas AI assisted
- Places where implementation differed from AI suggestions — be specific about what AI suggested and why you chose differently
- Human architectural decisions made without or against AI guidance
- Any cases where AI output was wrong, incomplete, or required correction

---

# Non-Goals

Avoid unnecessary complexity:

Do NOT include:

- Email integration
- SMS integration
- Microservices
- Distributed queues
- Complex orchestration
- Advanced styling
- External notification providers
- Production deployment setup

Goal:

Deliver complete, understandable, locally runnable software with clear reasoning and solid engineering fundamentals.
