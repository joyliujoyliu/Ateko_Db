from decimal import Decimal
from pydantic import BaseModel
from typing import List
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session

class OrderItemInput(BaseModel):
    product_id: int
    quantity: int

class OrderInput(BaseModel):
    customer_id: int
    items: List[OrderItemInput]


@app.post("/orders")
def create_order(data: OrderInput, db: Session = Depends(get_db)):

    try:
        with db.begin():  # 🔥 TRANSACTION START

            # 1️⃣ Validate customer
            customer = db.query(Customer).filter_by(id=data.customer_id).first()
            if not customer:
                raise HTTPException(status_code=404, detail="Customer not found")

            if not data.items:
                raise HTTPException(status_code=400, detail="Order must contain items")

            total = Decimal("0.00")

            # 5️⃣ Insert order FIRST (so we get order.id)
            order = Order(
                customer_id=data.customer_id,
                status="created",
                total_amount=Decimal("0.00")
            )
            db.add(order)
            db.flush()

            for item in data.items:

                # 2️⃣ Validate product
                product = db.query(Product).filter_by(id=item.product_id).first()
                if not product:
                    raise HTTPException(status_code=404, detail="Product not found")

                # 3️⃣ Check stock
                if product.stock < item.quantity:
                    raise HTTPException(status_code=400, detail="Insufficient stock")

                # 4️⃣ Deduct stock
                product.stock -= item.quantity

                # 7️⃣ Calculate total
                line_total = product.price * item.quantity
                total += line_total

                # 6️⃣ Insert order item
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=item.quantity,
                    unit_price=product.price
                )
                db.add(order_item)

            order.total_amount = total

        # 🔥 AUTO COMMIT if no errors

        return {
            "order_id": order.id,
            "total": float(total)
        }

    except HTTPException:
        raise  # keep your original errors

    except Exception as e:
        db.rollback()  # 🔥 safety rollback
        raise HTTPException(status_code=500, detail=str(e))