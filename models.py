# models.py

from sqlalchemy import Column, BigInteger, String, Integer, DECIMAL, Enum, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from db import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(BigInteger, primary_key=True)
    name = Column(String(120), nullable=False)
    email = Column(String(180), nullable=False, unique=True)
    created_at = Column(DateTime)

    orders = relationship("Order", back_populates="customer")


class Product(Base):
    __tablename__ = "products"

    id = Column(BigInteger, primary_key=True)
    name = Column(String(160), nullable=False)
    price = Column(DECIMAL(10,2), nullable=False)
    stock = Column(Integer, nullable=False)
    is_active = Column(Integer, nullable=False)
    created_at = Column(DateTime)

    order_items = relationship("OrderItem", back_populates="product")


class Order(Base):
    __tablename__ = "orders"

    id = Column(BigInteger, primary_key=True)
    customer_id = Column(BigInteger, ForeignKey("customers.id"))
    status = Column(Enum("created", "paid", "cancelled"))
    total_amount = Column(DECIMAL(12,2))
    created_at = Column(DateTime)

    customer = relationship("Customer", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(BigInteger, primary_key=True)
    order_id = Column(BigInteger, ForeignKey("orders.id"))
    product_id = Column(BigInteger, ForeignKey("products.id"))
    quantity = Column(Integer)
    unit_price = Column(DECIMAL(10,2))

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")