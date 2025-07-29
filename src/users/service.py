from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException
from . import models
from src.entities.user import User
from src.exceptions import UserNotFoundError, InvalidPasswordError, PasswordMismatchError
from src.auth.service import verify_password, get_password_hash
import logging


def get_user_by_id(db: Session, user_id: UUID) -> models.UserResponse:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logging.warning(f"User not found with ID: {user_id}")
        raise UserNotFoundError(user_id)
    logging.info(f"Successfully retrieved user with ID: {user_id}")
    return user


def change_password(db: Session, user_id: UUID, password_change: models.PasswordChange) -> None:
    try:
        user = get_user_by_id(db, user_id)
        
        # Verify current password
        if not verify_password(password_change.current_password, user.password_hash):
            logging.warning(f"Invalid current password provided for user ID: {user_id}")
            raise InvalidPasswordError()
        
        # Verify new passwords match
        if password_change.new_password != password_change.new_password_confirm:
            logging.warning(f"Password mismatch during change attempt for user ID: {user_id}")
            raise PasswordMismatchError()
        
        # Update password
        user.password_hash = get_password_hash(password_change.new_password)
        db.commit()
        logging.info(f"Successfully changed password for user ID: {user_id}")
    except Exception as e:
        logging.error(f"Error during password change for user ID: {user_id}. Error: {str(e)}")
        raise
