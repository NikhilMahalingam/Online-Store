from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, redirect, url_for, flash, session, g
from db import db, Products, Customers, Orders, OrderItems, OrderStatus
from dotenv import load_dotenv
import os
from datetime import date
from sqlalchemy import desc, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker, scoped_session
from supabase import create_client, Client
from utils import login_required


load_dotenv()

DATABASE_URI=os.getenv('DATABASE_URI')
SUPABASE_URL=os.getenv('SUPABASE_URL')
SUPABASE_API_KEY=os.getenv('SUPABASE_API_KEY')


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '\x93V\xa7\\\xdb\xb1\xd4d\xa9\x0f0\xe0\xae2p\tc\x079>\xd5*S\x07'
db.init_app(app)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_API_KEY)

#Routes for Pages

def get_customer_id_from_email(email):
    customer = db.session.query(Customers).filter_by(email=email).first()
    return customer.customer_id if customer else None

def get_cart_items(order):
    cart_items = []
    if order:
        cart_items = OrderItems.query.filter_by(order_id=order.order_id).all()
    return cart_items

def get_trending_products(limit=3):
    # products from most recent orders
    recent_orders = Orders.query.order_by(Orders.order_date.desc()).limit(limit).all()
    products_with_dates = []
    for order in recent_orders:
        for order_item in order.items:
            product = Products.query.get(order_item.product_id)
            if product:
                products_with_dates.append((product, order.order_date))

    sorted_products_with_dates = sorted(products_with_dates, key=lambda x: x[1], reverse=True)

    trending_products = []
    for product_with_date in sorted_products_with_dates[:limit]:
        product, purchase_date = product_with_date
        trending_products.append((product, purchase_date))

    return trending_products

# Global state
@app.before_request
def before_request():
    user_email = session.get('user_email')
    customer_id = get_customer_id_from_email(user_email)
    cart_order = Orders.query.filter_by(customer_id=customer_id, status='cart').first()
    cart_items = get_cart_items(cart_order)
    total_items = 0
    for cart_item in cart_items:
        total_items += cart_item.quantity

    g.items_in_cart = total_items
    g.current_user = user_email

# Define a custom Jinja filter for date format
def date_format(date):
    return date.strftime('%a, %b %d')

app.jinja_env.filters['date_format'] = date_format

# Routes for Pages
@app.route('/store')
def store():
    query = request.args.get('query')
    sort_by = request.args.get('sort')
    filtered_products = Products.query.all()

    if query:
        filtered_products = [product for product in filtered_products if query.lower() in product.name.lower()]

    if sort_by == 'stock':
        filtered_products.sort(key=lambda x: x.stock_quantity, reverse=True)
    elif sort_by == 'price-low':
        filtered_products.sort(key=lambda x: x.price)
    elif sort_by == 'price-high':
        filtered_products.sort(key=lambda x: x.price, reverse=True)
    
    # Debug: Print product details to verify
    for product in filtered_products:
        print(product.name, product.slug)

    return render_template('store.html', products=filtered_products)


@app.route('/product/<slug>')
def product_detail(slug):
    product = Products.query.filter_by(slug=slug).first()
    if product:
        return render_template('product_detail.html', product=product)
    else:
        flash('Product not found.', 'error')
        return redirect(url_for('store'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/view_cart')
def view_cart():
    user_email = session.get('user_email')
    customer_id = get_customer_id_from_email(user_email)
    cart_order = Orders.query.filter_by(customer_id=customer_id, status='cart').first()

    if cart_order:
        cart_items = OrderItems.query.filter_by(order_id=cart_order.order_id).all()
    else:
        cart_items = []

    return render_template('view_cart.html', cart_items=cart_items, total=cart_order.total_amount if cart_order else 0)

@app.route('/sell', methods=['GET', 'POST'])
def sell():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = float(request.form['price'])
        stock_quantity = int(request.form['stock_quantity'])

        sql = """
            INSERT INTO products (name, description, price, stock_quantity)
            VALUES (:name, :description, :price, :stock_quantity)
        """

        try:
            db.session.execute(text(sql), {
                'name': name,
                'description': description,
                'price': price,
                'stock_quantity': stock_quantity
            })
            db.session.commit()

            flash('Product successfully listed!', 'success')
            return redirect(url_for('store'))
        except IntegrityError as e:
            db.session.rollback()
            flash('An error occurred while listing the product. Please try again later.', 'danger')
            return redirect(url_for('store'))
    
    # If it's just GET, give the HTML
    return render_template('sell.html')

@app.route('/orders')
def orders():
    user_email = session.get('user_email')
    customer_id = get_customer_id_from_email(user_email)
    orders = Orders.query.filter_by(customer_id=customer_id).order_by(desc(Orders.order_id)).all()

    # We also need the product and status information from the order
    for order in orders:
        order_items = order.items
        for item in order_items:
            product = Products.query.get(item.product_id)
            item.product_name = product.name 
            item.price = product.price 

    return render_template('orders.html', orders=orders)

@app.route('/checkout')
def checkout():
    user_email = session.get('user_email')
    customer_id = get_customer_id_from_email(user_email)
    order = Orders.query.filter_by(customer_id=customer_id, status='cart').first()
    order_items = order.items

    trending_products = get_trending_products(2)

    for item in order_items:
        product = Products.query.get(item.product_id)
        item.product_name = product.name 
        item.price = product.price 

    return render_template('checkout.html', order=order, trending_products=trending_products)


#Routes for Functions
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            result = supabase.auth.sign_up({'email':email, 'password':password})
            print("Supabase result:", result) 

            if result:
                sql = """
                INSERT INTO customers (first_name, last_name, email, phone_number, address, city, state, zip_code)
                VALUES (:first_name, :last_name, :email, :phone_number, :address, :city, :state, :zip_code);
                """
                db.session.execute(text(sql), {
                    'first_name': request.form['first_name'],
                    'last_name': request.form['last_name'],
                    'email': email,
                    'phone_number': request.form['phone_number'],
                    'address': request.form['address'],
                    'city': request.form['city'],
                    'state': request.form['state'],
                    'zip_code': request.form['zip_code']
                })
                db.session.commit()

                flash('Registration successful! Please log in.', 'success')
                return redirect(url_for('login'))
            else:
                flash('Failed to register with Supabase. Please try again.', 'error')
                return redirect(url_for('register'))

        except Exception as e:
            db.session.rollback()
            flash(f'Registration failed: {str(e)}', 'error')
            return redirect(url_for('register'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        response = supabase.auth.sign_in_with_password({"email":email, "password":password})
        if response:
            session_obj = supabase.auth.get_session()
            if session_obj:
                    access_token = session_obj.access_token
                    session['access_token'] = access_token 
                    flash('Login successful!', 'success')

            return redirect(url_for('index'))
        else:
                flash('Login failed. Please check your credentials.', 'danger')
                return redirect(url_for('login'))
    return render_template('login.html')



Session = scoped_session(sessionmaker(autoflush=False))

@app.route('/cart', methods=['POST'])
def add_to_cart():
    current_page = request.form.get('current_page')
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
        user_email = session.get('user_email')
        customer_id = get_customer_id_from_email(user_email)

        order = Orders.query.filter_by(customer_id=customer_id, status='cart').first()
        if not order:
            order = Orders(
                customer_id=customer_id,
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
        return redirect(url_for(current_page))

    except Exception as e:  
        db.session.rollback()
        flash(str(e), "error")  
        return redirect(url_for(current_page))

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

@app.route('/confirm_order', methods=['POST'])
def confirm_order():
    if request.method == 'POST':
        order_id = request.form['order_id']
        order = Orders.query.get(order_id)
        if order:
            order_items = OrderItems.query.filter_by(order_id=order_id).all()

            # Check if stock is sufficient for each order item
            for order_item in order_items:
                product = Products.query.get(order_item.product_id)
                if not product or product.stock_quantity < order_item.quantity:
                    flash(f"Error: Not enough stock for {order_item.quantity} units of {product.name}. There are only {product.stock_quantity} units available.", 'danger')
                    return redirect(url_for('checkout'))
                
            # If not we're good to complete the transaction
            order.status = OrderStatus.completed

            # Decrease the quantity of each item in the order
            for order_item in order_items:
                product = Products.query.get(order_item.product_id)
                product.stock_quantity -= order_item.quantity

            db.session.commit()
        flash("Your order has been placed!", 'success')
    return redirect(url_for('orders'))



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

