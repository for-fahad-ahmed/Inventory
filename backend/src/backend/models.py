from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from argon2 import PasswordHasher
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base
from backend.enums import (
    PaymentMethod,
    PaymentStatus,
    PurchaseStatus,
    Role,
    StockMovementType,
)

ph = PasswordHasher()


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(20), nullable=False)
    username: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(12), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[Role] = mapped_column(SAEnum(Role), nullable=False)
    status: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    purchases: Mapped[list[Purchase]] = relationship(back_populates="user")
    sales: Mapped[list[Sale]] = relationship(back_populates="user")
    payment: Mapped[list[Payment]] = relationship(back_populates="user")

    def set_password(self, password: str):
        self.password_hash = ph.hash(password)

    def check_password(self, password: str) -> bool:
        try:
            ph.verify(self.password_hash, password)
            return True
        except Exception:
            return False


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(15), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)

    products: Mapped[list[Product]] = relationship(back_populates="category")


class Supplier(Base):
    __tablename__ = "suppliers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(20), nullable=False)
    contact_person: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(12), unique=True, nullable=False)
    address: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    products: Mapped[list[Product]] = relationship(back_populates="supplier")
    purchases: Mapped[list[Purchase]] = relationship(back_populates="supplier")


class Product(Base):
    __tablename__ = "products"

    __table_args__ = (
        CheckConstraint(
            "(minimum_stock_lvl >= 0)",
            name="positive_minimum_stock_lvl",
        ),
        CheckConstraint(
            "(cost_price) >= 0",
            name="positive_cost_price",
        ),
        CheckConstraint(
            "(selling_price) > 0",
            name="positive_selling_price",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(String(150), nullable=False)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"), nullable=False
    )
    supplier_id: Mapped[int] = mapped_column(ForeignKey("suppliers.id"), nullable=False)
    cost_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    selling_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    minimum_stock_lvl: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    supplier: Mapped[Supplier] = relationship(back_populates="products")
    category: Mapped[Category] = relationship(back_populates="products")
    purchase_details: Mapped[list[PurchaseDetail]] = relationship(
        back_populates="product"
    )
    sale_details: Mapped[list[SaleDetail]] = relationship(back_populates="product")


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[str | None] = mapped_column(String(50), unique=True, nullable=True)
    phone: Mapped[str | None] = mapped_column(
        String(12),
        unique=True,
        nullable=True,
    )
    address: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    sales: Mapped[list[Sale]] = relationship(back_populates="customer")


class Purchase(Base):
    __tablename__ = "purchases"

    __table_args__ = (
        CheckConstraint("subtotal >= 0", name="positive_subtotal"),
        CheckConstraint("discount >= 0", name="positive_discount"),
        CheckConstraint("total >= 0", name="positive_total"),
        CheckConstraint("amount_paid >= 0", name="positive_amount_paid"),
        CheckConstraint(
            "discount <= subtotal", name="discount_not_greater_than_subtotal"
        ),
        CheckConstraint(
            "amount_paid <= total", name="amount_paid_not_greater_than_total"
        ),
        CheckConstraint(
            "total = subtotal - discount", name="purchase_total_matches_subtotal"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reference_number: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    purchase_date: Mapped[date] = mapped_column(
        Date, nullable=False, default=date.today
    )
    supplier_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("suppliers.id"), nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    discount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
    )
    total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    amount_paid: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    payment_status: Mapped[PaymentStatus] = mapped_column(
        SAEnum(PaymentStatus),
        nullable=False,
        default=PaymentStatus.UNPAID,
    )
    purchase_status: Mapped[PurchaseStatus] = mapped_column(
        SAEnum(PurchaseStatus),
        nullable=False,
        default=PurchaseStatus.DRAFT,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    supplier: Mapped[Supplier] = relationship(back_populates="purchases")
    user: Mapped[User] = relationship(back_populates="purchases")
    purchase_details: Mapped[list[PurchaseDetail]] = relationship(
        back_populates="purchase",
        cascade="all, delete-orphan",
    )
    payment: Mapped[Payment | None] = relationship(back_populates="purchase")


class PurchaseDetail(Base):
    __tablename__ = "purchase_details"

    __table_args__ = (
        CheckConstraint("(quantity) > 0", name="positive_quantity"),
        CheckConstraint("(unit_price) > 0", name="positive_unit_price"),
        CheckConstraint("(line_total) > 0", name="positive_line_total"),
        CheckConstraint(
            "line_total = quantity * unit_price",
            name="purchase_line_total_matches_quantity_price",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    purchase_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("purchases.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("products.id"),
        nullable=False,
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    line_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    purchase: Mapped[Purchase] = relationship(back_populates="purchase_details")
    product: Mapped[Product] = relationship(back_populates="purchase_details")


class Sale(Base):
    __tablename__ = "sales"

    __table_args__ = (
        CheckConstraint("(subtotal) >= 0", name="positive_subtotal"),
        CheckConstraint("(discount) >= 0", name="positive_discount"),
        CheckConstraint("(total) >= 0", name="positive_total"),
        CheckConstraint("(amount_paid) >= 0", name="positive_amount_paid"),
        CheckConstraint(
            "discount <= subtotal", name="sale_discount_not_greater_than_subtotal"
        ),
        CheckConstraint(
            "amount_paid <= total", name="sale_amount_paid_not_greater_than_total"
        ),
        CheckConstraint(
            "total = subtotal - discount", name="sale_total_matches_subtotal"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    invoice_number: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    sale_date: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)
    customer_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("customers.id"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    discount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
    )
    total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    amount_paid: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    payment_status: Mapped[PaymentStatus] = mapped_column(
        SAEnum(PaymentStatus),
        nullable=False,
        default=PaymentStatus.UNPAID,
    )

    customer: Mapped[Customer] = relationship(back_populates="sales")
    user: Mapped[User] = relationship(back_populates="sales")
    sale_details: Mapped[list[SaleDetail]] = relationship(
        back_populates="sale",
        cascade="all, delete-orphan",
    )
    payment: Mapped[Payment | None] = relationship(back_populates="sale")


class SaleDetail(Base):
    __tablename__ = "sale_details"

    __table_args__ = (
        CheckConstraint("(quantity) > 0", name="positive_quantity"),
        CheckConstraint("(selling_price) > 0", name="positive_selling_price"),
        CheckConstraint("(line_total) > 0", name="positive_line_total"),
        CheckConstraint(
            "line_total = quantity * selling_price",
            name="sale_line_total_matches_quantity_price",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sale_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("sales.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("products.id"),
        nullable=False,
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    selling_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    cost_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    line_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    sale: Mapped[Sale] = relationship(back_populates="sale_details")
    product: Mapped[Product] = relationship(back_populates="sale_details")


class Payment(Base):
    __tablename__ = "payments"

    __table_args__ = (
        CheckConstraint(
            "(sale_id IS NOT NULL) <> (purchase_id IS NOT NULL)",
            name="one_payment_one_transaction",
        ),
        CheckConstraint("(amount > 0)", name="payment_amount_positive"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sale_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("sales.id"),
        nullable=True,
        unique=True,
    )
    purchase_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("purchases.id"),
        nullable=True,
        unique=True,
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    method: Mapped[PaymentMethod] = mapped_column(
        SAEnum(PaymentMethod),
        nullable=False,
    )
    paid_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )
    note: Mapped[str | None] = mapped_column(Text, nullable=True)

    sale: Mapped[Sale | None] = relationship(back_populates="payment")
    purchase: Mapped[Purchase | None] = relationship(back_populates="payment")
    user: Mapped[User] = relationship(back_populates="payment")


class StockMovement(Base):
    __tablename__ = "stock_movements"

    __table_args__ = (
        CheckConstraint(
            "(sale_id IS NOT NULL) <> (purchase_id IS NOT NULL)",
            name="one_stock_movement_one_transaction",
        ),
        CheckConstraint(
            "(quantity_change > 0)",
            name="quantity_amount_positive",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("products.id"),
        nullable=False,
    )
    movement_type: Mapped[StockMovementType] = mapped_column(
        SAEnum(StockMovementType),
        nullable=False,
    )
    quantity_change: Mapped[int] = mapped_column(Integer, nullable=False)
    sale_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("sales.id"),
        nullable=True,
    )
    purchase_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("purchases.id"),
        nullable=True,
    )
    reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
