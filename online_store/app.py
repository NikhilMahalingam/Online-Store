from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template
from db import db, Products, Customers, Orders, OrderItems
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URI=os.getenv('DATABASE_URI')


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

    
@app.route('/store')
def store():
    products = Products.query.all()
    return render_template('store.html', products=products)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cart')
def cart():
    return render_template('cart.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

