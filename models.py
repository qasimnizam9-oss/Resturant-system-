from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin

db = SQLAlchemy()

# --- AUTHENTICATION ---

class User(db.Model, UserMixin):
    """Staff and Admin users who can access the dashboard"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default='staff') # Options: staff, admin

# --- MENU ARCHITECTURE ---

class Category(db.Model):
    """Organizes dishes into groups (e.g., Starters, Mains, Desserts)"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    items = db.relationship('MenuItem', backref='category', lazy=True)

class MenuItem(db.Model):
    """The actual dishes available for purchase"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(255))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    
    # FIXED: Added cascade to prevent IntegrityError when deleting dishes
    order_entries = db.relationship('OrderItem', backref='menu_item', cascade="all, delete-orphan", lazy=True)

# --- RESERVATION SYSTEM ---

class Reservation(db.Model):
    """Stores customer table bookings"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    date = db.Column(db.String(20), nullable=False) 
    time = db.Column(db.String(20), nullable=False)
    guests = db.Column(db.Integer, nullable=False)
    special_requests = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# --- ORDER TRACKING ---

class Order(db.Model):
    """The main record for a customer's meal purchase"""
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), default="Guest")
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='Pending') 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Link to the specific items within this order
    items = db.relationship('OrderItem', backref='order', cascade="all, delete-orphan", lazy=True)

class OrderItem(db.Model):
    """A junction table connecting specific MenuItems to a single Order"""
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_item.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)