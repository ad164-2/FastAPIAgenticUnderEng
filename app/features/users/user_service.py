"""
User service for CRUD operations
"""

from app.features.users.user_repository import UserRepository
from app.features.users.user_entity import User
from app.core.utils import get_logger, NotFoundException

logger = get_logger(__name__)


class UserService:
    """Service for User CRUD operations."""

    def __init__(self):
        self.repository = UserRepository()

    def get_all_users(self, skip: int = 0, limit: int = 100):
        """Get all active users."""
        return self.repository.get_active_users(skip=skip, limit=limit)

    def get_user(self, user_id: int):
        """Get user by ID."""
        user = self.repository.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")
        return user

    def get_user_by_username(self, username: str):
        """Get user by username."""
        return self.repository.get_by_username(username)

    def update_user(self, user_id: int, user_data) -> User:
        """Update user profile."""
        user = self.repository.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")
        
        update_data = user_data.model_dump(exclude_unset=True, exclude_none=True)
        for key, value in update_data.items():
            if hasattr(user, key) and key != "id":
                setattr(user, key, value)
        
        db = self.repository._get_db()
        db.commit()
        db.refresh(user)
        return user

    def delete_user(self, user_id: int):
        """Delete user account."""
        user = self.repository.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")
        return self.repository.delete(user_id)

    def deactivate_user(self, user_id: int) -> User:
        """Deactivate user account."""
        logger.info(f"Deactivating user: {user_id}")
        return self.repository.deactivate_user(user_id)

    def activate_user(self, user_id: int) -> User:
        """Activate user account."""
        logger.info(f"Activating user: {user_id}")
        return self.repository.activate_user(user_id)
