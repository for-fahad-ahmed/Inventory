from decimal import ROUND_HALF_UP, Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from backend import models
from backend.database import get_db
from backend.dependencies import get_current_user
from backend.enums import PaymentStatus, PurchaseStatus, Role, StockMovementType
from backend.schemas import (
    PurchaseCreate,
    PurchaseResponse,
    PurchaseUpdate,
)
from backend.stock import apply_detail_movements

CENT = Decimal("0.01")
ZERO = Decimal("0.00")


def money(value: Decimal):
    return Decimal(str(value)).quantize(CENT, rounding=ROUND_HALF_UP)


def build_purchase_details(detail_inputs: list, db: Session):
    product_ids = {detail.product_id for detail in detail_inputs}
    products = db.scalars(
        select(models.Product).where(models.Product.id.in_(product_ids))
    ).all()
    products_by_id = {product.id: product for product in products}

    missing_ids = product_ids - products_by_id.keys()
    if missing_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product(s) not found: {', '.join(map(str, sorted(missing_ids)))}",
        )

    details = []
    for item in detail_inputs:
        product = products_by_id[item.product_id]
        if not product.status:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Product {item.product_id} is inactive",
            )
        unit_price = money(item.unit_price)
        line_total = money(Decimal(item.quantity) * unit_price)
        details.append(
            models.PurchaseDetail(
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=unit_price,
                line_total=line_total,
            )
        )
    return details


def get_authorized_purchase(db: Session, purchase_id: int, current_user: models.User):
    statement = select(models.Purchase).where(models.Purchase.id == purchase_id)
    if current_user.role != Role.OWNER:
        statement = statement.where(models.Purchase.user_id == current_user.id)
    purchase = db.scalar(
        statement.options(selectinload(models.Purchase.purchase_details))
    )
    if purchase is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase not found",
        )
    return purchase


def calculate_purchase_totals(
    details: list,
    discount: Decimal,
    amount_paid: Decimal,
):
    subtotal = money(
        sum(
            (
                Decimal(str(detail.quantity)) * Decimal(str(detail.unit_price))
                for detail in details
            ),
            ZERO,
        )
    )

    discount = money(discount)
    amount_paid = money(amount_paid)

    if discount > subtotal:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Discount cannot exceed subtotal",
        )

    total = money(subtotal - discount)

    if amount_paid > total:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Amount paid cannot exceed total",
        )

    if amount_paid == ZERO:
        payment_status = PaymentStatus.UNPAID
    elif amount_paid == total:
        payment_status = PaymentStatus.PAID
    else:
        payment_status = PaymentStatus.PARTIAL

    return subtotal, total, payment_status


router = APIRouter(prefix="/purchases", tags=["purchases"])


@router.post("/", response_model=PurchaseResponse, status_code=status.HTTP_201_CREATED)
def create_purchase(
    purchase: PurchaseCreate,
    db: Session = Depends(get_db),
    current_user: models.User = (Depends(get_current_user)),
):

    reference_number_exists = db.scalar(
        select(models.Purchase.id).where(
            models.Purchase.reference_number == purchase.reference_number
        )
    )

    if reference_number_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Purchase reference number already exists",
        )

    supplier = db.get(models.Supplier, purchase.supplier_id)

    if supplier is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found"
        )
    if not supplier.status:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Cannot create a purchase for an inactive supplier",
        )

    details = build_purchase_details(purchase.purchase_details, db)

    subtotal, total, payment_status = calculate_purchase_totals(
        details, purchase.discount, purchase.amount_paid
    )

    new_purchase = models.Purchase(
        reference_number=purchase.reference_number,
        purchase_date=purchase.purchase_date,
        supplier_id=purchase.supplier_id,
        user_id=current_user.id,
        subtotal=subtotal,
        discount=money(purchase.discount),
        total=total,
        amount_paid=money(purchase.amount_paid),
        payment_status=payment_status,
        purchase_status=PurchaseStatus.COMPLETED,
        notes=purchase.notes,
        purchase_details=details,
    )
    try:
        db.add(new_purchase)
        db.flush()

        apply_detail_movements(
            db,
            new_purchase.purchase_details,
            movement_type=StockMovementType.PURCHASE,
            user_id=current_user.id,
            purchase_id=new_purchase.id,
            reason=f"Purchase {new_purchase.reference_number}",
        )

        db.commit()
        db.refresh(new_purchase)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Could not create purchase due to a database constraint",
        )
    except HTTPException:
        db.rollback()
        raise

    return new_purchase


@router.get("/{id}", response_model=PurchaseResponse, status_code=status.HTTP_200_OK)
def get_purchase(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    purchase = get_authorized_purchase(db, id, current_user)

    return purchase


@router.get("/", response_model=list[PurchaseResponse], status_code=status.HTTP_200_OK)
def get_purchases(
    db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)
):
    if current_user.role == Role.OWNER:
        purchases = db.scalars(
            select(models.Purchase).options(
                selectinload(models.Purchase.purchase_details)
            )
        ).all()

    else:
        purchases = db.scalars(
            select(models.Purchase)
            .where(models.Purchase.user_id == current_user.id)
            .options(selectinload(models.Purchase.purchase_details))
        ).all()

    return purchases


@router.patch("/{id}", response_model=PurchaseResponse, status_code=status.HTTP_200_OK)
def update_purchase_partial(
    id: int,
    purchase: PurchaseUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    purchase_data = purchase.model_dump(exclude_unset=True)
    if not purchase_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No data provided"
        )

    existing_purchase = get_authorized_purchase(db, id, current_user)

    if existing_purchase.purchase_status == PurchaseStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cancelled purchases cannot be edited",
        )

    if "reference_number" in purchase_data:
        duplicate = db.scalar(
            select(models.Purchase.id).where(
                models.Purchase.reference_number == purchase_data["reference_number"],
                models.Purchase.id != id,
            )
        )
        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Purchase reference number already exists",
            )

    amount_paid = purchase_data.get("amount_paid", existing_purchase.amount_paid)
    _, _, payment_status = calculate_purchase_totals(
        existing_purchase.purchase_details, existing_purchase.discount, amount_paid
    )

    try:
        for key, value in purchase_data.items():
            setattr(existing_purchase, key, value)

        existing_purchase.amount_paid = money(amount_paid)
        existing_purchase.payment_status = payment_status

        db.commit()
        db.refresh(existing_purchase)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Could not update purchase due to a database constraint",
        )

    return existing_purchase


@router.post(
    "/{id}/cancel", response_model=PurchaseResponse, status_code=status.HTTP_200_OK
)
def cancel_purchase(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    existing_purchase = get_authorized_purchase(db, id, current_user)

    if existing_purchase.purchase_status == PurchaseStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Purchase is already cancelled",
        )

    try:
        if existing_purchase.purchase_status == PurchaseStatus.COMPLETED:
            apply_detail_movements(
                db,
                existing_purchase.purchase_details,
                movement_type=StockMovementType.PURCHASE_CANCELLATION,
                user_id=current_user.id,
                purchase_id=existing_purchase.id,
                reason=f"Cancelled purchase {existing_purchase.reference_number}",
            )

        existing_purchase.purchase_status = PurchaseStatus.CANCELLED
        db.commit()
        db.refresh(existing_purchase)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Could not cancel purchase due to a database constraint",
        )
    except HTTPException:
        db.rollback()
        raise

    return existing_purchase


# @router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
# def delete_purchase(id: int, db: Session = Depends(get_db)):
#     purchase = db.scalar(select(models.Purchase).where(models.Purchase.id == id))

#     if not purchase:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Purchase with id: {id} not found",
#         )

#     db.delete(purchase)
#     db.commit()
