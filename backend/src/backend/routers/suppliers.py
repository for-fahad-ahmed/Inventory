from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..schemas import SupplierCreate, SupplierResponse, SupplierUpdate

router = APIRouter(prefix="/suppliers", tags=["suppliers"])


@router.post("/", response_model=SupplierResponse, status_code=status.HTTP_201_CREATED)
def create_supplier(supplier: SupplierCreate, db: Session = Depends(get_db)):
    email_exists = db.scalar(
        select(models.Supplier.id).where(models.Supplier.email == supplier.email)
    )
    phone_exists = db.scalar(
        select(models.Supplier.id).where(models.Supplier.phone == supplier.phone)
    )

    if email_exists or phone_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="email or number already exists",
        )

    new_supplier = models.Supplier(
        name=supplier.name,
        contact_person=supplier.contact_person,
        email=supplier.email,
        phone=supplier.phone,
        address=supplier.address,
        status=supplier.status,
    )

    try:
        db.add(new_supplier)
        db.commit()
        db.refresh(new_supplier)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="email or phone already exists"
        )

    return new_supplier


@router.get("/", response_model=list[SupplierResponse], status_code=status.HTTP_200_OK)
def get_suppliers(db: Session = Depends(get_db)):
    suppliers = db.scalars(select(models.Supplier)).all()

    return suppliers


@router.get("/{id}", response_model=SupplierResponse, status_code=status.HTTP_200_OK)
def get_supplier(id: int, db: Session = Depends(get_db)):
    supplier = db.scalar(select(models.Supplier).where(models.Supplier.id == id))

    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Supplier with id: {id} not found",
        )

    return supplier


@router.put("/{id}", response_model=SupplierResponse, status_code=status.HTTP_200_OK)
def update_supplier_full(
    id: int, supplier: SupplierCreate, db: Session = Depends(get_db)
):
    existing_supplier = db.scalar(
        select(models.Supplier).where(models.Supplier.id == id)
    )

    if not existing_supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Supplier with id: {id} not found",
        )

    email_exists = db.scalar(
        select(models.Supplier.id).where(
            models.Supplier.email == supplier.email, models.Supplier.id != id
        )
    )
    phone_exists = db.scalar(
        select(models.Supplier.id).where(
            models.Supplier.phone == supplier.phone, models.Supplier.id != id
        )
    )

    if email_exists or phone_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="email or phone already exists"
        )

    existing_supplier.name = supplier.name
    existing_supplier.contact_person = supplier.contact_person
    existing_supplier.email = supplier.email
    existing_supplier.phone = supplier.phone
    existing_supplier.address = supplier.address
    existing_supplier.status = supplier.status

    try:
        db.commit()
        db.refresh(existing_supplier)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="email or phone already exists"
        )

    return existing_supplier


@router.patch("/{id}", response_model=SupplierResponse, status_code=status.HTTP_200_OK)
def update_supplier_partial(
    id: int, supplier: SupplierUpdate, db: Session = Depends(get_db)
):
    existing_supplier = db.scalar(
        select(models.Supplier).where(models.Supplier.id == id)
    )

    if not existing_supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Supplier with id: {id} not found",
        )

    supplier_data = supplier.model_dump(exclude_unset=True)

    if not supplier_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="no data provided"
        )

    if "email" in supplier_data:
        email_exists = db.scalar(
            select(models.Supplier.id).where(
                models.Supplier.email == supplier_data["email"],
                models.Supplier.id != id,
            )
        )

        if email_exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists",
            )

    if "phone" in supplier_data:
        phone_exists = db.scalar(
            select(models.Supplier.id).where(
                models.Supplier.phone == supplier_data["phone"],
                models.Supplier.id != id,
            )
        )

        if phone_exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Phone already exists",
            )

    for key, value in supplier_data.items():
        setattr(existing_supplier, key, value)

    try:
        db.commit()
        db.refresh(existing_supplier)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email or phone already exists"
        )

    return existing_supplier


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_supplier(id: int, db: Session = Depends(get_db)):
    existing_supplier = db.scalar(
        select(models.Supplier).where(models.Supplier.id == id)
    )

    if not existing_supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Supplier with id: {id} not found",
        )
    try:
        db.delete(existing_supplier)
        db.commit()

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete supplier because it is linked to existing products or purchases.",
        )
