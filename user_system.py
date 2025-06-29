from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps

from security_middleware import register_security

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usersystem.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

register_security(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='user')  # 'admin' or 'user'
    cart_items = db.relationship('CartItem', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(500), nullable=True)

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    product = db.relationship('Product')

# Decorators
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(id=data['user_id']).first()
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if current_user.role != 'admin':
            return jsonify({'message': 'Admin access required!'}), 403
        return f(current_user, *args, **kwargs)
    return decorated

# Routes
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({'message': 'Email and password required'}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'User already exists'}), 400
    user = User(email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'})

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({'message': 'Invalid credentials'}), 401
    token = jwt.encode({'user_id': user.id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)},
                       app.config['SECRET_KEY'], algorithm="HS256")
    return jsonify({'token': token, 'role': user.role})

# Admin product management
@app.route('/products', methods=['POST'])
@token_required
@admin_required
def add_product(current_user):
    data = request.json
    name = data.get('name')
    price = data.get('price')
    description = data.get('description', '')
    if not name or price is None:
        return jsonify({'message': 'Name and price are required'}), 400
    product = Product(name=name, price=price, description=description)
    db.session.add(product)
    db.session.commit()
    return jsonify({'message': 'Product added', 'product_id': product.id})

@app.route('/products/<int:product_id>', methods=['PUT'])
@token_required
@admin_required
def update_product(current_user, product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'message': 'Product not found'}), 404
    data = request.json
    product.name = data.get('name', product.name)
    product.price = data.get('price', product.price)
    product.description = data.get('description', product.description)
    db.session.commit()
    return jsonify({'message': 'Product updated'})

@app.route('/products/<int:product_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_product(current_user, product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'message': 'Product not found'}), 404
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted'})

@app.route('/products', methods=['GET'])
def list_products():
    products = Product.query.all()
    output = []
    for p in products:
        output.append({'id': p.id, 'name': p.name, 'price': p.price, 'description': p.description})
    return jsonify(output)

# User cart management
@app.route('/cart', methods=['GET'])
@token_required
def get_cart(current_user):
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    output = []
    for item in cart_items:
        output.append({
            'product_id': item.product_id,
            'name': item.product.name,
            'price': item.product.price,
            'quantity': item.quantity
        })
    return jsonify(output)

@app.route('/cart', methods=['POST'])
@token_required
def add_to_cart(current_user):
    data = request.json
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'message': 'Product not found'}), 404
    cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(user_id=current_user.id, product_id=product_id, quantity=quantity)
        db.session.add(cart_item)
    db.session.commit()
    return jsonify({'message': 'Product added to cart'})

@app.route('/cart/<int:product_id>', methods=['DELETE'])
@token_required
def remove_from_cart(current_user, product_id):
    cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if not cart_item:
        return jsonify({'message': 'Product not in cart'}), 404
    db.session.delete(cart_item)
    db.session.commit()
    return jsonify({'message': 'Product removed from cart'})

import os

# New Models for Orders
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    status = db.Column(db.String(50), default='pending')  # pending, completed, cancelled
    total_amount = db.Column(db.Float, nullable=False)
    order_items = db.relationship('OrderItem', backref='order', lazy=True)

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    price = db.Column(db.Float, nullable=False)
    product = db.relationship('Product')

# API to create order from cart
@app.route('/orders', methods=['POST'])
@token_required
def create_order(current_user):
    import smtplib
    from email.mime.text import MIMEText

    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        return jsonify({'message': 'Cart is empty'}), 400

    total_amount = 0
    for item in cart_items:
        total_amount += item.product.price * item.quantity

    order = Order(user_id=current_user.id, total_amount=total_amount)
    db.session.add(order)
    db.session.flush()  # to get order.id

    for item in cart_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=item.product.price
        )
        db.session.add(order_item)

    # Clear cart after order creation
    for item in cart_items:
        db.session.delete(item)

    db.session.commit()

    # Send order confirmation email (simple SMTP example)
    try:
        sender = 'no-reply@farmaciaselsol.com'
        receiver = current_user.email
        subject = f'Confirmación de Pedido #{order.id}'
        body = f'Hola {current_user.email},\n\nGracias por tu compra. Tu pedido #{order.id} ha sido recibido y está siendo procesado.\n\nTotal: ${total_amount:.2f}\n\nSaludos,\nFarmacias El Sol'

        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = receiver

        # Configure your SMTP server here
        smtp_server = 'localhost'
        smtp_port = 25

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.sendmail(sender, [receiver], msg.as_string())
    except Exception as e:
        print(f'Error sending email: {e}')

    return jsonify({'message': 'Order created', 'order_id': order.id})

# API to get user's orders
@app.route('/orders', methods=['GET'])
@token_required
def get_orders(current_user):
    orders = Order.query.filter_by(user_id=current_user.id).all()
    output = []
    for order in orders:
        items = []
        for item in order.order_items:
            items.append({
                'product_id': item.product_id,
                'name': item.product.name,
                'quantity': item.quantity,
                'price': item.price
            })
        output.append({
            'order_id': order.id,
            'created_at': order.created_at.isoformat(),
            'status': order.status,
            'total_amount': order.total_amount,
            'items': items
        })
    return jsonify(output)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Create default admin user if not exists
        admin_email = os.getenv('ADMIN_EMAIL') or "fernandotroncoso.ortiz@gmail.com"
        admin_password = os.getenv('ADMIN_PASSWORD') or "192168death!"
        if admin_email and admin_password:
            admin_user = User.query.filter_by(email=admin_email).first()
            if not admin_user:
                admin_user = User(email=admin_email, role='admin')
                admin_user.set_password(admin_password)
                db.session.add(admin_user)
                db.session.commit()
                print(f"Default admin user created: {admin_email}")
            else:
                print(f"Admin user {admin_email} already exists.")
        else:
            print("Admin credentials not set in environment variables.")
    app.run(debug=True)
