from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Set a secret key for sessions

# Database connection
conn = sqlite3.connect('database.db')

# HTML templates directory
app.config['TEMPLATES_AUTO_RELOAD'] = True


@app.route('/')
def index():
    if 'logged_in' in session:
        return redirect(url_for('user_books'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print("Received username:", username)
        print("Received password:", password)

        # Validate user credentials (dummy authentication, replace with actual logic)
        if username == 'user' and password == 'password':
            session['logged_in'] = True
            session['username'] = username
            print("Login successful!")
            return redirect(url_for('user_books'))
        else:
            print("Login failed. Invalid credentials!")
            return render_template('login.html', error='Invalid credentials')

    return render_template('login.html')


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

            # Implement API call to Google Books using the provided ISBN
            # Retrieve book details and store them in the database
            # Display appropriate error if API call fails or book details aren't found

            # Dummy book data (replace with actual data fetched from API)
            book_data = {
                'title': 'Book Title',
                'author': 'Author Name',
                'page_count': 300,
                'average_rating': 4.5
            }

            # Store book data in the database for the logged-in user
            insert_query = """
                INSERT INTO user_books (title, author, page_count, average_rating, user_id)
                VALUES (?, ?, ?, ?, ?)
            """
            conn.execute(insert_query, (book_data['title'], book_data['author'], book_data['page_count'],
                                        book_data['average_rating'], session['username']))
            conn.commit()
            return redirect(url_for('user_books'))

        else:
            # Fetch and display user's books from the database
            select_query = """
                SELECT title, author, page_count, average_rating FROM user_books
                WHERE user_id = ?
            """
            books_cursor = conn.execute(select_query, (session['username'],))
            user_books = books_cursor.fetchall()
            return render_template('user_books.html', books=user_books)
    else:
        return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
