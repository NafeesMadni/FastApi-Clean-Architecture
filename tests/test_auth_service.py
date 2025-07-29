import pytest
from datetime import timedelta
from uuid import uuid4
from src.auth import service as auth_service
from src.auth.models import RegisterUserRequest
from src.exceptions import AuthenticationError
from fastapi.security import OAuth2PasswordRequestForm
from src.entities.user import User

class TestAuthService:
    def test_verify_password(self):
        password = "password123"
        hashed = auth_service.get_password_hash(password)
        assert auth_service.verify_password(password, hashed)
        assert not auth_service.verify_password("wrongpassword", hashed)

    def test_authenticate_user(self, db_session, test_user):
        db_session.add(test_user)
        db_session.commit()
        
        user = auth_service.authenticate_user("test@example.com", "password123", db_session)
        assert user is not False
        assert user.email == test_user.email

    def test_login_for_access_token(self, db_session, test_user):
        db_session.add(test_user)
        db_session.commit()

        class FormData:
            def __init__(self):
                self.username = "test@example.com"
                self.password = "password123"
                self.scope = ""
                self.client_id = None
                self.client_secret = None
        
        form_data = FormData()
        token = auth_service.login_for_access_token(form_data, db_session)
        assert token.token_type == "bearer"
        assert token.access_token is not None

@pytest.mark.asyncio
async def test_register_user(db_session):
    request = RegisterUserRequest(
        email="new@example.com",
        password="password123",
        first_name="New",
        last_name="User"
    )
    auth_service.register_user(db_session, request)
    
    user = db_session.query(User).filter_by(email="new@example.com").first()
    assert user is not None
    assert user.email == "new@example.com"
    assert user.first_name == "New"
    assert user.last_name == "User"

def test_create_and_verify_token(db_session):
    user_id = uuid4()
    token = auth_service.create_access_token("test@example.com", user_id, timedelta(minutes=30))
    
    token_data = auth_service.verify_token(token)
    assert token_data.get_uuid() == user_id

    # Test invalid credentials
    assert auth_service.authenticate_user("test@example.com", "wrongpassword", db_session) is False

    with pytest.raises(AuthenticationError):
        form_data = OAuth2PasswordRequestForm(
            username="test@example.com",
            password="wrongpassword",
            scope=""
        )
        auth_service.login_for_access_token(form_data, db_session) 