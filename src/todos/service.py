from datetime import datetime, timezone
from uuid import uuid4, UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException
from . import models
from src.auth.models import TokenData
from src.entities.todo import Todo
from src.exceptions import TodoCreationError, TodoNotFoundError
import logging

def create_todo(current_user: TokenData, db: Session, todo: models.TodoCreate) -> Todo:
    try:
        new_todo = Todo(**todo.model_dump())
        new_todo.user_id = current_user.get_uuid()
        db.add(new_todo)
        db.commit()
        db.refresh(new_todo)
        logging.info(f"Created new todo for user: {current_user.get_uuid()}")
        return new_todo
    except Exception as e:
        logging.error(f"Failed to create todo for user {current_user.get_uuid()}. Error: {str(e)}")
        raise TodoCreationError(str(e))


def get_todos(current_user: TokenData, db: Session) -> list[models.TodoResponse]:
    todos = db.query(Todo).filter(Todo.user_id == current_user.get_uuid()).all()
    logging.info(f"Retrieved {len(todos)} todos for user: {current_user.get_uuid()}")
    return todos


def get_todo_by_id(current_user: TokenData, db: Session, todo_id: UUID) -> Todo:
    todo = db.query(Todo).filter(Todo.id == todo_id).filter(Todo.user_id == current_user.get_uuid()).first()
    if not todo:
        logging.warning(f"Todo {todo_id} not found for user {current_user.get_uuid()}")
        raise TodoNotFoundError(todo_id)
    logging.info(f"Retrieved todo {todo_id} for user {current_user.get_uuid()}")
    return todo


def update_todo(current_user: TokenData, db: Session, todo_id: UUID, todo_update: models.TodoCreate) -> Todo:
    todo_data = todo_update.model_dump(exclude_unset=True)
    db.query(Todo).filter(Todo.id == todo_id).filter(Todo.user_id == current_user.get_uuid()).update(todo_data)
    db.commit()
    logging.info(f"Successfully updated todo {todo_id} for user {current_user.get_uuid()}")
    return get_todo_by_id(current_user, db, todo_id)

def complete_todo(current_user: TokenData, db: Session, todo_id: UUID) -> Todo:
    todo = get_todo_by_id(current_user, db, todo_id)
    if todo.is_completed:
        logging.debug(f"Todo {todo_id} is already completed")
        return todo
    todo.is_completed = True
    todo.completed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(todo)
    logging.info(f"Todo {todo_id} marked as completed by user {current_user.get_uuid()}")
    return todo


def delete_todo(current_user: TokenData, db: Session, todo_id: UUID) -> None:
    todo = get_todo_by_id(current_user, db, todo_id)
    db.delete(todo)
    db.commit()
    logging.info(f"Todo {todo_id} deleted by user {current_user.get_uuid()}")
