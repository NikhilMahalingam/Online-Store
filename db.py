from app import db

#Basic SQLAlchemy setup, we can expand on this, I haven't tested yet

class Product(db.Model):
    __tablename__ = 'products'
    product_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    

with app.app_context():
    db.create_all()
