from flask import Flask, render_template, request, redirect, url_for, flash, abort, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from sqlalchemy import func, desc
import json
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookstore.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# File upload configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}

# Create upload folder if not exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# ------------------ MODELS ------------------

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_author = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    books = db.relationship('Book', backref='author', lazy=True)
    comments = db.relationship('Comment', backref='user', lazy=True)
    likes = db.relationship('BookLike', backref='user', lazy=True)
    purchases = db.relationship('Purchase', backref='user', lazy=True)
    cart_items = db.relationship('Cart', backref='user', lazy=True)
    orders = db.relationship('Order', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    summary = db.Column(db.Text, nullable=False)
    pdf_filename = db.Column(db.String(300), nullable=False)
    price = db.Column(db.Float, default=0.0)
    cover_image = db.Column(db.String(300), default='https://covers.openlibrary.org/b/id/10523338-L.jpg')
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    views = db.Column(db.Integer, default=0)
    
    comments = db.relationship('Comment', backref='book', lazy=True, cascade='all, delete-orphan')
    likes = db.relationship('BookLike', backref='book', lazy=True, cascade='all, delete-orphan')
    purchases = db.relationship('Purchase', backref='book', lazy=True)
    cart_items = db.relationship('Cart', backref='book', lazy=True)
    order_items = db.relationship('OrderItem', backref='book', lazy=True)
    
    @property
    def is_paid(self):
        return self.price > 0
    
    @property
    def like_count(self):
        return BookLike.query.filter_by(book_id=self.id, is_like=True).count()
    
    @property
    def dislike_count(self):
        return BookLike.query.filter_by(book_id=self.id, is_like=False).count()
    
    @property
    def total_interactions(self):
        return self.like_count + self.dislike_count + self.views
    
    def user_reaction(self, user_id):
        if user_id:
            reaction = BookLike.query.filter_by(book_id=self.id, user_id=user_id).first()
            if reaction:
                return 'like' if reaction.is_like else 'dislike'
        return None

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class BookLike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    is_like = db.Column(db.Boolean, nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    __table_args__ = (db.UniqueConstraint('book_id', 'user_id', name='unique_book_user'),)

class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    purchased_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'book_id', name='unique_user_book_purchase'),)

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'book_id', name='unique_user_book_cart'),)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='pending')
    payment_method = db.Column(db.String(50), nullable=False)
    payment_status = db.Column(db.String(50), default='pending')
    shipping_address = db.Column(db.Text, nullable=False)
    shipping_city = db.Column(db.String(100), nullable=False)
    shipping_state = db.Column(db.String(100), nullable=False)
    shipping_pincode = db.Column(db.String(10), nullable=False)
    shipping_phone = db.Column(db.String(15), nullable=False)
    ordered_at = db.Column(db.DateTime, default=datetime.utcnow)
    delivered_at = db.Column(db.DateTime, nullable=True)
    
    items = db.relationship('OrderItem', backref='order', cascade='all, delete-orphan')

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    price = db.Column(db.Float, nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# ------------------ HELPER FUNCTIONS ------------------

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def can_read_book(user, book):
    """Check if user can read the book (free/purchased/author)"""
    if not user.is_authenticated:
        return False
    if user.is_author:
        return True
    if not book.is_paid:
        return True
    purchase = Purchase.query.filter_by(user_id=user.id, book_id=book.id).first()
    return purchase is not None

def mark_purchased(user_id, book_id):
    """Mark a book as purchased by user"""
    existing = Purchase.query.filter_by(user_id=user_id, book_id=book_id).first()
    if not existing:
        purchase = Purchase(user_id=user_id, book_id=book_id)
        db.session.add(purchase)
        db.session.commit()

# ------------------ ROUTES ------------------

@app.route('/')
def index():
    """Landing page - no books displayed"""
    total_books = Book.query.count()
    total_authors = User.query.filter_by(is_author=True).count()
    total_users = User.query.filter_by(is_author=False).count()
    return render_template('landing.html', 
                         total_books=total_books, 
                         total_authors=total_authors,
                         total_users=total_users)

@app.route('/books')
@login_required
def books():
    """Main books page after login"""
    sort_by = request.args.get('sort', 'recent')
    category = request.args.get('category', '')
    search = request.args.get('search', '')
    price_filter = request.args.get('price', '')
    
    query = Book.query
    
    if search:
        query = query.filter(Book.title.contains(search) | Book.summary.contains(search))
    
    if category:
        query = query.filter_by(category=category)
    
    if price_filter == 'free':
        query = query.filter_by(price=0)
    elif price_filter == 'paid':
        query = query.filter(Book.price > 0)
    
    if sort_by == 'recent':
        query = query.order_by(Book.created_at.desc())
    elif sort_by == 'oldest':
        query = query.order_by(Book.created_at.asc())
    elif sort_by == 'price_low':
        query = query.order_by(Book.price.asc())
    elif sort_by == 'price_high':
        query = query.order_by(Book.price.desc())
    elif sort_by == 'popular':
        query = query.order_by(Book.views.desc())
    else:
        query = query.order_by(Book.created_at.desc())
    
    books = query.all()
    
    if sort_by == 'trending':
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        books = [b for b in books if b.created_at >= thirty_days_ago]
        books.sort(key=lambda b: (b.views + b.like_count), reverse=True)
    elif sort_by == 'most_liked':
        books.sort(key=lambda b: b.like_count, reverse=True)
    
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    trending_books = [b for b in books if b.created_at >= thirty_days_ago]
    trending_books.sort(key=lambda b: (b.views + b.like_count), reverse=True)
    
    popular_books = sorted(books, key=lambda b: b.views, reverse=True)
    recent_books = sorted(books, key=lambda b: b.created_at, reverse=True)
    
    categories = db.session.query(Book.category).distinct().all()
    categories = [c[0] for c in categories]
    
    return render_template('books.html', 
                         books=books[:12],
                         trending_books=trending_books[:4],
                         popular_books=popular_books[:4],
                         recent_books=recent_books[:4],
                         categories=categories, 
                         sort_by=sort_by, 
                         selected_category=category, 
                         search=search, 
                         price_filter=price_filter)

@app.route('/filter')
@login_required
def filter_page():
    """Filter page with advanced filtering options"""
    sort_by = request.args.get('sort', 'recent')
    category = request.args.get('category', '')
    search = request.args.get('search', '')
    price_filter = request.args.get('price', '')
    min_price = request.args.get('min_price', '')
    max_price = request.args.get('max_price', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    
    query = Book.query
    
    if search:
        query = query.filter(Book.title.contains(search) | Book.summary.contains(search))
    
    if category:
        query = query.filter_by(category=category)
    
    if price_filter == 'free':
        query = query.filter_by(price=0)
    elif price_filter == 'paid':
        query = query.filter(Book.price > 0)
    
    if min_price:
        query = query.filter(Book.price >= float(min_price))
    if max_price:
        query = query.filter(Book.price <= float(max_price))
    
    if date_from:
        date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
        query = query.filter(Book.created_at >= date_from_obj)
    if date_to:
        date_to_obj = datetime.strptime(date_to, '%Y-%m-%d') + timedelta(days=1)
        query = query.filter(Book.created_at <= date_to_obj)
    
    if sort_by == 'recent':
        query = query.order_by(Book.created_at.desc())
    elif sort_by == 'oldest':
        query = query.order_by(Book.created_at.asc())
    elif sort_by == 'price_low':
        query = query.order_by(Book.price.asc())
    elif sort_by == 'price_high':
        query = query.order_by(Book.price.desc())
    elif sort_by == 'popular':
        query = query.order_by(Book.views.desc())
    else:
        query = query.order_by(Book.created_at.desc())
    
    books = query.all()
    
    if sort_by == 'trending':
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        books = [b for b in books if b.created_at >= thirty_days_ago]
        books.sort(key=lambda b: (b.views + b.like_count), reverse=True)
    elif sort_by == 'most_liked':
        books.sort(key=lambda b: b.like_count, reverse=True)
    
    categories = db.session.query(Book.category).distinct().all()
    categories = [c[0] for c in categories]
    
    return render_template('filter.html', books=books, categories=categories, 
                         sort_by=sort_by, selected_category=category, 
                         search=search, price_filter=price_filter,
                         min_price=min_price, max_price=max_price,
                         date_from=date_from, date_to=date_to)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        is_author = request.form.get('role') == 'author'
        
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('register'))
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'danger')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered!', 'danger')
            return redirect(url_for('register'))
        
        user = User(username=username, email=email, is_author=is_author)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(url_for('books'))
        else:
            flash('Invalid email or password!', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    if current_user.is_author:
        user_books = Book.query.filter_by(author_id=current_user.id).all()
    else:
        user_books = []
    return render_template('profile.html', user_books=user_books)

@app.route('/book/<int:book_id>')
def book_detail(book_id):
    book = Book.query.get_or_404(book_id)
    book.views += 1
    db.session.commit()
    
    comments = Comment.query.filter_by(book_id=book_id).order_by(Comment.created_at.desc()).all()
    user_reaction = None
    if current_user.is_authenticated:
        user_reaction = book.user_reaction(current_user.id)
    share_link = request.url_root + url_for('book_detail', book_id=book_id)[1:]
    return render_template('book_detail.html', book=book, comments=comments, user_reaction=user_reaction, share_link=share_link)

@app.route('/book/create', methods=['GET', 'POST'])
@login_required
def create_book():
    if not current_user.is_author:
        flash('Only authors can create books!', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        category = request.form.get('category')
        summary = request.form.get('summary')
        price = float(request.form.get('price') or 0)
        cover_image = request.form.get('cover_image') or 'https://covers.openlibrary.org/b/id/10523338-L.jpg'
        
        if 'pdf_file' not in request.files:
            flash('Please upload a PDF file!', 'danger')
            return redirect(url_for('create_book'))
        
        pdf_file = request.files['pdf_file']
        if pdf_file.filename == '':
            flash('Please select a PDF file!', 'danger')
            return redirect(url_for('create_book'))
        
        if not allowed_file(pdf_file.filename):
            flash('Only PDF files are allowed!', 'danger')
            return redirect(url_for('create_book'))
        
        if not title or not category or not summary:
            flash('Please fill all required fields!', 'danger')
            return redirect(url_for('create_book'))
        
        filename = secure_filename(f"{datetime.utcnow().timestamp()}_{pdf_file.filename}")
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        pdf_file.save(pdf_path)
        
        book = Book(
            title=title,
            category=category,
            summary=summary,
            pdf_filename=filename,
            price=price,
            cover_image=cover_image,
            author_id=current_user.id
        )
        db.session.add(book)
        db.session.commit()
        flash('Book published successfully!', 'success')
        return redirect(url_for('book_detail', book_id=book.id))
    
    return render_template('create_book.html')

@app.route('/book/<int:book_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_book(book_id):
    book = Book.query.get_or_404(book_id)
    if book.author_id != current_user.id:
        flash('You can only edit your own books!', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        book.title = request.form.get('title')
        book.category = request.form.get('category')
        book.summary = request.form.get('summary')
        book.price = float(request.form.get('price') or 0)
        book.cover_image = request.form.get('cover_image') or book.cover_image
        
        if 'pdf_file' in request.files and request.files['pdf_file'].filename != '':
            pdf_file = request.files['pdf_file']
            if allowed_file(pdf_file.filename):
                old_pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], book.pdf_filename)
                if os.path.exists(old_pdf_path):
                    os.remove(old_pdf_path)
                
                filename = secure_filename(f"{datetime.utcnow().timestamp()}_{pdf_file.filename}")
                pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                pdf_file.save(pdf_path)
                book.pdf_filename = filename
            else:
                flash('Only PDF files are allowed!', 'danger')
                return redirect(url_for('edit_book', book_id=book.id))
        
        db.session.commit()
        flash('Book updated successfully!', 'success')
        return redirect(url_for('book_detail', book_id=book.id))
    
    return render_template('edit_book.html', book=book)

@app.route('/read/<int:book_id>')
@login_required
def read_book(book_id):
    book = Book.query.get_or_404(book_id)
    if not can_read_book(current_user, book):
        flash('You need to purchase this book to read it!', 'warning')
        return redirect(url_for('payment', book_id=book.id))
    return render_template('read_book.html', book=book)

@app.route('/uploads/<filename>')
@login_required
def serve_pdf(filename):
    book = Book.query.filter_by(pdf_filename=filename).first()
    if not book:
        abort(404)
    
    if not can_read_book(current_user, book):
        abort(403)
    
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/payment/<int:book_id>')
@login_required
def payment(book_id):
    book = Book.query.get_or_404(book_id)
    if can_read_book(current_user, book):
        flash('You already have access to this book!', 'info')
        return redirect(url_for('read_book', book_id=book.id))
    if not book.is_paid:
        return redirect(url_for('read_book', book_id=book.id))
    return render_template('payment.html', book=book)

@app.route('/payment/process', methods=['POST'])
@login_required
def process_payment():
    book_id = request.form.get('book_id')
    payment_method = request.form.get('payment_method')
    book = Book.query.get_or_404(book_id)
    
    mark_purchased(current_user.id, book.id)
    flash('Payment successful! You can now read the book.', 'success')
    return redirect(url_for('payment_success', book_id=book.id))

@app.route('/payment/success/<int:book_id>')
@login_required
def payment_success(book_id):
    book = Book.query.get_or_404(book_id)
    if not can_read_book(current_user, book):
        return redirect(url_for('payment', book_id=book.id))
    return render_template('payment_success.html', book=book)

@app.route('/like/<int:book_id>', methods=['POST'])
@login_required
def like_book(book_id):
    book = Book.query.get_or_404(book_id)
    reaction = request.form.get('reaction')
    is_like = (reaction == 'like')
    
    existing = BookLike.query.filter_by(book_id=book_id, user_id=current_user.id).first()
    if existing:
        if existing.is_like == is_like:
            db.session.delete(existing)
        else:
            existing.is_like = is_like
    else:
        new_reaction = BookLike(book_id=book_id, user_id=current_user.id, is_like=is_like)
        db.session.add(new_reaction)
    
    db.session.commit()
    return redirect(url_for('book_detail', book_id=book.id))

@app.route('/comment/<int:book_id>', methods=['POST'])
@login_required
def add_comment(book_id):
    book = Book.query.get_or_404(book_id)
    comment_text = request.form.get('comment')
    if comment_text and comment_text.strip():
        comment = Comment(text=comment_text.strip(), book_id=book_id, user_id=current_user.id)
        db.session.add(comment)
        db.session.commit()
        flash('Comment added!', 'success')
    else:
        flash('Comment cannot be empty!', 'danger')
    return redirect(url_for('book_detail', book_id=book_id))

# ------------------ CART ROUTES ------------------

@app.route('/cart')
@login_required
def view_cart():
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    total = sum(item.book.price * item.quantity for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/cart/add/<int:book_id>', methods=['POST'])
@login_required
def add_to_cart(book_id):
    book = Book.query.get_or_404(book_id)
    quantity = int(request.form.get('quantity', 1))
    
    cart_item = Cart.query.filter_by(user_id=current_user.id, book_id=book_id).first()
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = Cart(user_id=current_user.id, book_id=book_id, quantity=quantity)
        db.session.add(cart_item)
    
    db.session.commit()
    flash(f'"{book.title}" added to cart!', 'success')
    return redirect(request.referrer or url_for('books'))

@app.route('/cart/update/<int:cart_id>', methods=['POST'])
@login_required
def update_cart(cart_id):
    cart_item = Cart.query.get_or_404(cart_id)
    if cart_item.user_id != current_user.id:
        abort(403)
    
    quantity = int(request.form.get('quantity', 1))
    if quantity <= 0:
        db.session.delete(cart_item)
    else:
        cart_item.quantity = quantity
    
    db.session.commit()
    return redirect(url_for('view_cart'))

@app.route('/cart/remove/<int:cart_id>')
@login_required
def remove_from_cart(cart_id):
    cart_item = Cart.query.get_or_404(cart_id)
    if cart_item.user_id != current_user.id:
        abort(403)
    
    db.session.delete(cart_item)
    db.session.commit()
    flash('Item removed from cart.', 'info')
    return redirect(url_for('view_cart'))

# ------------------ ORDER ROUTES ------------------

@app.route('/checkout')
@login_required
def checkout():
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        flash('Your cart is empty!', 'warning')
        return redirect(url_for('books'))
    
    total = sum(item.book.price * item.quantity for item in cart_items)
    return render_template('checkout.html', cart_items=cart_items, total=total)

@app.route('/order/place', methods=['POST'])
@login_required
def place_order():
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        flash('Your cart is empty!', 'warning')
        return redirect(url_for('books'))
    
    full_name = request.form.get('full_name')
    address = request.form.get('address')
    city = request.form.get('city')
    state = request.form.get('state')
    pincode = request.form.get('pincode')
    phone = request.form.get('phone')
    payment_method = request.form.get('payment_method')
    
    if not all([full_name, address, city, state, pincode, phone]):
        flash('Please fill all shipping details!', 'danger')
        return redirect(url_for('checkout'))
    
    total = sum(item.book.price * item.quantity for item in cart_items)
    order_number = f"ORD-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{current_user.id}"
    shipping_address = f"{full_name}\n{address}\n{city}, {state} - {pincode}\nPhone: {phone}"
    
    order = Order(
        order_number=order_number,
        user_id=current_user.id,
        total_amount=total,
        payment_method=payment_method,
        shipping_address=shipping_address,
        shipping_city=city,
        shipping_state=state,
        shipping_pincode=pincode,
        shipping_phone=phone
    )
    
    if payment_method == 'cod':
        order.payment_status = 'pending'
        order.status = 'confirmed'
    else:
        order.payment_status = 'completed'
        order.status = 'confirmed'
    
    db.session.add(order)
    db.session.flush()
    
    for cart_item in cart_items:
        order_item = OrderItem(
            order_id=order.id,
            book_id=cart_item.book_id,
            quantity=cart_item.quantity,
            price=cart_item.book.price
        )
        db.session.add(order_item)
    
    for cart_item in cart_items:
        db.session.delete(cart_item)
    
    db.session.commit()
    
    flash(f'Order placed successfully! Order ID: {order_number}', 'success')
    
    if payment_method != 'cod':
        return redirect(url_for('order_payment', order_id=order.id))
    
    return redirect(url_for('order_confirmation', order_id=order.id))

@app.route('/order/payment/<int:order_id>')
@login_required
def order_payment(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        abort(403)
    return render_template('order_payment.html', order=order)

@app.route('/order/process-payment/<int:order_id>', methods=['POST'])
@login_required
def process_order_payment(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        abort(403)
    
    payment_method = request.form.get('payment_method')
    order.payment_method = payment_method
    order.payment_status = 'completed'
    order.status = 'confirmed'
    db.session.commit()
    
    flash('Payment successful! Your order has been confirmed.', 'success')
    return redirect(url_for('order_confirmation', order_id=order.id))

@app.route('/order/confirmation/<int:order_id>')
@login_required
def order_confirmation(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        abort(403)
    return render_template('order_confirmation.html', order=order)

@app.route('/my-orders')
@login_required
def my_orders():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.ordered_at.desc()).all()
    return render_template('my_orders.html', orders=orders)

@app.route('/order/<int:order_id>')
@login_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        abort(403)
    return render_template('order_detail.html', order=order)

@app.route('/my-library')
@login_required
def my_library():
    if current_user.is_author:
        books = Book.query.filter_by(author_id=current_user.id).all()
        page_title = "My Published Books"
        empty_message = "You haven't published any books yet."
        empty_action = "Publish your first book"
        empty_link = url_for('create_book')
    else:
        books = [purchase.book for purchase in current_user.purchases]
        page_title = "My Library"
        empty_message = "Your library is empty."
        empty_action = "Browse books"
        empty_link = url_for('books')
    
    return render_template('my_library.html', books=books, page_title=page_title, 
                         empty_message=empty_message, empty_action=empty_action, 
                         empty_link=empty_link)

# ------------------ TEMPLATE CONTEXT PROCESSOR ------------------
@app.context_processor
def utility_processor():
    cart_count = 0
    if current_user.is_authenticated:
        cart_count = Cart.query.filter_by(user_id=current_user.id).count()
    return dict(can_read_book=can_read_book, cart_count=cart_count)

# ------------------ RUN APP ------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)