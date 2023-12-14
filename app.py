from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'my_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

with app.app_context():
    user = User.query.filter_by(username='adam').first()
    if not user:
        hashed_password = generate_password_hash('password123')
        new_user = User(username='adam', password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

class UserBook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(200), nullable=False)
    page_count = db.Column(db.Integer)
    average_rating = db.Column(db.REAL)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


    def __repr__(self):
        return f'<UserBook {self.title}>'

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            if username != 'adam':
                error = "You can only log in as 'adam'"
                flash(error, 'error')
                return render_template('login.html', error=error)

            session['logged_in'] = True
            session['username'] = username
            flash('Login successful', 'success')
            return redirect(url_for('dashboard'))
        else:
            error = 'Invalid username or password'
            flash(error, 'error')

    return render_template('login.html', error=error)


@app.route('/dashboard')
def dashboard():
    if 'logged_in' in session:
        print("Rendering dashboard")
        return render_template('dashboard.html')
    else:
        print("Redirecting to login")
        return redirect(url_for('login'))

@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/user_books', methods=['GET', 'POST'])
def user_books():
    if 'logged_in' in session:
        if request.method == 'POST':
            isbn = request.form['isbn']

            # Logic to fetch book details from an API (placeholder)
            book_data = {
                'title': 'Book Title',
                'author': 'Author Name',
                'page_count': 300,
                'average_rating': 4.5
            }

            # Create a new book object and add it to the database
            new_book = UserBook(
                title=book_data['title'],
                author=book_data['author'],
                page_count=book_data['page_count'],
                average_rating=book_data['average_rating'],
                user_id=session['username']  # Assuming user_id here is the username
            )
            try:
                db.session.add(new_book)
                db.session.commit()
                print("Book added to the database")
            except Exception as e:
                print("Error adding book:", e)

            return redirect(url_for('user_books'))

        else:
            user_books = UserBook.query.filter_by(user_id=session['username']).all()
            print("Books retrieved from the database:", user_books)
            return render_template('user_books.html', books=user_books)
    else:
        return redirect(url_for('login'))




with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)