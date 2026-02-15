from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
from models import db, MenuItem, Category, Reservation, Order, OrderItem, User
import os

# --- ADDED MODEL FOR CHATBOT ---
class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_message = db.Column(db.Text, nullable=False)
    bot_response = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

app = Flask(__name__)

# --- CONFIGURATION ---
app.secret_key = 'restaurant_secret_key_123' 
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'restaurant.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- EMAIL CONFIGURATION (SMTP) ---
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your-email@gmail.com' 
app.config['MAIL_PASSWORD'] = 'your-app-password'    

mail = Mail(app)
db.init_app(app)

# --- LOGIN MANAGER SETUP ---
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- DATABASE INITIALIZATION & AUTO-SEEDING ---
with app.app_context():
    db.create_all()
    
    if not User.query.filter_by(username='admin').first():
        print("Creating default admin account...")
        default_admin = User(username='admin', password='password123', role='admin')
        db.session.add(default_admin)
        db.session.commit()

    if not Category.query.first():
        print("Database empty. Injecting professional menu data...")
        starters = Category(name="Starters")
        mains = Category(name="Main Course")
        desserts = Category(name="Desserts")
        db.session.add_all([starters, mains, desserts])
        db.session.commit() 

        sample_dishes = [
            MenuItem(name="Truffle Mushroom Arancini", description="Risotto balls stuffed with mozzarella and truffle oil.", 
                     price=1250, image_url="https://images.unsplash.com/photo-1541529086526-db283c563270?w=500", category_id=starters.id),
            MenuItem(name="Grilled Atlantic Salmon", description="Fresh salmon fillet with lemon butter sauce and seasonal asparagus.", 
                     price=3500, image_url="https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?w=500", category_id=mains.id),
            MenuItem(name="Classic Ribeye Steak", description="Dry-aged beef served with garlic mash and red wine reduction.", 
                     price=4500, image_url="https://images.unsplash.com/photo-1546241072-48010ad28c2c?w=500", category_id=mains.id),
            MenuItem(name="Molten Chocolate Cake", description="Warm dark chocolate cake with a gooey center and vanilla bean ice cream.", 
                     price=850, image_url="https://images.unsplash.com/photo-1624353339130-975003666f7d?w=500", category_id=desserts.id)
        ]
        db.session.add_all(sample_dishes)
        db.session.commit()
        print("Seeding complete!")

# --- AUTHENTICATION ROUTES ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('admin'))
        else:
            flash('Invalid username or password')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# --- PUBLIC ROUTES ---

@app.route('/')
def index():
    dishes = MenuItem.query.limit(3).all()
    return render_template('index.html', dishes=dishes)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_msg = data.get("message")
    bot_res = "Thank you! Our concierge will get back to you soon. We've saved your request."
    
    try:
        new_chat = ChatMessage(user_message=user_msg, bot_response=bot_res)
        db.session.add(new_chat)
        db.session.commit()
        return jsonify({"response": bot_res})
    except Exception as e:
        return jsonify({"response": "Message received (offline)."}), 200

@app.route('/gallery/<category>')
def gallery_detail(category):
    gallery_data = {
        'kitchen': {
            'title': 'The Culinary Heart',
            'description': 'Where Qasim Nizam\'s master chefs craft every masterpiece with precision.',
            'images': [
                'https://images.unsplash.com/photo-1556910103-1c02745aae4d?w=800',
                'https://images.unsplash.com/photo-1583394838336-acd977736f90?w=800',
                'https://images.unsplash.com/photo-1600565193348-f74bd3c7ccdf?w=800'
            ]
        },
        'dining': {
            'title': 'Elegant Ambience',
            'description': 'Sophisticated seating designed for comfort and luxury.',
            'images': [
                'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=800',
                'https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=800',
                'https://images.unsplash.com/photo-1551632432-c735e7a0338b?w=800'
            ]
        },
        'food': {
            'title': 'Signature Dishes',
            'description': 'A visual feast of our most celebrated gourmet plates.',
            'images': [
                'https://images.unsplash.com/photo-1544025162-d76694265947?w=800',
                'https://images.unsplash.com/photo-1467003909585-2f8a72700288?w=800',
                'https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=800'
            ]
        }
    }
    
    data = gallery_data.get(category.lower())
    if not data:
        flash("Gallery category not found.")
        return redirect(url_for('index'))
        
    return render_template('gallery_detail.html', data=data)

@app.route('/menu')
def menu():
    items = MenuItem.query.all()
    categories = Category.query.all()
    return render_template('menu.html', items=items, categories=categories)

@app.route('/cart')
def cart():
    return render_template('cart.html')

@app.route('/reserve', methods=['GET', 'POST'])
def reserve():
    if request.method == 'POST':
        try:
            new_res = Reservation(
                name=request.form.get('name'),
                email=request.form.get('email'),
                phone=request.form.get('phone'),
                date=request.form.get('date'),
                time=request.form.get('time'),
                guests=int(request.form.get('guests')),
                special_requests=request.form.get('requests')
            )
            db.session.add(new_res)
            db.session.commit()
            return render_template('index.html', success="Table booked successfully!")
        except Exception as e:
            db.session.rollback()
            return f"Error saving reservation: {e}"
    return render_template('reserve.html')

@app.route('/checkout', methods=['POST'])
def checkout():
    data = request.get_json()
    cart_items = data.get('items') or data.get('cart', [])
    if not cart_items:
        return jsonify({"status": "error", "message": "Cart is empty"}), 400

    try:
        total = sum(float(item['price']) for item in cart_items)
        new_order = Order(total_amount=total, status='Pending')
        db.session.add(new_order)
        db.session.flush() 

        for item in cart_items:
            order_item = OrderItem(order_id=new_order.id, menu_item_id=item['id'], quantity=1)
            db.session.add(order_item)
        
        db.session.commit()
        return jsonify({"status": "success", "message": "Order placed successfully!", "order_id": new_order.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/success/<int:order_id>')
def success(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('success.html', order=order)

@app.route('/subscribe', methods=['POST'])
def subscribe():
    data = request.get_json()
    customer_email = data.get('email')
    
    if not customer_email:
        return jsonify({"status": "error", "message": "No email provided"}), 400

    try:
        msg = Message("Welcome to The Grand Bistro! 🥂",
                      sender=app.config['MAIL_USERNAME'],
                      recipients=[customer_email]) 
        
        msg.body = f"Thank you for joining our inner circle! Show this email for a 10% discount!"
        mail.send(msg)
        return jsonify({"status": "success", "message": "Successfully joined!"})
    except Exception as e:
        return jsonify({"status": "success", "message": "Thanks for joining our list!"})

# --- ADMIN ROUTES ---

@app.route('/admin')
@login_required
def admin():
    orders = Order.query.all()
    reservations = Reservation.query.all()
    return render_template('admin.html', orders=orders, reservations=reservations)

@app.route('/admin/orders')
@login_required
def admin_orders():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('admin_orders.html', orders=orders)

@app.route('/admin/reservations')
@login_required
def admin_reservations():
    reservations = Reservation.query.order_by(Reservation.created_at.desc()).all()
    return render_template('admin_reservations.html', reservations=reservations)

@app.route('/admin/menu')
@login_required
def admin_menu():
    menu_items = MenuItem.query.all()
    categories = Category.query.all()
    return render_template('admin_menu.html', menu_items=menu_items, categories=categories)

@app.route('/admin/menu/edit/<int:item_id>', methods=['GET', 'POST'])
@login_required
def edit_menu_item(item_id):
    item = MenuItem.query.get_or_404(item_id)
    if request.method == 'POST':
        item.name = request.form.get('name')
        item.description = request.form.get('description')
        item.price = float(request.form.get('price'))
        item.image_url = request.form.get('image_url')
        item.category_id = int(request.form.get('category_id'))
        db.session.commit()
        flash(f'Dish "{item.name}" updated successfully!')
        return redirect(url_for('admin_menu'))
    
    categories = Category.query.all()
    return render_template('edit_item.html', item=item, categories=categories)

@app.route('/admin/order/<int:order_id>/update', methods=['POST'])
@login_required
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    order.status = 'Completed'
    db.session.commit()
    flash(f'Order #{order_id} marked as completed.')
    return redirect(url_for('admin_orders'))

@app.route('/admin/reservation/<int:res_id>/delete', methods=['POST'])
@login_required
def delete_reservation(res_id):
    res = Reservation.query.get_or_404(res_id)
    db.session.delete(res)
    db.session.commit()
    flash('Reservation cleared/removed.')
    return redirect(url_for('admin_reservations'))

@app.route('/admin/reservation/<int:res_id>/arrived', methods=['POST'])
@login_required
def reservation_arrived(res_id):
    res = Reservation.query.get_or_404(res_id)
    db.session.delete(res)
    db.session.commit()
    flash(f'Guest {res.name} has arrived and list updated.')
    return redirect(url_for('admin_reservations'))

@app.route('/admin/menu/add', methods=['GET', 'POST'])
@login_required
def add_menu_item():
    if request.method == 'POST':
        try:
            new_item = MenuItem(
                name=request.form.get('name'),
                description=request.form.get('description'),
                price=float(request.form.get('price')),
                image_url=request.form.get('image_url'),
                category_id=int(request.form.get('category_id'))
            )
            db.session.add(new_item)
            db.session.commit()
            flash('New dish added successfully!')
            return redirect(url_for('admin_menu'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding item: {e}')
    
    categories = Category.query.all()
    return render_template('add_item.html', categories=categories)

@app.route('/admin/menu/delete/<int:item_id>', methods=['POST'])
@login_required
def delete_menu_item(item_id):
    item = MenuItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash(f'Dish "{item.name}" removed from menu.')
    return redirect(url_for('admin_menu'))

@app.route('/admin/chats')
@login_required
def admin_chats():
    chats = ChatMessage.query.order_by(ChatMessage.created_at.desc()).all()
    return render_template('admin_chats.html', chats=chats)

# --- NEW: ADMIN SETTINGS ROUTE ---
@app.route('/admin/settings', methods=['GET', 'POST'])
@login_required
def admin_settings():
    if request.method == 'POST':
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if new_password != confirm_password:
            flash('Passwords do not match!', 'danger')
        elif len(new_password) < 6:
            flash('Password must be at least 6 characters.', 'warning')
        else:
            user = User.query.get(current_user.id)
            user.password = new_password
            db.session.commit()
            flash('Admin password updated successfully!', 'success')
            return redirect(url_for('admin'))

    return render_template('admin_settings.html')

if __name__ == '__main__':
    app.run(debug=True)