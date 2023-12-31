from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
import requests

app = Flask(__name__)
app.secret_key = 'my_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

class UserBook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(200), nullable=False)
    page_count = db.Column(db.Integer)
    average_rating = db.Column(db.REAL)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    isbn = db.Column(db.String(20))

with app.app_context():
    db.create_all()

    users_to_create = [
        {'username': 'adam', 'password': 'password123'},
        {'username': 'sarah', 'password': 'sa2024'},
        {'username': 'noah', 'password': 'python01'}
    ]

    for user_data in users_to_create:
        user = User.query.filter_by(username=user_data['username']).first()
        if not user:
            hashed_password = generate_password_hash(user_data['password'])
            new_user = User(username=user_data['username'], password=hashed_password)
            db.session.add(new_user)

    db.session.commit()

    if not hasattr(UserBook, 'isbn'):
        db.engine.execute('ALTER TABLE user_book ADD COLUMN isbn TEXT;')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['logged_in'] = True
            session['username'] = username

            session.pop('_flashes', None)

            flash('Login successful', 'success')
            return redirect(url_for('dashboard'))
        else:
            error = 'Invalid username or password'
            flash(error, 'error')

    return render_template('login.html', error=error)

@app.route('/dashboard')
def dashboard():
    error = None
    if 'logged_in' in session:
        user_books = UserBook.query.filter_by(user_id=session['username']).all()
        return render_template('dashboard.html', books=user_books, error=error)
    else:
        error = 'Please login to view your dashboard'
        flash(error, 'error')
        return redirect(url_for('login'))

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/delete/<int:book_id>', methods=['GET', 'POST'])
def delete_book(book_id):
    if 'logged_in' in session:
        book_to_delete = UserBook.query.get(book_id)
        if book_to_delete:
            db.session.delete(book_to_delete)
            db.session.commit()
            flash('Book deleted successfully', 'success')
        else:
            flash('Book not found', 'error')
    else:
        flash('Please log in to delete books', 'error')

    return redirect(url_for('user_books'))

def fetch_book_details(isbn):
    google_books_api_url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
    response = requests.get(google_books_api_url)

    if response.status_code == 200:
        book_data = response.json()
        if 'items' in book_data and len(book_data['items']) > 0:
            book_info = book_data['items'][0]['volumeInfo']
            return {
                'title': book_info.get('title'),
                'author': book_info.get('authors')[0] if 'authors' in book_info else 'Unknown Author',
                'page_count': book_info.get('pageCount'),
                'average_rating': book_info.get('averageRating') if 'averageRating' in book_info else 0.0,
            }
    return None

@app.route('/user_books', methods=['GET', 'POST'])
def user_books():
    if 'logged_in' in session:
        user_id = session['username']

        if request.method == 'POST':
            isbn = request.form['isbn']
            existing_book = UserBook.query.filter_by(user_id=user_id, isbn=isbn).first()

            if existing_book:
                flash('Book already exists in your collection', 'error')
            else:
                book_data = fetch_book_details(isbn)

                if book_data:
                    new_book = UserBook(
                        title=book_data.get('title'),
                        author=book_data.get('author'),
                        page_count=book_data.get('page_count'),
                        average_rating=book_data.get('average_rating'),
                        user_id=user_id,
                        isbn=isbn
                    )

                    try:
                        db.session.add(new_book)
                        db.session.commit()
                        flash('Book added successfully', 'success')
                    except Exception as e:
                        print("Error adding book:", e)
                        flash('Error adding book', 'error')
                else:
                    flash('Book not found or invalid ISBN', 'error')

            return redirect(url_for('dashboard'))

        else:
            user_books = UserBook.query.filter_by(user_id=user_id).all()
            return render_template('user_books.html', user_name=user_id, books=user_books)
    else:
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)