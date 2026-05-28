# Full-Stack Interview Exercise
## Todo List Application with Due Date Reminders

---

## Objective

Build a full-stack application that demonstrates thoughtful use of AI, solid engineering fundamentals, and understanding of when to apply AI vs. critical thinking.

---

## The Task

Build a todo list app. Users can create an account, log in, create todos, mark them complete, edit them, and delete them. Todos can have optional due dates, and the system should schedule background reminder notifications when a due date is approaching.

---

## Core Features

- User registration and login
- Create, read, update, delete todos
- Mark todos as complete
- Todos persist in a database
- Each user only sees their own todos
- Functional UI (not a design competition)

---

## Due Date Reminders

Each todo can optionally have a due date. When a todo is created or updated with a due date, schedule a background reminder job. The job can simulate sending a notification (write to a notifications table, log, or in-app notification center). No real email or SMS integration needed.

This forces you to think about how to run work outside the request/response cycle, handle failures, manage state, and avoid race conditions.

---

## Tech Stack

- **Backend:** Python
- **Frontend:** React
- **Database:** PostgreSQL or SQLite
- Must run locally

---

## What You Need to Submit

### Code
- Working backend and frontend
- Proper error handling
- Input validation
- Tests for at least one critical path

### Documentation
- `README.md`: How to run the app locally
- Explanation of how you built it and how you used AI

---

## What We're Testing

- **AI Judgment** — Can you use AI effectively without just transcribing its output?
- **Understanding** — Do you know what your code does?
- **Fundamentals** — Authentication, database design, API structure, state management, async patterns, background jobs
- **Production Mindset** — Error handling, validation, security, concurrency, reliability, architecture tradeoffs

---

## Time

Typical submission takes 2–4 hours. If you're past 5 hours, scope back and document what you'd do next. A complete simple solution beats an incomplete ambitious one.

---

## Using AI

You can use any AI tool (Claude, Copilot, ChatGPT, etc.). Be honest about it in your README and explain where you made different choices than what AI suggested.

The goal is to see how you work with AI, not whether you used it.

---

## Interview

90 minutes. We'll walk through your code and approach. We'll ask questions about your decisions and go deep where it makes sense.

---

## What Disqualifies You

- You can't explain your own code
- No clear reasoning for your architecture
- Security issues (hardcoded secrets, SQL injection, etc.)
- You treat AI output as gospel
- No tests or validation
- App doesn't run

---

## Submission

- Git repo
- README with setup instructions
- Explanation of your approach and AI usage
- Don't include `node_modules`, `__pycache__`, or `.env`