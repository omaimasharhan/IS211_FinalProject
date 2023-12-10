from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db = SQLAlchemy(app)

# Define your models (e.g., User, UserBook)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

class UserBook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    author = db.Column(db.String(200))
    page_count = db.Column(db.Integer)
    average_rating = db.Column(db.Float)
    user_id = db.Column(db.String(100))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and password == user.password:
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('user_books'))
        else:
            return render_template('login.html', error='Invalid credentials')

    return render_template('login.html')

@app.route('/')
def index():
    if 'logged_in' in session:
        return redirect(url_for('user_books'))
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
            db.session.add(new_book)
            db.session.commit()

            return redirect(url_for('user_books'))

        else:
            user_books = UserBook.query.filter_by(user_id=session['username']).all()
            return render_template('user_books.html', books=user_books)
    else:
        return redirect(url_for('login'))


with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
