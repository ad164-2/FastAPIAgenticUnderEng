"""
Authentication service - handles user authentication logic only
"""

from app.features.users.user_repository import UserRepository
from app.features.users.user_entity import User
from app.features.auth.auth_utils import hash_password, verify_password
from app.core.utils import get_logger, ValidationException

logger = get_logger(__name__)


class AuthService:
    """Service for authentication operations (login, register)."""

    def __init__(self):
        self.repository = UserRepository()

    def register_user(self, username: str, password: str, role: str = "user") -> User:
        """Register a new user."""
        logger.info(f"Registering user: {username}")

        # Check if user already exists
        if self.repository.get_by_username(username):
            logger.warning(f"Registration failed: username exists: {username}")
            raise ValidationException("Username already exists")

        return self.repository.create_user(
            username=username,
            password_hash=hash_password(password),
            role=role or "user"
        )

    def authenticate_user(self, username: str, password: str) -> User:
        """Authenticate user with username and password."""
        logger.info(f"Authenticating user: {username}")

        user = self.repository.get_by_username(username)
        if not user:
            logger.warning(f"Authentication failed: user not found: {username}")
            return None

        if not user.is_active:
            logger.warning(f"Authentication failed: user inactive: {username}")
            return None

        if not verify_password(password, user.password_hash):
            logger.warning(f"Authentication failed: invalid password: {username}")
            return None

        # Update last login
        self.repository.update_last_login(user.id)
        logger.info(f"User authenticated: {username}")

        return user
