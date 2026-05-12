"""BFF Layer: Authentication endpoints."""

import logging

from fastapi import APIRouter, HTTPException, Depends

logger = logging.getLogger(__name__)
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from services import auth_service

router = APIRouter(prefix="/v1/auth", tags=["auth"])


class LoginRequest(BaseModel):
    username: str  # email
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


@router.post("/login", response_model=LoginResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    logger.info(f"[LOGIN ATTEMPT] username={req.username}")
    user = auth_service.authenticate_user(db, req.username, req.password)
    if user is None:
        logger.warning(f"[LOGIN FAILED] username={req.username}")
        raise HTTPException(status_code=401, detail="Invalid username or password")

    logger.info(f"[LOGIN SUCCESS] user={user}")
    token = auth_service.create_access_token(user)
    return LoginResponse(access_token=token, user=user)
