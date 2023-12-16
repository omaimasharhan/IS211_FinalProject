CREATE TABLE user_books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    page_count INTEGER,
    average_rating REAL,
    isbn TEXT,  -- Add ISBN field
    FOREIGN KEY (user_id) REFERENCES users(id)
);



CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL
);
