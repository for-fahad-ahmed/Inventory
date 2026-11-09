from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, contains_eager, joinedload

from backend import models
from backend.database import get_db
from backend.dependencies import get_current_user
from backend.schemas import InventoryResponse, PaginatedInventoryResponse

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get(
    "/", response_model=PaginatedInventoryResponse, status_code=status.HTTP_200_OK
)
def get_inventory(
    low_stock: Optional[bool] = False,
    category_id: Optional[int] = None,
    supplier_id: Optional[int] = None,
    search: Optional[str] = None,
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
):
    statement = select(models.Inventory)
    product_joined = False
    if (
        low_stock
        or category_id is not None
        or supplier_id is not None
        or search
        or active_only
    ):
        statement = statement.join(models.Inventory.product)
        product_joined = True
    if active_only:
        statement = statement.where(models.Product.status.is_(True))
    if low_stock:
        statement = statement.where(
            models.Inventory.quantity_on_hand <= models.Product.minimum_stock_lvl
        )
    if search:
        pattern = f"%{search}%"
        statement = statement.where(
            or_(
                models.Product.name.ilike(pattern),
                models.Product.product_code.ilike(pattern),
            )
        )
    if category_id is not None:
        statement = statement.where(models.Product.category_id == category_id)
    if supplier_id is not None:
        statement = statement.where(models.Product.supplier_id == supplier_id)

    count_statement = statement.with_only_columns(
        func.count(models.Inventory.product_id)
    ).order_by(None)
    total = db.scalar(count_statement) or 0

    if not product_joined:
        statement = statement.join(models.Inventory.product)

    statement = (
        statement.options(contains_eager(models.Inventory.product))
        .order_by(models.Inventory.product_id)
        .offset(skip)
        .limit(limit)
    )

    inventory = db.scalars(statement).all()

    has_more = (len(inventory) + skip) < total

    return PaginatedInventoryResponse(
        products=inventory, total=total, skip=skip, limit=limit, has_more=has_more
    )


@router.get(
    "/{product_id}", response_model=InventoryResponse, status_code=status.HTTP_200_OK
)
def get_product_inventory(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    inventory = db.scalar(
        select(models.Inventory)
        .where(models.Inventory.product_id == product_id)
        .options(joinedload(models.Inventory.product))
    )
    if inventory is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory record not found",
        )
    return inventory
