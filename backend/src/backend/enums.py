from enum import Enum


class Role(str, Enum):
    OWNER = "owner"
    USER = "user"


class PurchaseStatus(str, Enum):
    DRAFT = "draft"
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PaymentStatus(str, Enum):
    UNPAID = "unpaid"
    PARTIAL = "partial"
    PAID = "paid"


class PaymentMethod(str, Enum):
    CASH = "cash"
    CARD = "card"


class StockMovementType(str, Enum):
    PURCHASE = "purchase"
    SALE = "sale"
