from fastapi import FastAPI

from .routers import (
    categories,
    products,
    suppliers,
    users,
)

app = FastAPI()

app.include_router(categories.router)
# app.include_router(customers.router)
# app.include_router(payments.router)
app.include_router(products.router)
# app.include_router(purchases.router)
# app.include_router(purchases_details.router)
# app.include_router(sales.router)
# app.include_router(sales_details.router)
# app.include_router(stockmovements.router)
app.include_router(suppliers.router)
app.include_router(users.router)
