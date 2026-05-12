"""Shared FastAPI dependencies — authentication, authorization."""

import os
from typing import List

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

security = HTTPBearer()

JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "")
JWT_ALGORITHM = "HS256"


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """Decode and validate JWT token. Returns user payload or raises 401."""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_permissions(*required: str):
    """
    Dependency factory: checks that the current user has ALL required permissions.

    Permissions from roles table:
      CEO:          {"all": true, "view_all": true, "manage_all": true}
      HR:           {"manage_all": true, "view_all": true, "export_reports": true}
      Unit Manager: {"view_unit": true, "manage_unit": true, "approve_evaluations": true}
      Group Leader: {"view_group": true, "manage_group": true, "review_evaluations": true}
      Member:       {"view_self": true, "edit_self": true}

    Usage:
      @router.get("/admin", dependencies=[Depends(require_permissions("manage_all"))])
      def admin_endpoint(...): ...

      OR as parameter:
      def endpoint(user: dict = Depends(require_permissions("view_all"))):
    """
    def checker(user: dict = Depends(get_current_user)) -> dict:
        permissions = user.get("permissions", {})
        # "all" permission grants everything
        if permissions.get("all"):
            return user
        for perm in required:
            if not permissions.get(perm):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied. Required: {', '.join(required)}",
                )
        return user
    return checker


def require_any_permission(*required: str):
    """Checks that the current user has AT LEAST ONE of the required permissions."""
    def checker(user: dict = Depends(get_current_user)) -> dict:
        permissions = user.get("permissions", {})
        if permissions.get("all"):
            return user
        if any(permissions.get(perm) for perm in required):
            return user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission denied. Required one of: {', '.join(required)}",
        )
    return checker
