"""
Critical path test: create todo with due date → reminder fires → notification created.
Also covers: completed todo skip, deleted todo skip.
"""
import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app import models
from app.scheduler import send_reminder

engine = create_engine("sqlite:///./test.db", connect_args={"check_same_thread": False})
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def user(db):
    u = models.User(email="test@example.com", password_hash="hashed")
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


def test_reminder_creates_notification(db, user):
    todo = models.Todo(
        user_id=user.id,
        title="Finish report",
        due_date=datetime.now(timezone.utc) + timedelta(hours=1),
    )
    db.add(todo)
    db.commit()
    db.refresh(todo)

    with patch("app.scheduler.SessionLocal", return_value=db):
        send_reminder(todo.id)

    notification = db.query(models.Notification).filter_by(todo_id=todo.id).first()
    assert notification is not None
    assert "Finish report" in notification.message
    assert notification.status == "sent"
    assert todo.reminder_scheduled is False


def test_reminder_skips_completed_todo(db, user):
    todo = models.Todo(
        user_id=user.id,
        title="Already done",
        completed=True,
        due_date=datetime.now(timezone.utc) + timedelta(hours=1),
    )
    db.add(todo)
    db.commit()
    db.refresh(todo)

    with patch("app.scheduler.SessionLocal", return_value=db):
        send_reminder(todo.id)

    assert db.query(models.Notification).filter_by(todo_id=todo.id).count() == 0


def test_reminder_skips_deleted_todo(db, user):
    with patch("app.scheduler.SessionLocal", return_value=db):
        send_reminder(9999)

    assert db.query(models.Notification).count() == 0
