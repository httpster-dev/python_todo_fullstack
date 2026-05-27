from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas
from ..auth import get_current_user
from ..database import get_db
from ..scheduler import schedule_reminder, cancel_reminder

router = APIRouter(prefix="/api/todos", tags=["todos"])


@router.get("", response_model=List[schemas.TodoResponse])
def list_todos(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return (
        db.query(models.Todo)
        .filter(models.Todo.user_id == current_user.id)
        .order_by(models.Todo.created_at.desc())
        .all()
    )


@router.post("", response_model=schemas.TodoResponse, status_code=201)
def create_todo(
    body: schemas.TodoCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if not body.title.strip():
        raise HTTPException(status_code=422, detail="Title cannot be empty")

    todo = models.Todo(
        user_id=current_user.id,
        title=body.title.strip(),
        description=body.description,
        due_date=body.due_date,
    )
    db.add(todo)
    db.commit()
    db.refresh(todo)

    if todo.due_date:
        schedule_reminder(todo.id, todo.due_date)
        todo.reminder_scheduled = True
        db.commit()

    return todo


@router.put("/{todo_id}", response_model=schemas.TodoResponse)
def update_todo(
    todo_id: int,
    body: schemas.TodoUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    todo = db.query(models.Todo).filter(
        models.Todo.id == todo_id,
        models.Todo.user_id == current_user.id,
    ).first()

    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    if body.title is not None:
        if not body.title.strip():
            raise HTTPException(status_code=422, detail="Title cannot be empty")
        todo.title = body.title.strip()

    if body.description is not None:
        todo.description = body.description

    if body.completed is not None:
        todo.completed = body.completed

    due_date_changed = "due_date" in body.model_fields_set and body.due_date != todo.due_date
    if due_date_changed:
        todo.due_date = body.due_date

    db.commit()
    db.refresh(todo)

    if due_date_changed:
        if todo.due_date:
            schedule_reminder(todo.id, todo.due_date)
            todo.reminder_scheduled = True
        else:
            cancel_reminder(todo.id)
            todo.reminder_scheduled = False
        db.commit()

    return todo


@router.delete("/{todo_id}", status_code=204)
def delete_todo(
    todo_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    todo = db.query(models.Todo).filter(
        models.Todo.id == todo_id,
        models.Todo.user_id == current_user.id,
    ).first()

    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    cancel_reminder(todo.id)
    db.delete(todo)
    db.commit()
