"""
Authentication middleware
"""

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from app.features.auth.jwt import get_user_id_from_token
from app.core.config import settings
from app.core.utils import get_logger
from app.features.users.user_repository import UserRepository


logger = get_logger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware to validate authentication tokens."""

    async def dispatch(self, request: Request, call_next):
        """
        Process request and validate token if needed.

        Args:
            request: HTTP request
            call_next: Next middleware/route

        Returns:
            Response
        """
        # Check if route is excluded from authentication
        path = request.url.path
        if self._is_excluded_route(path):
            logger.debug(f"Public route accessed: {path}")
            return await call_next(request)

        # Get token from header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            logger.warning(f"No authorization header for route: {path}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authorization header",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Extract token
        try:
            scheme, token = auth_header.split()
            if scheme.lower() != "bearer":
                raise ValueError("Invalid scheme")
        except ValueError:
            logger.warning(f"Invalid authorization header format: {auth_header}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header format",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Verify token
        user_id = get_user_id_from_token(token)
        if not user_id:
            logger.warning(f"Invalid token provided for route: {path}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Add user to request state
        repo = UserRepository()
        user = repo.get_by_id(user_id)
        if not user or not user.is_active:
            logger.warning(f"Inactive or missing user for token: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive or missing user",
                headers={"WWW-Authenticate": "Bearer"},
            )
        request.state.user = user
        logger.debug(f"Authenticated user {user.username} accessing {path}")

        return await call_next(request)

    @staticmethod
    def _is_excluded_route(path: str) -> bool:
        """
        Check if route is excluded from authentication.

        Args:
            path: Request path

        Returns:
            True if route is excluded
        """
        excluded = settings.auth_excluded_routes
        for excluded_route in excluded:
            if path == excluded_route or path.startswith(excluded_route):
                return True
        return False
