from fastapi import FastAPI

from backend.routers import (
    auth,
    categories,
    customers,
    inventory,
    products,
    purchases,
    sales,
    suppliers,
    users,
)

app = FastAPI()

app.include_router(auth.router)
app.include_router(categories.router)
app.include_router(customers.router)
# app.include_router(payments.router)
app.include_router(products.router)
app.include_router(purchases.router)
app.include_router(sales.router)
app.include_router(suppliers.router)
app.include_router(users.router)
app.include_router(inventory.router)
