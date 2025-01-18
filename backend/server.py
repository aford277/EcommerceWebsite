from flask import Flask, jsonify, request, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import random

app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')
app.config['SQLALCHEMY_DATABASE_URI'] = r'sqlite:///..\db\congo.db'
app.config['SECRET_KEY'] = 'ranbiuge93nfdskll930NIF89biodB893R'
db = SQLAlchemy(app)

# Add the context processor here
@app.context_processor
def inject_user():
    user_id = session.get('user_id')  # Get user_id from the session
    return {'user_id': user_id}  # Make user_id available to all templates

class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(200))
    price = db.Column(db.Float, nullable=False)
    rating = db.Column(db.Float, nullable=True)
    picture_url = db.Column(db.String(200), nullable=False)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False) 
    password = db.Column(db.String(120), nullable=False) 
    street = db.Column(db.String(200), nullable=True) 
    city = db.Column(db.String(100), nullable=True) 
    state = db.Column(db.String(100), nullable=True)  
    postal_code = db.Column(db.String(20), nullable=True)
    country = db.Column(db.String(100), nullable=True)

class Orders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())

class OrderProducts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

# Homepage is just the search bar with a list of products on the site
@app.route('/', methods=['GET'])
def home():
    search_query = request.args.get('search', '')
    products = get_products(search_query)
    user_id = session.get('user_id')
    return render_template('home.html', products=products, user_id=user_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        error_message = None

        # Check if user exists and password matches
        user = Users.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):  # Check hashed password
            session['user_id'] = user.id
            session['email'] = user.email
            next_page = request.args.get('next')
            return redirect(next_page or url_for('home'))
        else:
            error_message = "Invalid email or password"
            return render_template('login.html', error_message=error_message)

    return render_template('login.html', next=request.args.get('next'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        error_message = None

        # Check if email already exists
        if Users.query.filter_by(email=email).first():
            error_message = "Email already exists"

        # Check if passwords match
        elif password != confirm_password:
            error_message = "Passwords do not match"
        
        elif len(password) < 8:
            error_message = "Password must be at least 8 characters long."

        if error_message:
            return render_template('signup.html', error_message=error_message, email=email, password=password, confirm_password=confirm_password);
        
        # Add user to the database
        hashed_password = generate_password_hash(password)
        new_user = Users(email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/product/<int:product_id>', methods=['GET'])
def product_page(product_id):
    product = Products.query.get_or_404(product_id)
    return render_template('product.html', product=product)

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    quantity = int(request.form.get('quantity', 1))
    product = Products.query.get_or_404(product_id)

    if 'cart' not in session:
        session['cart'] = []

    cart = session['cart']
    
    # Check if the product is already in the cart
    for item in cart:
        if isinstance(item, dict) and item.get('id') == product.id:
            item['quantity'] += quantity
            session['cart'] = cart  # Update session
            return redirect(url_for('product_page', product_id=product_id))

    # Add new item to the cart
    cart.append({
        'id': product.id,
        'name': product.name,
        'price': product.price,
        'quantity': quantity
    })

    session.modified = True
    return redirect(url_for('product_page', product_id=product_id))

@app.route('/cart', methods=['GET'])
def cart():
    if 'cart' not in session or not session['cart']:
        return render_template('cart.html', total=0)
    
    cart = session.get('cart', [])

    # Generate totals to display to user
    raw_total = sum(item['price'] * item['quantity'] for item in cart)
    tax = f"{raw_total * 0.13:.2f}"
    total = f"{raw_total * 1.13:.2f}"
    
    return render_template('cart.html', cart=cart, tax=tax, total=total)

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'user_id' not in session:
        return redirect(url_for('login', next='/checkout'))

    user_id = session['user_id']
    user = Users.query.get(user_id)  # Fetch the user from the database

    if not user:
        return redirect(url_for('home'))  # Redirect if user is not found

    # Prepopulate saved address
    address_data = {
        'street': user.street or '',
        'city': user.city or '',
        'state': user.state or '',
        'postal_code': user.postal_code or '',
        'country': user.country or '',
    }

    if request.method == 'POST':
        # If user wishes to save address
        if request.form.get('save_address') == 'on':
            # Get submitted address data
            user.street = request.form['street']
            user.city = request.form['city']
            user.state = request.form['state']
            user.postal_code = request.form['postal_code']
            user.country = request.form['country']
            db.session.commit()
        
        # These variables are created to go under the address column in the Orders table
        street = request.form['street']
        city = request.form['city']
        state = request.form['state']
        postal_code = request.form['postal_code']
        country = request.form['country']

        cart = session.get('cart', [])

        total_price = sum(item['price'] * item['quantity'] for item in cart)

        # Create a new order
        new_order = Orders(
            user_id=user_id,
            address=f"{street}, {city}, {state}, {postal_code}, {country}",
            total_price=total_price
        )
        db.session.add(new_order)
        db.session.commit()

        # Add products to the order
        for item in cart:
            order_product = OrderProducts(
                order_id=new_order.id,
                product_id=item['id'],
                quantity=item['quantity']
            )
            db.session.add(order_product)
        db.session.commit()

        # Clear the cart
        session.pop('cart', None)

        # Generate random delivery date (System does not calculate how long it would take to ship a product)
        delivery_days = random.randint(2, 10)
        expected_delivery_date = datetime.now() + timedelta(days=delivery_days)

        return render_template(
            'order_confirmation.html',
            order_id=new_order.id,
            delivery_date=expected_delivery_date.strftime("%A, %B %d, %Y")
        )

    return render_template('checkout.html', address=address_data)

# Gets a list of all products that contain the string in the search query
def get_products(search_query=None):
    if search_query:
        products_query = Products.query.filter(Products.name.contains(search_query)).all()
    else:
        products_query = Products.query.all()
    
    products = products = [
        {'id': p.id, 'name': p.name, 'description': p.description, 'price': p.price, 'rating': p.rating, 'image': p.picture_url}
        for p in products_query
    ]
    return products

if __name__ == '__main__':
    with app.app_context(): 
        db.create_all()
    app.run(debug=True)