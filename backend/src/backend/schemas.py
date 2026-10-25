from datetime import date, datetime
from decimal import Decimal

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)

from backend.enums import (
    PaymentMethod,
    PaymentStatus,
    PurchaseStatus,
    Role,
    StockMovementType,
)


class Token(BaseModel):
    access_token: str
    token_type: str


class UserBase(BaseModel):
    username: str = Field(min_length=1, max_length=20)
    email: EmailStr = Field(max_length=50)
    name: str = Field(min_length=1, max_length=20)
    phone: str = Field(
        min_length=12,
        max_length=12,
        pattern=r"^92[0-9]{10}$",
    )
    role: Role
    status: bool = True

    @field_validator("phone", mode="before")
    @classmethod
    def normalize_phone(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.removeprefix("+")


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=255)


class UserResponse(UserBase):
    id: int
    last_login_at: datetime | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=1, max_length=20)
    email: EmailStr | None = Field(default=None, max_length=50)
    name: str | None = Field(default=None, min_length=1, max_length=20)
    phone: str | None = Field(
        default=None,
        min_length=12,
        max_length=12,
        pattern=r"^92[0-9]{10}$",
    )
    role: Role | None = None
    status: bool | None = None
    password: str | None = Field(
        default=None,
        min_length=8,
        max_length=255,
    )

    @field_validator("phone", mode="before")
    @classmethod
    def normalize_phone(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.removeprefix("+")


class CategoryBase(BaseModel):
    name: str = Field(min_length=1, max_length=15)
    description: str = Field(max_length=255)


class CategoryCreate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=15)
    description: str | None = Field(default=None, max_length=255)


class SupplierBase(BaseModel):
    name: str = Field(min_length=1, max_length=20)
    contact_person: str = Field(min_length=1, max_length=20)
    email: EmailStr = Field(max_length=50)
    phone: str = Field(
        min_length=12,
        max_length=12,
        pattern=r"^92[0-9]{10}$",
    )
    address: str = Field(min_length=1, max_length=100)
    status: bool = True

    @field_validator("phone", mode="before")
    @classmethod
    def normalize_phone(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.removeprefix("+")


class SupplierCreate(SupplierBase):
    pass


class SupplierResponse(SupplierBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SupplierUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=20)
    contact_person: str | None = Field(default=None, min_length=1, max_length=20)
    email: EmailStr | None = Field(default=None, max_length=50)
    phone: str | None = Field(
        default=None,
        min_length=12,
        max_length=12,
        pattern=r"^92[0-9]{10}$",
    )
    address: str | None = Field(default=None, min_length=1, max_length=100)
    status: bool | None = None

    @field_validator("phone", mode="before")
    @classmethod
    def normalize_phone(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.removeprefix("+")


class ProductBase(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    description: str = Field(max_length=150)
    category_id: int
    supplier_id: int
    cost_price: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    selling_price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    minimum_stock_lvl: int = Field(ge=0)
    status: bool = True


class ProductCreate(ProductBase):
    pass


class ProductResponse(ProductBase):
    id: int
    product_code: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=50)
    description: str | None = Field(default=None, max_length=150)
    category_id: int | None = None
    supplier_id: int | None = None
    cost_price: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=12,
        decimal_places=2,
    )
    selling_price: Decimal | None = Field(
        default=None,
        gt=0,
        max_digits=12,
        decimal_places=2,
    )
    minimum_stock_lvl: int | None = Field(default=None, ge=0)
    status: bool | None = None


class InventoryResponse(BaseModel):
    product_id: int
    quantity_on_hand: int
    updated_at: datetime
    product: ProductResponse

    model_config = ConfigDict(from_attributes=True)


class CustomerBase(BaseModel):
    name: str = Field(min_length=1, max_length=20)
    email: EmailStr | None = Field(default=None, max_length=50)
    phone: str | None = Field(
        default=None,
        min_length=12,
        max_length=12,
        pattern=r"^92[0-9]{10}$",
    )
    address: str | None = Field(default=None, max_length=100)
    status: bool = True

    @field_validator("phone", mode="before")
    @classmethod
    def normalize_phone(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.removeprefix("+")


class CustomerCreate(CustomerBase):
    pass


class CustomerResponse(CustomerBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CustomerUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=20)
    email: EmailStr | None = Field(default=None, max_length=50)
    phone: str | None = Field(
        default=None,
        min_length=12,
        max_length=12,
        pattern=r"^92[0-9]{10}$",
    )
    address: str | None = Field(default=None, max_length=100)
    status: bool | None = None

    @field_validator("phone", mode="before")
    @classmethod
    def normalize_phone(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.removeprefix("+")


class PurchaseDetailBase(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)
    unit_price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)


class PurchaseDetailCreate(PurchaseDetailBase):
    pass


class PurchaseDetailResponse(PurchaseDetailBase):
    id: int
    purchase_id: int
    line_total: Decimal = Field(gt=0, decimal_places=2)

    model_config = ConfigDict(from_attributes=True)


class PurchaseDetailUpdate(BaseModel):
    product_id: int | None = None
    quantity: int | None = Field(default=None, gt=0)
    unit_price: Decimal | None = Field(
        default=None,
        gt=0,
        max_digits=12,
        decimal_places=2,
    )


class PurchaseBase(BaseModel):
    reference_number: str = Field(min_length=1, max_length=50)
    purchase_date: date
    supplier_id: int
    discount: Decimal = Field(
        default=Decimal("0.00"), ge=0, decimal_places=2, max_digits=12
    )
    amount_paid: Decimal = Field(ge=0, decimal_places=2)
    notes: str | None = None


class PurchaseCreate(PurchaseBase):
    purchase_details: list[PurchaseDetailCreate] = Field(min_length=1)


class PurchaseResponse(PurchaseBase):
    id: int
    user_id: int
    subtotal: Decimal = Field(ge=0, decimal_places=2)
    total: Decimal = Field(ge=0, decimal_places=2)
    payment_status: PaymentStatus
    purchase_status: PurchaseStatus
    created_at: datetime
    purchase_details: list[PurchaseDetailResponse] = Field(min_length=1)

    model_config = ConfigDict(from_attributes=True)


class PurchaseUpdate(BaseModel):
    """Only fields that don't affect stock or totals.

    Lines, supplier, discount and status are fixed once a purchase is posted;
    to undo a purchase use POST /purchases/{id}/cancel. Unknown fields are
    rejected (422) instead of being silently ignored.
    """

    model_config = ConfigDict(extra="forbid")

    reference_number: str | None = Field(default=None, min_length=1, max_length=50)
    purchase_date: date | None = None
    amount_paid: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=12,
        decimal_places=2,
    )
    notes: str | None = None

    @model_validator(mode="after")
    def reject_null_non_nullable_fields(self):
        for field_name in self.model_fields_set:
            if getattr(self, field_name) is None and field_name != "notes":
                raise ValueError(f"{field_name} cannot be null")
        return self


class SaleDetailBase(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)
    selling_price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)


class SaleDetailCreate(SaleDetailBase):
    pass


class SaleDetailResponse(SaleDetailBase):
    id: int
    sale_id: int
    line_total: Decimal = Field(gt=0, decimal_places=2)

    model_config = ConfigDict(from_attributes=True)


class SaleDetailUpdate(BaseModel):
    product_id: int | None = None
    quantity: int | None = Field(default=None, gt=0)
    selling_price: Decimal | None = Field(
        default=None,
        gt=0,
        decimal_places=2,
    )


class SaleBase(BaseModel):
    invoice_number: str = Field(min_length=1, max_length=50)
    sale_date: date
    customer_id: int
    discount: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        max_digits=12,
        decimal_places=2,
    )
    amount_paid: Decimal = Field(ge=0, max_digits=12, decimal_places=2)


class SaleCreate(SaleBase):
    sale_details: list[SaleDetailCreate] = Field(min_length=1)


class SaleResponse(SaleBase):
    id: int
    user_id: int
    subtotal: Decimal = Field(ge=0, decimal_places=2)
    total: Decimal = Field(ge=0, decimal_places=2)
    payment_status: PaymentStatus
    sale_details: list[SaleDetailResponse] = Field(min_length=1)

    model_config = ConfigDict(from_attributes=True)


class SaleUpdate(BaseModel):
    """Only fields that don't affect stock or totals.

    Sale lines and discount are fixed once a sale is created (stock has
    already been deducted). Unknown fields are rejected (422).
    """

    model_config = ConfigDict(extra="forbid")

    invoice_number: str | None = Field(default=None, min_length=1, max_length=50)
    sale_date: date | None = None
    customer_id: int | None = None
    amount_paid: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=12,
        decimal_places=2,
    )


class PaymentBase(BaseModel):
    amount: Decimal = Field(gt=0, decimal_places=2)
    method: PaymentMethod
    note: str | None = None


class PaymentCreate(PaymentBase):
    sale_id: int | None = None
    purchase_id: int | None = None

    @model_validator(mode="after")
    def validate_transaction_reference(self):
        if (self.sale_id is None) == (self.purchase_id is None):
            raise ValueError("Exactly one of sale_id or purchase_id must be provided.")
        return self


class PaymentResponse(PaymentBase):
    id: int
    user_id: int
    paid_at: datetime
    sale_id: int | None = None
    purchase_id: int | None = None

    model_config = ConfigDict(from_attributes=True)


class PaymentUpdate(BaseModel):
    amount: Decimal | None = Field(
        default=None,
        gt=0,
        decimal_places=2,
    )
    method: PaymentMethod | None = None
    note: str | None = None


class StockMovementBase(BaseModel):
    product_id: int
    movement_type: StockMovementType
    quantity_change: int = Field(gt=0)
    reason: str | None = Field(default=None, max_length=255)


class StockMovementCreate(StockMovementBase):
    sale_id: int | None = None
    purchase_id: int | None = None
    user_id: int

    @model_validator(mode="after")
    def validate_transaction_reference(self):
        if (self.sale_id is None) == (self.purchase_id is None):
            raise ValueError("Exactly one of sale_id or purchase_id must be provided")
        return self


class StockMovementResponse(StockMovementBase):
    id: int
    user_id: int
    sale_id: int | None = None
    purchase_id: int | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StockMovementUpdate(BaseModel):
    movement_type: StockMovementType | None = None
    quantity_change: int | None = Field(default=None, gt=0)
    reason: str | None = Field(default=None, max_length=255)
