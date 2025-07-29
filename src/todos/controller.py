from fastapi import APIRouter, status
from typing import List
from uuid import UUID

from ..database.core import DbSession
from . import  models
from . import service
from ..auth.service import CurrentUser

router = APIRouter(
    prefix="/todos",
    tags=["Todos"]
)

@router.post("/", response_model=models.TodoResponse, status_code=status.HTTP_201_CREATED)
def create_todo(db: DbSession, todo: models.TodoCreate, current_user: CurrentUser):
    return service.create_todo(current_user, db, todo)


@router.get("/", response_model=List[models.TodoResponse])
def get_todos(db: DbSession, current_user: CurrentUser):
    return service.get_todos(current_user, db)


@router.get("/{todo_id}", response_model=models.TodoResponse)
def get_todo(db: DbSession, todo_id: UUID, current_user: CurrentUser):
    return service.get_todo_by_id(current_user, db, todo_id)


@router.put("/{todo_id}", response_model=models.TodoResponse)
def update_todo(db: DbSession, todo_id: UUID, todo_update: models.TodoCreate, current_user: CurrentUser):
    return service.update_todo(current_user, db, todo_id, todo_update)


@router.put("/{todo_id}/complete", response_model=models.TodoResponse)
def complete_todo(db: DbSession, todo_id: UUID, current_user: CurrentUser):
    return service.complete_todo(current_user, db, todo_id)


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(db: DbSession, todo_id: UUID, current_user: CurrentUser):
    service.delete_todo(current_user, db, todo_id)
