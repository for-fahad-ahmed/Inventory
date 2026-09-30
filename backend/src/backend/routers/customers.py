from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..schemas import CustomerCreate, CustomerResponse, CustomerUpdate

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):

    existing_email = db.scalar(
        select(models.Customer.email).where(models.Customer.email == customer.email)
    )

    existing_phone = db.scalar(
        select(models.Customer.phone).where(models.Customer.phone == customer.phone)
    )

    if existing_email or existing_phone:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Customer with this email or phone already exists",
        )

    new_customer = models.Customer(
        name=customer.name,
        email=customer.email,
        phone=customer.phone,
        address=customer.address,
        status=customer.status,
    )

    try:
        db.add(new_customer)
        db.commit()
        db.refresh(new_customer)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="email, or phone already exists",
        )

    return new_customer


@router.get("/{id}", response_model=CustomerResponse, status_code=status.HTTP_200_OK)
def get_customer(id: int, db: Session = Depends(get_db)):
    customer = db.scalar(select(models.Customer).where(models.Customer.id == id))

    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with id: {id} not found",
        )

    return customer


@router.get("/", response_model=list[CustomerResponse], status_code=status.HTTP_200_OK)
def get_customers(db: Session = Depends(get_db)):
    customers = db.scalars(select(models.Customer)).all()
    return customers


@router.put("/{id}", response_model=CustomerResponse, status_code=status.HTTP_200_OK)
def update_customer_full(
    id: int, customer: CustomerCreate, db: Session = Depends(get_db)
):
    existing_customer = db.scalar(
        select(models.Customer).where(models.Customer.id == id)
    )

    if not existing_customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with id: {id} not found",
        )

    existing_email = db.scalar(
        select(models.Customer).where(
            models.Customer.email == customer.email, models.Customer.id != id
        )
    )

    existing_phone = db.scalar(
        select(models.Customer).where(
            models.Customer.phone == customer.phone, models.Customer.id != id
        )
    )

    if existing_email or existing_phone:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Customer with this email or phone already exists",
        )

    existing_customer.email = customer.email
    existing_customer.name = customer.name
    existing_customer.phone = customer.phone
    existing_customer.address = customer.address
    existing_customer.status = customer.status

    try:
        db.commit()
        db.refresh(existing_customer)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="email, or phone already exists",
        )

    return existing_customer


@router.patch("/{id}", response_model=CustomerResponse, status_code=status.HTTP_200_OK)
def update_customer_partial(
    id: int, customer: CustomerUpdate, db: Session = Depends(get_db)
):
    customer_data = customer.model_dump(exclude_unset=True)

    if not customer_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No data provided"
        )

    existing_customer = db.scalar(
        select(models.Customer).where(models.Customer.id == id)
    )

    if not existing_customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer with id: {id} not found",
        )

    if "email" in customer_data:
        existing_email = db.scalar(
            select(models.Customer).where(
                models.Customer.email == customer_data["email"],
                models.Customer.id != id,
            )
        )

        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Email already exists"
            )

    if "phone" in customer_data:
        existing_phone = db.scalar(
            select(models.Customer).where(
                models.Customer.phone == customer_data["phone"],
                models.Customer.id != id,
            )
        )

        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Phone already exists"
            )

    for key, value in customer_data.items():
        setattr(existing_customer, key, value)

    try:
        db.commit()
        db.refresh(existing_customer)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="email, or phone already exists..",
        )

    return existing_customer


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(id: int, db: Session = Depends(get_db)):
    customer = db.scalar(select(models.Customer).where(models.Customer.id == id))

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with id: {id} not found",
        )

    db.delete(customer)
    db.commit()
