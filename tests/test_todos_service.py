import pytest
from uuid import uuid4
from src.todos import service as todos_service
from src.todos.models import TodoCreate
from src.exceptions import TodoNotFoundError
from src.entities.todo import Todo

class TestTodosService:
    def test_create_todo(self, db_session, test_token_data):
        todo_create = TodoCreate(
            description="New Description"
        )
        
        new_todo = todos_service.create_todo(test_token_data, db_session, todo_create)
        assert new_todo.description == "New Description"
        assert new_todo.user_id == test_token_data.get_uuid()
        assert not new_todo.is_completed

    def test_get_todos(self, db_session, test_token_data, test_todo):
        test_todo.user_id = test_token_data.get_uuid()
        db_session.add(test_todo)
        db_session.commit()
        
        todos = todos_service.get_todos(test_token_data, db_session)
        assert len(todos) == 1
        assert todos[0].id == test_todo.id

    def test_get_todo_by_id(self, db_session, test_token_data, test_todo):
        test_todo.user_id = test_token_data.get_uuid()
        db_session.add(test_todo)
        db_session.commit()
        
        todo = todos_service.get_todo_by_id(test_token_data, db_session, test_todo.id)
        assert todo.id == test_todo.id
        
        with pytest.raises(TodoNotFoundError):
            todos_service.get_todo_by_id(test_token_data, db_session, uuid4())

    def test_complete_todo(self, db_session, test_token_data, test_todo):
        test_todo.user_id = test_token_data.get_uuid()
        db_session.add(test_todo)
        db_session.commit()
        
        completed_todo = todos_service.complete_todo(test_token_data, db_session, test_todo.id)
        assert completed_todo.is_completed
        assert completed_todo.completed_at is not None

    def test_delete_todo(self, db_session, test_token_data, test_todo):
        test_todo.user_id = test_token_data.get_uuid()
        db_session.add(test_todo)
        db_session.commit()
        
        todos_service.delete_todo(test_token_data, db_session, test_todo.id)
        assert db_session.query(Todo).filter_by(id=test_todo.id).first() is None 