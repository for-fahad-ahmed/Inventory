from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from backend import models
from backend.database import get_db
from backend.dependencies import get_current_user
from backend.schemas import InventoryResponse

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("/", response_model=list[InventoryResponse], status_code=status.HTTP_200_OK)
def get_inventory(
    low_stock: bool = False,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    statement = select(models.Inventory).join(models.Product)
    if low_stock:
        statement = statement.where(
            models.Inventory.quantity_on_hand <= models.Product.minimum_stock_lvl
        )
    statement = statement.options(selectinload(models.Inventory.product)).order_by(
        models.Inventory.product_id
    )
    return db.scalars(statement).all()


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
        .options(selectinload(models.Inventory.product))
    )
    if inventory is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory record not found",
        )
    return inventory
