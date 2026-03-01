from sqlite3 import OperationalError

from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy import func, text, and_, or_
from db import get_db
from models import Product, Customer, Order, OrderItem
from typing import Optional  # ← Add this import
from datetime import datetime
from pydantic import BaseModel
from typing import List
from decimal import Decimal
from pydantic import BaseModel, Field


# 👇 DEFINE THESE FIRST
class OrderItemInput(BaseModel):
    product_id: int
    quantity: int

class OrderInput(BaseModel):
    customer_id: int
    items: List[OrderItemInput]



class PurchaseRequest(BaseModel):
    # qty: int = Field(..., ge=1)
    product_id: int
    quantity: int

app = FastAPI(title="Ateko DB")

@app.get("/")
def root():
    return {"message": "Ateko Mini Commerce Backend is running"}



# -----------------------
# Endpoint 1: ORM example
# -----------------------
@app.get("/products")
def list_products(
    min_price: float | None = None,
    max_price: float | None = None,
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    query = db.query(Product)

    if active_only:
        query = query.filter(Product.is_active == 1)

    if min_price is not None:
        query = query.filter(Product.price >= min_price)

    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    products = query.all()

    return [
        {
            "id": p.id,
            "name": p.name,
            "price": float(p.price),
            "stock": p.stock
        }
        for p in products
    ]


# offset
@app.get("/products/paged")
def paged_products(
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    products = (
        db.query(Product)
        .order_by(Product.id)
        .offset(offset)
        .limit(limit)
        .all()
    )

    return [
        {
            "id": p.id,
            "name": p.name,
            "price": float(p.price)
        }
        for p in products
    ]


#cursor
@app.get("/products/cursor")
def cursor_products(
    limit: int = 5,
    cursor: str | None = None,
    db: Session = Depends(get_db)
):
    query = db.query(Product).order_by(Product.created_at, Product.id)

    if cursor:
        try:
            created_at_str, id_str = cursor.split("|")
            created_at = datetime.fromisoformat(created_at_str)
            id_int = int(id_str)
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="Cursor must be format: 2026-03-01T15:20:33.123456|9"
            )

        query = query.filter(
            or_(
                Product.created_at > created_at,
                and_(
                    Product.created_at == created_at,
                    Product.id > id_int
                )
            )
        )

    products = query.limit(limit).all()

    next_cursor = None
    if products:
        last = products[-1]
        next_cursor = f"{last.created_at.isoformat()}|{last.id}"

    return {
        "next_cursor": next_cursor,
        "items": [
            {
                "id": p.id,
                "name": p.name,
                "price": float(p.price)
            }
            for p in products
        ]
    }


#post order
from fastapi import Query

@app.post("/orders/query")
def create_order_query(
    customer_id: int = Query(..., description="Customer ID"),
    product_id: List[int] = Query(..., description="Product IDs, repeatable"),
    quantity: List[int] = Query(..., description="Quantities matching product IDs"),
    db: Session = Depends(get_db)
):
    # Validate that product_id and quantity lists match
    if len(product_id) != len(quantity):
        raise HTTPException(status_code=400, detail="product_id and quantity must have the same length")

    # 1️⃣ Check if customer exists
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # 2️⃣ Fetch all products in the order
    products = db.query(Product).filter(Product.id.in_(product_id), Product.is_active == 1).all()
    products_dict = {p.id: p for p in products}

    # 3️⃣ Validate stock
    for pid, qty in zip(product_id, quantity):
        if pid not in products_dict:
            raise HTTPException(status_code=404, detail=f"Product {pid} not found or inactive")
        if qty > products_dict[pid].stock:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough stock for product {products_dict[pid].name}"
            )

    # 4️⃣ Calculate total amount
    total_amount = sum(products_dict[pid].price * qty for pid, qty in zip(product_id, quantity))

    # 5️⃣ Create the order
    new_order = Order(
        customer_id=customer_id,
        status="created",
        total_amount=total_amount,
        created_at=datetime.utcnow()
    )
    db.add(new_order)
    db.flush()  # get new_order.id

    # 6️⃣ Create order items and update stock
    for pid, qty in zip(product_id, quantity):
        product = products_dict[pid]
        order_item = OrderItem(
            order_id=new_order.id,
            product_id=pid,
            quantity=qty,
            unit_price=product.price
        )
        db.add(order_item)
        product.stock -= qty

    db.commit()
    db.refresh(new_order)

    return {
        "order_id": new_order.id,
        "customer_id": new_order.customer_id,
        "total_amount": float(new_order.total_amount),
        "items": [
            {
                "product_id": pid,
                "quantity": qty,
                "unit_price": float(products_dict[pid].price)
            }
            for pid, qty in zip(product_id, quantity)
        ],
        "status": new_order.status
    }

# ------------------------------------------------------------

@app.post("/orders")
def create_order(data: OrderInput, db: Session = Depends(get_db)):
    # 1️⃣ Check if customer exists
    customer = db.query(Customer).filter(Customer.id == data.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # 2️⃣ Fetch all products in the order
    product_ids = [item.product_id for item in data.items]
    products = db.query(Product).filter(Product.id.in_(product_ids), Product.is_active == 1).all()
    products_dict = {p.id: p for p in products}

    # 3️⃣ Validate stock
    for item in data.items:
        if item.product_id not in products_dict:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found or inactive")
        if item.quantity > products_dict[item.product_id].stock:
            raise HTTPException(
                status_code=400, 
                detail=f"Not enough stock for product {products_dict[item.product_id].name}"
            )

    # 4️⃣ Calculate total amount
    total_amount = sum(products_dict[item.product_id].price * item.quantity for item in data.items)

    # 5️⃣ Create the order
    new_order = Order(
        customer_id=data.customer_id,
        status="created",
        total_amount=total_amount,
        created_at=datetime.utcnow()
    )
    db.add(new_order)
    db.flush()  # get new_order.id before committing

    # 6️⃣ Create order items and update stock
    for item in data.items:
        product = products_dict[item.product_id]
        order_item = OrderItem(
            order_id=new_order.id,
            product_id=product.id,
            quantity=item.quantity,
            unit_price=product.price
        )
        db.add(order_item)

        # Update stock
        product.stock -= item.quantity

    # 7️⃣ Commit everything
    db.commit()
    db.refresh(new_order)

    return {
        "order_id": new_order.id,
        "customer_id": new_order.customer_id,
        "total_amount": float(new_order.total_amount),
        "items": [
            {
                "product_id": item.product_id,
                "quantity": item.quantity,
                "unit_price": float(products_dict[item.product_id].price)
            } 
            for item in data.items
        ],
        "status": new_order.status
    }

# # ---------------------------------------------------------------------------------------

# @app.post("/products/{product_id}/{quantity}/purchase")
# def purchase_safe(product_id: int, quantity :int,  body: PurchaseRequest, db: Session = Depends(get_db)):
#     try:
#         with db.begin():
#             p = (
#                 db.query(Product)
#                 .filter(Product.id == product_id)
#                 .with_for_update()
#                 .one_or_none()
#             )
#             if not p:
#                 raise HTTPException(status_code=404, detail="product not found")

#             if p.stock < quantity:
#                 raise HTTPException(status_code=409, detail="insufficient stock")

#             p.stock -= quantity
#             db.add(p)

#         return {"ok": True, "product_id": int(product_id), "remaining_stock": int(p.stock)}

#     except OperationalError:
#         # lock wait timeout / deadlock under high contention
#         raise HTTPException(status_code=409, detail="conflict, retry")
    


# ------------------------------------------------------------------------------

# @app.post("/orders")
# def create_order( product_id: int, quantity :int, customer_id: int ,  body: PurchaseRequest ,
#                     data: OrderInput,
#                     db: Session = Depends(get_db)):

#     # 1️⃣ Validate customer existence
#     customer = db.query(Customer).filter_by(id= customer_id).first()
#     if not customer:
#         raise HTTPException(status_code=404, detail="Customer not found")

#     if not data.items:
#         raise HTTPException(status_code=400, detail="Order must contain items")

#     # 5️⃣ Create order record
#     order = Order(
#         customer_id=customer_id,
#         status="created",
#         total_amount=Decimal("0.00")
#     )
#     db.add(order)
#     # db.flush()

#     total = Decimal("0.00")

#     for item in data.items:

#         # 2️⃣ Validate product existence
#         product = db.query(Product).filter_by(id=product_id).first()
#         if not product:
#             raise HTTPException(status_code=404, detail="Product not found")

#         # 3️⃣ Check stock availability
#         if product.stock < item.quantity:
#             raise HTTPException(status_code=400, detail="Insufficient stock")

#         # 4️⃣ Deduct stock
#         product.stock -= item.quantity

#         # 7️⃣ Calculate total safely
#         line_total = product.price * item.quantity
#         total += line_total

#         # 6️⃣ Create order items
#         order_item = OrderItem(
#             order_id=order.id,
#             product_id=product.id,
#             quantity=item.quantity,
#             unit_price=product.price
#         )

#         db.add(order_item)

#     order.total_amount = total
#     db.commit()

#     return {
#         "order_id": order.id,
#         "total": float(total)
#     }

# #OMR version



@app.get("/analytics/top-products/orm")
def top_products_orm(db: Session = Depends(get_db)):

     results = (
         db.query(
             Product.id,
             Product.name,
             func.sum(OrderItem.quantity).label("total_quantity"),
             func.sum(OrderItem.quantity * OrderItem.unit_price).label("total_revenue")
         )
         .join(OrderItem)
         .group_by(Product.id)
         .order_by(func.sum(OrderItem.quantity * OrderItem.unit_price).desc())
         .limit(5)
         .all()
     )

     return [
         {
             "product_id": r.id,
             "product_name": r.name,
             "total_quantity_sold": int(r.total_quantity),
             "total_revenue": float(r.total_revenue)
         }
         for r in results
     ]

 # raw sql  version
@app.get("/analytics/top-products/sql")
def top_products_sql(db: Session = Depends(get_db)):

     sql = text("""
         SELECT
             p.id AS product_id,
             p.name AS product_name,
             SUM(oi.quantity) AS total_quantity_sold,
             SUM(oi.quantity * oi.unit_price) AS total_revenue
         FROM order_items oi
         JOIN products p ON p.id = oi.product_id
         GROUP BY p.id, p.name
         ORDER BY total_revenue DESC
         LIMIT 5
     """)

     rows = db.execute(sql).mappings().all()
     return rows
