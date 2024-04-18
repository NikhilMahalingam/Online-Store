from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Text, Date, DECIMAL, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum

db = SQLAlchemy()

class Products(db.Model):
    __tablename__ = 'products'
    product_id = db.Column(Integer, primary_key=True)
    name = db.Column(String(100), nullable=False)
    description = db.Column(Text, nullable=True)
    price = db.Column(DECIMAL(10, 2), nullable=False)
    stock_quantity = db.Column(Integer, nullable=False)
    order_items = relationship("OrderItems", back_populates="product")

class Customers(db.Model):
    __tablename__ = 'customers'
    customer_id = db.Column(Integer, primary_key=True)
    first_name = db.Column(String(50), nullable=False)
    last_name = db.Column(String(50), nullable=False)
    email = db.Column(String(100), nullable=False)
    phone_number = db.Column(String(20), nullable=False)
    address = db.Column(String(255), nullable=False)
    city = db.Column(String(100), nullable=False)
    state = db.Column(String(50), nullable=False)
    zip_code = db.Column(String(20), nullable=False)
    orders = relationship("Orders", back_populates="customer")

class OrderStatus(enum.Enum):
    cart = 'cart'
    pending = 'pending'
    completed = 'completed'

class Orders(db.Model):
    __tablename__ = 'orders'
    order_id = db.Column(Integer, primary_key=True)
    customer_id = db.Column(Integer, ForeignKey('customers.customer_id'))
    order_date = db.Column(Date)
    total_amount = db.Column(DECIMAL(10, 2))
    status = db.Column(Enum(OrderStatus))  # 3 States: Cart, Pending, Completed
    customer = relationship("Customers", back_populates="orders")
    items = relationship("OrderItems", back_populates="order")

class OrderItems(db.Model):
    __tablename__ = 'order_items'
    order_item_id = db.Column(Integer, primary_key=True)
    order_id = db.Column(Integer, ForeignKey('orders.order_id'))
    product_id = db.Column(Integer, ForeignKey('products.product_id'))
    quantity = db.Column(Integer)
    unit_price = db.Column(DECIMAL(10, 2))
    order = relationship("Orders", back_populates="items")
    product = relationship("Products", back_populates="order_items")
