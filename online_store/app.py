from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, redirect, url_for, flash
from db import db, Products, Customers, Orders, OrderItems
from dotenv import load_dotenv
import os
from datetime import date
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker, scoped_session

load_dotenv()

DATABASE_URI=os.getenv('DATABASE_URI')


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '\x93V\xa7\\\xdb\xb1\xd4d\xa9\x0f0\xe0\xae2p\tc\x079>\xd5*S\x07'
db.init_app(app)

    
@app.route('/store')
def store():
    products = Products.query.all()
    return render_template('store.html', products=products)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/view_cart')
def view_cart():
    customer_id = 1
    cart_order = Orders.query.filter_by(customer_id=customer_id, status='cart').first()

    if cart_order:
        cart_items = OrderItems.query.filter_by(order_id=cart_order.order_id).all()
    else:
        cart_items = []

    return render_template('view_cart.html', cart_items=cart_items, total=cart_order.total_amount if cart_order else 0)

Session = scoped_session(sessionmaker(autoflush=False))

@app.route('/cart', methods=['POST'])
def add_to_cart():
    session = Session()
    try:
        product_id = request.form.get('product_id')
        if not product_id:
            flash("No product specified.", "error")
            return redirect(url_for('store'))

        product = Products.query.get(product_id)
        if not product:
            flash("Product not found.", "error")
            return redirect(url_for('store'))

        quantity = int(request.form.get('quantity', 1))
        customer_id = 1  # Temporary for testing

        order = Orders.query.filter_by(customer_id=1, status='cart').first()
        if not order:
            order = Orders(
                customer_id=1,
                order_date=date.today(),
                total_amount=0.0, 
                status='cart'
            )
            db.session.add(order)

        
        order_item = OrderItems.query.filter_by(order_id=order.order_id, product_id=product_id).first()
        if order_item:
            order_item.quantity += quantity
        else:
            order_item = OrderItems(
                order_id=order.order_id,
                product_id=product_id,
                quantity=quantity,
                unit_price=product.price  
            )
            db.session.add(order_item)

        # Calculate total amount
        order.total_amount = sum(item.unit_price * item.quantity for item in order.items)
        db.session.commit()

        flash(f"{quantity}x {product.name} added to cart successfully!", 'success')
        return redirect(url_for('store'))

    except Exception as e:  
        db.session.rollback()
        flash(str(e), "error")  
        return redirect(url_for('store'))

@app.route('/delete_item/<int:order_item_id>', methods=['POST'])
def delete_item(order_item_id):
    try:
        order_item = OrderItems.query.get(order_item_id)
        if order_item:
            order = Orders.query.get(order_item.order_id)
            db.session.delete(order_item)
            db.session.commit()

            order.total_amount = sum(item.unit_price * item.quantity for item in order.items)
            db.session.commit()

            flash('Item deleted successfully!', 'success')
        else:
            flash('Item not found!', 'error')
    except Exception as e:
        db.session.rollback()
        flash(str(e), 'error')
    return redirect(url_for('view_cart'))



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

