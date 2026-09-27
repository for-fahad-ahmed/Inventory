from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..schemas import UserCreate, UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):

    existing_username = db.scalar(
        select(models.User.username).where(models.User.username == user.username)
    )
    existing_email = db.scalar(
        select(models.User.email).where(models.User.email == user.email)
    )

    existing_phone = db.scalar(
        select(models.User.phone).where(models.User.phone == user.phone)
    )

    if existing_username or existing_email or existing_phone:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this username, email or phone already exists",
        )

    new_user = models.User(
        username=user.username,
        name=user.name,
        email=user.email,
        phone=user.phone,
        role=user.role,
        status=user.status,
    )

    new_user.set_password(user.password)

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username, email, or phone already exists",
        )

    return new_user


@router.get("/{id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.scalar(select(models.User).where(models.User.id == id))

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User with: {id} not found"
        )

    return user


@router.get("/", response_model=list[UserResponse], status_code=status.HTTP_200_OK)
def get_users(db: Session = Depends(get_db)):
    users = db.scalars(select(models.User)).all()
    return users


@router.put("/{id}", response_model=UserResponse, status_code=status.HTTP_202_ACCEPTED)
def update_user_full(id: int, user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.scalar(select(models.User).where(models.User.id == id))

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id: {id} not found",
        )

    existing_username = db.scalar(
        select(models.User).where(
            models.User.username == user.username, models.User.id != id
        )
    )

    existing_email = db.scalar(
        select(models.User).where(models.User.email == user.email, models.User.id != id)
    )

    existing_phone = db.scalar(
        select(models.User).where(models.User.phone == user.phone, models.User.id != id)
    )

    if existing_username or existing_email or existing_phone:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this username, email or phone already exists",
        )

    existing_user.username = user.username
    existing_user.email = user.email
    existing_user.name = user.name
    existing_user.phone = user.phone
    existing_user.role = user.role
    existing_user.status = user.status
    existing_user.set_password(user.password)

    try:
        db.commit()
        db.refresh(existing_user)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username, email, or phone already exists",
        )

    return existing_user


@router.patch(
    "/{id}", response_model=UserResponse, status_code=status.HTTP_202_ACCEPTED
)
def update_user_partial(id: int, user: UserUpdate, db: Session = Depends(get_db)):
    user_data = user.model_dump(exclude_unset=True)

    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No data provided"
        )

    existing_user = db.scalar(select(models.User).where(models.User.id == id))

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if "username" in user_data:
        existing_username = db.scalar(
            select(models.User).where(
                models.User.username == user_data["username"], models.User.id != id
            )
        )

        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Username already exists"
            )

    if "email" in user_data:
        existing_email = db.scalar(
            select(models.User).where(
                models.User.email == user_data["email"], models.User.id != id
            )
        )

        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Email already exists"
            )

    if "phone" in user_data:
        existing_phone = db.scalar(
            select(models.User).where(
                models.User.phone == user_data["phone"], models.User.id != id
            )
        )

        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Phone already exists"
            )

    for key, value in user_data.items():
        if key == "password":
            existing_user.set_password(value)
        else:
            setattr(existing_user, key, value)

    try:
        db.commit()
        db.refresh(existing_user)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username, email, or phone already exists..",
        )

    return existing_user


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(id: int, db: Session = Depends(get_db)):
    user = db.scalar(select(models.User).where(models.User.id == id))

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    db.delete(user)
    db.commit()
