from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend import models
from backend.database import get_db
from backend.dependencies import get_current_user
from backend.schemas import CategoryCreate, CategoryResponse, CategoryUpdate

router = APIRouter(
    prefix="/categories", tags=["categories"], dependencies=[Depends(get_current_user)]
)


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):

    existing_name = db.scalar(
        select(models.Category.name).where(models.Category.name == category.name)
    )

    if existing_name:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Category with this name already exists",
        )

    new_category = models.Category(name=category.name, description=category.description)

    try:
        db.add(new_category)
        db.commit()
        db.refresh(new_category)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Category with this name already exists",
        )

    return new_category


@router.get("/", response_model=list[CategoryResponse], status_code=status.HTTP_200_OK)
def get_categories(db: Session = Depends(get_db)):
    categories = db.scalars(select(models.Category)).all()

    return categories


@router.get("/{id}", response_model=CategoryResponse, status_code=status.HTTP_200_OK)
def get_category(id: int, db: Session = Depends(get_db)):
    category = db.scalar(select(models.Category).where(models.Category.id == id))
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"category with id: {id} not found",
        )
    return category


@router.put("/{id}", response_model=CategoryResponse, status_code=status.HTTP_200_OK)
def update_category_full(
    id: int, category: CategoryCreate, db: Session = Depends(get_db)
):
    existing_category = db.scalar(
        select(models.Category).where(models.Category.id == id)
    )

    if not existing_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id: {id} not found",
        )

    existing_name = db.scalar(
        select(models.Category.name).where(
            models.Category.name == category.name, models.Category.id != id
        )
    )

    if existing_name:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Category with this name already exists",
        )

    existing_category.name = category.name
    existing_category.description = category.description

    try:
        db.commit()
        db.refresh(existing_category)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Category with this name already exists",
        )

    return existing_category


@router.patch("/{id}", response_model=CategoryResponse, status_code=status.HTTP_200_OK)
def update_category_partial(
    id: int, category: CategoryUpdate, db: Session = Depends(get_db)
):
    existing_category = db.scalar(
        select(models.Category).where(models.Category.id == id)
    )

    if not existing_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id: {id} not found",
        )

    category_data = category.model_dump(exclude_unset=True)

    if "name" in category_data:
        existing_name = db.scalar(
            select(models.Category.name).where(
                models.Category.name == category_data["name"], models.Category.id != id
            )
        )

        if existing_name:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Category with this name already exists",
            )

    for key, value in category_data.items():
        setattr(existing_category, key, value)

    try:
        db.commit()
        db.refresh(existing_category)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Category with this name already exists..",
        )

    return existing_category


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(id: int, db: Session = Depends(get_db)):
    category = db.scalar(select(models.Category).where(models.Category.id == id))

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id: {id} not found",
        )

    db.delete(category)
    db.commit()
