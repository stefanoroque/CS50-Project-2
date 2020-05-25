CREATE TABLE users (
    id serial PRIMARY KEY,
    username VARCHAR NOT NULL UNIQUE,
    pword VARCHAR NOT NULL
);

CREATE TABLE books (
    isbn VARCHAR PRIMARY KEY,
    title VARCHAR NOT NULL,
    author VARCHAR NOT NULL,
    pub_yr INTEGER,
    review_count INTEGER,
    avg_score INTEGER
);

CREATE TABLE reviews (
    user_id INTEGER REFERENCES users,
    book_isbn VARCHAR REFERENCES books,
    text_opinion VARCHAR NOT NULL,
    rating INTEGER NOT NULL check(rating >= 0 and rating <= 5)
);