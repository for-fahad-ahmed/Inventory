from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend import models
from backend.database import get_db
from backend.dependencies import get_current_user
from backend.schemas import Token, UserResponse
from backend.security import create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/token", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = db.scalar(
        select(models.User).where(models.User.username == form_data.username)
    )

    if user is None or not user.status or not user.check_password(form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user.last_login_at = datetime.now(timezone.utc)
    db.commit()

    return Token(access_token=create_access_token(user.id), token_type="bearer")


@router.get("/me", response_model=UserResponse)
def read_user(current_user: models.User = Depends(get_current_user)):
    return current_user
