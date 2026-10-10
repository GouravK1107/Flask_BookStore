# 📚 Online Book Store

A full-featured e-commerce web application for buying and reading books online. Built with Flask, this platform supports both readers and authors with features like digital reading, physical book purchases, and community engagement.

## ✨ Features

> 🤝 **Project Type: Freelance**
>
> This project was built as part of a freelance engagement for a client. It is shared here with the client's permission to showcase my work, and sensitive details such as credentials, business data, and proprietary information have been removed. If you'd like a similar solution for your business, feel free to get in touch!

### 👥 User System
- **Dual Role System**: Users can register as either a **Reader** or **Author**
- **Authentication**: Secure login/logout with password hashing
- **Profile Management**: View account stats, manage books, track purchases

### 📖 For Readers
- **Browse Books**: Search, filter, and sort through thousands of books
- **Digital Reading**: Read purchased/free books directly in browser with PDF.js viewer
- **Purchase Options**: 
  - Pay & Read (instant digital access)
  - Add to Cart (physical/delivery purchase)
- **Interactive Features**: Like/dislike books, comment, share book links
- **My Library**: Access all purchased books in one place
- **Order Tracking**: View order history and status

### ✍️ For Authors
- **Publish Books**: Upload PDF files with cover images
- **Set Pricing**: Choose free or paid models
- **Edit Books**: Update content, pricing, and metadata
- **Analytics**: Track views and interactions on your books

### 🛒 E-commerce Features
- **Shopping Cart**: Add/remove items, update quantities
- **Checkout**: Multiple payment methods including Cash on Delivery
- **Order Management**: Track orders from confirmation to delivery
- **Payment Integration**: Dummy payment gateway for testing

### 🔧 Technical Features
- **PDF Viewer**: Full-featured PDF reader with zoom, fullscreen, navigation
- **Advanced Filtering**: Filter by category, price range, date, and more
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Beautiful UI**: Modern design with custom backgrounds per page

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/online-book-store.git
cd online-book-store
```

2. **Create virtual environment**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the application**
```bash
python app.py
```

5. **Open your browser**
```
http://127.0.0.1:5000
```

## 📁 Project Structure

```
online-book-store/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .gitignore            # Git ignore file
├── README.md             # Project documentation
├── instance/
│   └── bookstore.db      # SQLite database (auto-created)
├── uploads/              # Uploaded PDF files
│   └── .gitkeep          # Keep folder in git
└── templates/
    ├── base.html         # Base template
    ├── landing.html      # Landing page
    ├── login.html        # Login page
    ├── register.html     # Registration page
    ├── profile.html      # User profile
    ├── books.html        # Browse books
    ├── book_detail.html  # Book details
    ├── read_book.html    # PDF reader
    ├── create_book.html  # Publish book (Author)
    ├── edit_book.html    # Edit book (Author)
    ├── filter.html       # Advanced filters
    ├── my_library.html   # User's purchased books
    ├── cart.html         # Shopping cart
    ├── checkout.html     # Checkout page
    ├── my_orders.html    # Order history
    ├── order_detail.html # Order details
    ├── order_confirmation.html # Order success
    ├── order_payment.html # Payment page
    ├── payment.html      # Instant payment
    └── payment_success.html # Payment success
```

## 🗄️ Database Schema

### User Model
- `id`, `username`, `email`, `password_hash`
- `is_author` (role: Reader/Author)
- `created_at`

### Book Model
- `id`, `title`, `category`, `summary`
- `pdf_filename`, `price`, `cover_image`
- `author_id`, `created_at`, `views`

### E-commerce Models
- **Cart**: User's shopping cart items
- **Order**: Purchase orders with shipping details
- **OrderItem**: Individual items in orders

### Interaction Models
- **Comment**: User comments on books
- **BookLike**: Like/dislike reactions
- **Purchase**: Digital access purchases

## 🎯 Usage Guide

### As a Reader

1. **Register** as a "Reader"
2. **Browse books** from the homepage
3. **Read free books** instantly or **purchase** paid ones
4. **Add books to cart** for physical delivery
5. **Checkout** with address and payment method
6. **Track orders** in "My Orders"
7. **View purchased books** in "My Library"
8. **Interact** with books via likes and comments

### As an Author

1. **Register** as an "Author"
2. **Publish books** via "Publish New Book"
3. **Upload PDF** and set price (0 = free)
4. **Edit books** anytime
5. **Track views** and engagement

### Payment Methods

- **Card**: Credit/Debit card (demo)
- **UPI**: Google Pay, PhonePe, etc.
- **NetBanking**: All major banks
- **COD**: Cash on Delivery (physical orders)

## ⌨️ Keyboard Shortcuts (PDF Reader)

| Shortcut | Action |
|----------|--------|
| `←` | Previous Page |
| `→` | Next Page |
| `+` / `=` | Zoom In |
| `-` / `_` | Zoom Out |
| `0` | Reset Zoom (50%) |
| `F` | Fullscreen Mode |
| `Esc` | Exit Fullscreen |

## 🛠️ Technology Stack

- **Backend**: Flask 2.3.3
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: Flask-Login
- **PDF Rendering**: PDF.js 2.16.105
- **Frontend**: HTML5, CSS3, JavaScript
- **Fonts**: Google Fonts (Inter)

## 📦 Dependencies

```
Flask==2.3.3
Flask-SQLAlchemy==3.0.5
Flask-Login==0.6.2
Werkzeug==2.3.7
```

## 🔐 Environment Variables

Create a `.env` file for production (optional):

```env
SECRET_KEY=your-secret-key-here
FLASK_ENV=production
DATABASE_URL=sqlite:///bookstore.db
```

## 🧪 Testing Accounts

Register your own accounts or use:
- **Reader**: Register as "Reader" to test browsing and purchases
- **Author**: Register as "Author" to test book publishing

## 📱 Responsive Design

The application is fully responsive and works on:
- 💻 Desktop (1920x1080 and above)
- 📱 Tablet (768x1024)
- 📱 Mobile (320x480)

## 🎨 Customization

### Changing Backgrounds
Each page has its own background image. Edit the `{% block extra_css %}` section in any template:

```html
{% block extra_css %}
<style>
    body {
        background-image: url('your-image-url.jpg');
    }
</style>
{% endblock %}
```

### Modifying Colors
The main theme colors are defined in `base.html`:
- Primary accent: `#e67e22` (orange)
- Dark background: `#2c3e50` (navy)
- Text colors: various shades of gray

## 🐛 Troubleshooting

### Common Issues

**"Cart is undefined" error**
- Make sure you've added the Cart model to `app.py`
- Restart the Flask server

**PDF not loading**
- Check if PDF file was uploaded correctly
- Verify the file exists in `uploads/` folder
- Clear browser cache

**Database errors**
- Delete `instance/bookstore.db` and restart
- Run `db.create_all()` in Flask shell

**Port already in use**
```bash
# Change port
python app.py --port=5001
```

## 📈 Future Enhancements

- [ ] Email notifications for orders
- [ ] Wishlist feature
- [ ] Rating system (1-5 stars)
- [ ] Social login (Google, Facebook)
- [ ] Advanced search with recommendations
- [ ] Bulk discount for multiple books
- [ ] Author dashboard with sales analytics
- [ ] Coupon/discount code system
- [ ] Book categories management
- [ ] API for mobile app

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Unsplash for beautiful background images
- PDF.js for PDF rendering capabilities
- Font Awesome for icons (via emoji)

## 📧 Contact
- Reachout :- https://gouravk1107.github.io/my-portfolio/

---

## 🎉 Happy Reading!

Made with ❤️ using Flask
