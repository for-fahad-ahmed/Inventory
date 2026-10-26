from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend import models
from backend.database import get_db
from backend.dependencies import get_current_user
from backend.enums import Role
from backend.schemas import ProductCreate, ProductResponse, ProductUpdate

router = APIRouter(
    prefix="/products", tags=["products"], dependencies=[Depends(get_current_user)]
)


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    if db.get(models.Category, product.category_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id: {product.category_id} not found",
        )

    if db.get(models.Supplier, product.supplier_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Supplier with id: {product.supplier_id} not found",
        )

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
        inventory=models.Inventory(quantity_on_hand=0),
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
    products = db.scalars(select(models.Product).order_by(models.Product.id)).all()

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
def update_product_full(
    id: int,
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    existing_product = db.scalar(select(models.Product).where(models.Product.id == id))

    if not existing_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id: {id} not found",
        )

    # Only the owner can change prices (resending the current prices is fine)
    if current_user.role != Role.OWNER and (
        product.cost_price != existing_product.cost_price
        or product.selling_price != existing_product.selling_price
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the owner can change product prices",
        )

    if db.get(models.Category, product.category_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id: {product.category_id} not found",
        )

    if db.get(models.Supplier, product.supplier_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Supplier with id: {product.supplier_id} not found",
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
            detail="Could not update product due to a database constraint",
        )

    return existing_product


@router.patch("/{id}", response_model=ProductResponse, status_code=status.HTTP_200_OK)
def update_product_partial(
    id: int,
    product: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
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

    # None of the product fields are nullable
    for key, value in product_data.items():
        if value is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Field '{key}' cannot be null",
            )

    # Only the owner can change prices (resending the current price is fine)
    if current_user.role != Role.OWNER:
        for price_field in ("cost_price", "selling_price"):
            if price_field in product_data and product_data[price_field] != getattr(
                existing_product, price_field
            ):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only the owner can change product prices",
                )

    if "category_id" in product_data:
        if db.get(models.Category, product_data["category_id"]) is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with id: {product_data['category_id']} not found",
            )

    if "supplier_id" in product_data:
        if db.get(models.Supplier, product_data["supplier_id"]) is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Supplier with id: {product_data['supplier_id']} not found",
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
def deactivate_product(id: int, db: Session = Depends(get_db)):
    existing_product = db.scalar(select(models.Product).where(models.Product.id == id))

    if not existing_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id: {id} not found",
        )

    if existing_product.status:
        existing_product.status = False
        db.commit()
