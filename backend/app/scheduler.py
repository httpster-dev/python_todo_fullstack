from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from datetime import datetime, timedelta, timezone
import logging

from .database import SessionLocal
from . import models

logger = logging.getLogger(__name__)

# SQLite-backed job store means scheduled jobs survive app restarts.
# This is the key difference from an in-memory scheduler — comparable to
# Sidekiq's Redis persistence.
jobstores = {
    "default": SQLAlchemyJobStore(url="sqlite:///./scheduler.db")
}

scheduler = BackgroundScheduler(jobstores=jobstores, timezone="UTC")


def send_reminder(todo_id: int):
    """
    Executed by the scheduler outside the request cycle.
    Always re-checks todo state before acting — handles the case where
    a todo was completed or deleted after the job was scheduled.
    """
    db = SessionLocal()
    try:
        todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()

        if not todo:
            logger.info(f"Reminder skipped: todo {todo_id} deleted before job ran")
            return

        if todo.completed:
            logger.info(f"Reminder skipped: todo {todo_id} already completed")
            return

        existing = db.query(models.Notification).filter_by(
            todo_id=todo.id, status="sent"
        ).first()
        if existing:
            logger.info(f"Reminder skipped: unread notification already exists for todo {todo_id}")
            todo.reminder_scheduled = False
            db.commit()
            return

        notification = models.Notification(
            user_id=todo.user_id,
            todo_id=todo.id,
            due_date=todo.due_date,
            message=f"Reminder: '{todo.title}' is due soon",
            status="sent",
        )
        db.add(notification)
        todo.reminder_scheduled = False
        db.commit()
        logger.info(f"Notification created for todo {todo_id}: {todo.title}")

    except Exception as e:
        db.rollback()
        logger.error(f"Reminder job failed for todo {todo_id}: {e}")
    finally:
        db.close()


def schedule_reminder(todo_id: int, due_date: datetime):
    """
    Schedule a reminder job. Using todo_id as the job ID ensures only one
    reminder exists per todo at a time — calling this again on the same todo
    replaces the existing job, which handles rescheduling without duplicates.
    """
    # SQLite returns naive datetimes — attach UTC so comparisons are consistent
    if due_date.tzinfo is None:
        due_date = due_date.replace(tzinfo=timezone.utc)

    run_at = due_date - timedelta(hours=24)
    if run_at <= datetime.now(timezone.utc):
        # Due date is within 24 hours (or past) — fire soon for demo visibility
        run_at = datetime.now(timezone.utc) + timedelta(seconds=3)

    scheduler.add_job(
        send_reminder,
        trigger="date",
        run_date=run_at,
        args=[todo_id],
        id=f"reminder_{todo_id}",
        replace_existing=True,  # atomic replace — prevents duplicate jobs
        misfire_grace_time=None,  # always fire after a restart, no matter how late
    )
    logger.info(f"Reminder scheduled for todo {todo_id} at {run_at} UTC")


def cancel_reminder(todo_id: int):
    job_id = f"reminder_{todo_id}"
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
        logger.info(f"Reminder cancelled for todo {todo_id}")
