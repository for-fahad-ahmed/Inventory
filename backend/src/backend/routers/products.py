from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend import models
from backend.database import get_db
from backend.dependencies import get_current_user
from backend.schemas import ProductCreate, ProductResponse, ProductUpdate

router = APIRouter(
    prefix="/products", tags=["products"], dependencies=[Depends(get_current_user)]
)


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    new_product = models.Product(
        product_code=f"PRD-{uuid4().hex[:12].upper()}",
        name=product.name,
        description=product.description,
        category_id=product.category_id,
        supplier_id=product.supplier_id,
        cost_price=product.cost_price,
        selling_price=product.selling_price,
        minimum_stock_lvl=product.minimum_stock_lvl,
        status=product.status,
    )

    try:
        db.add(new_product)
        db.commit()
        db.refresh(new_product)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Could not create product due to a database constraint",
        )

    return new_product


@router.get("/", response_model=list[ProductResponse], status_code=status.HTTP_200_OK)
def get_products(db: Session = Depends(get_db)):
    products = db.scalars(select(models.Product)).all()

    return products


@router.get("/{id}", response_model=ProductResponse, status_code=status.HTTP_200_OK)
def get_product(id: int, db: Session = Depends(get_db)):
    product = db.scalar(select(models.Product).where(models.Product.id == id))

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id: {id} not found",
        )

    return product


@router.put("/{id}", response_model=ProductResponse, status_code=status.HTTP_200_OK)
def update_product_full(id: int, product: ProductCreate, db: Session = Depends(get_db)):
    existing_product = db.scalar(select(models.Product).where(models.Product.id == id))

    if not existing_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id: {id} not found",
        )

    existing_product.name = product.name
    existing_product.description = product.description
    existing_product.category_id = product.category_id
    existing_product.supplier_id = product.supplier_id
    existing_product.cost_price = product.cost_price
    existing_product.selling_price = product.selling_price
    existing_product.minimum_stock_lvl = product.minimum_stock_lvl
    existing_product.status = product.status

    try:
        db.commit()
        db.refresh(existing_product)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Could not create product due to a database constraint",
        )

    return existing_product


@router.patch("/{id}", response_model=ProductResponse, status_code=status.HTTP_200_OK)
def update_product_partial(
    id: int, product: ProductUpdate, db: Session = Depends(get_db)
):
    existing_product = db.scalar(select(models.Product).where(models.Product.id == id))

    if not existing_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id: {id} not found",
        )

    product_data = product.model_dump(exclude_unset=True)

    if not product_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No data provided"
        )

    for key, value in product_data.items():
        setattr(existing_product, key, value)

    try:
        db.commit()
        db.refresh(existing_product)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Could not update product due to a database constraint",
        )

    return existing_product


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(id: int, db: Session = Depends(get_db)):
    existing_product = db.scalar(select(models.Product).where(models.Product.id == id))

    if not existing_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id: {id} not found",
        )

    try:
        db.delete(existing_product)
        db.commit()
    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Can not delete product because it is linked to existing purchases",
        )
