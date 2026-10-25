from decimal import ROUND_HALF_UP, Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from backend import models
from backend.database import get_db
from backend.dependencies import get_current_user
from backend.enums import PaymentStatus, Role, StockMovementType
from backend.schemas import SaleCreate, SaleResponse, SaleUpdate
from backend.stock import apply_detail_movements

CENT = Decimal("0.01")
ZERO = Decimal("0.00")


def money(value: Decimal):
    return Decimal(str(value)).quantize(CENT, rounding=ROUND_HALF_UP)


def build_sale_details(detail_inputs: list, db: Session):
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

        selling_price = money(item.selling_price)
        line_total = money(Decimal(item.quantity) * selling_price)
        details.append(
            models.SaleDetail(
                product_id=item.product_id,
                quantity=item.quantity,
                selling_price=selling_price,
                cost_price=money(product.cost_price),
                line_total=line_total,
            )
        )

    return details


def get_authorized_sale(db: Session, sale_id: int, current_user: models.User):
    statement = select(models.Sale).where(models.Sale.id == sale_id)
    if current_user.role != Role.OWNER:
        statement = statement.where(models.Sale.user_id == current_user.id)

    sale = db.scalar(statement.options(selectinload(models.Sale.sale_details)))
    if sale is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sale not found",
        )
    return sale


def calculate_sale_totals(details: list, discount: Decimal, amount_paid: Decimal):
    subtotal = money(
        sum(
            (
                Decimal(str(detail.quantity)) * Decimal(str(detail.selling_price))
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


router = APIRouter(prefix="/sales", tags=["sales"])


@router.post("/", response_model=SaleResponse, status_code=status.HTTP_201_CREATED)
def create_sale(
    sale: SaleCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    invoice_number_exists = db.scalar(
        select(models.Sale.id).where(models.Sale.invoice_number == sale.invoice_number)
    )
    if invoice_number_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Sale invoice number already exists",
        )

    customer = db.get(models.Customer, sale.customer_id)
    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )
    if not customer.status:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Cannot create a sale for an inactive customer",
        )

    details = build_sale_details(sale.sale_details, db)
    subtotal, total, payment_status = calculate_sale_totals(
        details, sale.discount, sale.amount_paid
    )

    new_sale = models.Sale(
        invoice_number=sale.invoice_number,
        sale_date=sale.sale_date,
        customer_id=sale.customer_id,
        user_id=current_user.id,
        subtotal=subtotal,
        discount=money(sale.discount),
        total=total,
        amount_paid=money(sale.amount_paid),
        payment_status=payment_status,
        sale_details=details,
    )

    try:
        db.add(new_sale)
        db.flush()

        apply_detail_movements(
            db,
            new_sale.sale_details,
            movement_type=StockMovementType.SALE,
            user_id=current_user.id,
            sale_id=new_sale.id,
            reason=f"Sale invoice {new_sale.invoice_number}",
        )

        db.commit()
        db.refresh(new_sale)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Could not create sale due to a database constraint",
        )
    except HTTPException:
        db.rollback()
        raise

    return new_sale


@router.get("/{id}", response_model=SaleResponse, status_code=status.HTTP_200_OK)
def get_sale(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return get_authorized_sale(db, id, current_user)


@router.get("/", response_model=list[SaleResponse], status_code=status.HTTP_200_OK)
def get_sales(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    statement = select(models.Sale).options(selectinload(models.Sale.sale_details))
    if current_user.role != Role.OWNER:
        statement = statement.where(models.Sale.user_id == current_user.id)

    return db.scalars(statement).all()


@router.patch("/{id}", response_model=SaleResponse, status_code=status.HTTP_200_OK)
def update_sale_partial(
    id: int,
    sale: SaleUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    sale_data = sale.model_dump(exclude_unset=True)
    if not sale_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data provided",
        )

    existing_sale = get_authorized_sale(db, id, current_user)

    for key, value in sale_data.items():
        if value is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Field '{key}' cannot be null",
            )

    if "invoice_number" in sale_data:
        duplicate = db.scalar(
            select(models.Sale.id).where(
                models.Sale.invoice_number == sale_data["invoice_number"],
                models.Sale.id != id,
            )
        )
        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Sale invoice number already exists",
            )

    if "customer_id" in sale_data:
        customer = db.get(models.Customer, sale_data["customer_id"])
        if customer is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found",
            )
        if not customer.status:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Cannot use an inactive customer",
            )

    amount_paid = sale_data.get("amount_paid", existing_sale.amount_paid)
    _, _, payment_status = calculate_sale_totals(
        existing_sale.sale_details, existing_sale.discount, amount_paid
    )

    try:
        for key, value in sale_data.items():
            setattr(existing_sale, key, value)

        existing_sale.amount_paid = money(amount_paid)
        existing_sale.payment_status = payment_status

        db.commit()
        db.refresh(existing_sale)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Could not update sale due to a database constraint",
        )

    return existing_sale
