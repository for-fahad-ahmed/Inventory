from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend import models
from backend.enums import StockMovementType

MOVEMENT_DIRECTION = {
    StockMovementType.PURCHASE: 1,
    StockMovementType.SALE: -1,
    StockMovementType.PURCHASE_CANCELLATION: -1,
}


def apply_stock_movement(
    db: Session,
    *,
    product_id: int,
    movement_type: StockMovementType,
    quantity: int,
    user_id: int,
    sale_id: int | None = None,
    purchase_id: int | None = None,
    reason: str | None = None,
) -> None:

    inventory = db.scalar(
        select(models.Inventory)
        .where(models.Inventory.product_id == product_id)
        .with_for_update()
        .execution_options(populate_existing=True)
    )
    if inventory is None:
        inventory = models.Inventory(product_id=product_id, quantity_on_hand=0)
        db.add(inventory)
        db.flush()

    new_quantity = inventory.quantity_on_hand + (
        MOVEMENT_DIRECTION[movement_type] * quantity
    )
    if new_quantity < 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Insufficient stock for product {product_id}: "
                f"{inventory.quantity_on_hand} in stock, {quantity} needed"
            ),
        )

    inventory.quantity_on_hand = new_quantity
    db.add(
        models.StockMovement(
            product_id=product_id,
            movement_type=movement_type,
            quantity_change=quantity,
            sale_id=sale_id,
            purchase_id=purchase_id,
            reason=reason,
            user_id=user_id,
        )
    )


def apply_detail_movements(
    db: Session,
    details: list,
    *,
    movement_type: StockMovementType,
    user_id: int,
    sale_id: int | None = None,
    purchase_id: int | None = None,
    reason: str | None = None,
) -> None:
    for detail in sorted(details, key=lambda d: d.product_id):
        apply_stock_movement(
            db,
            product_id=detail.product_id,
            movement_type=movement_type,
            quantity=detail.quantity,
            user_id=user_id,
            sale_id=sale_id,
            purchase_id=purchase_id,
            reason=reason,
        )
