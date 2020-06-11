import os
import requests
from flask import Flask, session, render_template, request, abort, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/loginAttempt", methods=["POST"])
def loginAttempt():
    """Attempt to login to the site."""

    username = request.form.get("username")
    pword = request.form.get("pword")

    user_info = db.execute("SELECT * FROM users WHERE username = :username AND pword = :pword", {"username": username, "pword": pword})

    if user_info.rowcount == 0:  
        return render_template("loginError.html", message="Incorrect username or password.")

    # Set session variable for the user's id
    session["user_id"] = user_info.fetchone().id

    # Bring logged in user to search page
    return render_template("search.html")

@app.route("/search", methods=["POST", "GET"])
def search():
    """User Searches for a book in the DB."""

    category = request.form.get("category")
    keyword = request.form.get("keyword")

    # User left the keyword textbox blank
    if keyword == "":
        return render_template("search.html", no_keyword=True)

    # Search by ISBN
    if category == "isbn":
        keyword = keyword.upper()
        books = db.execute("SELECT * FROM books WHERE isbn LIKE :isbn",
                            {"isbn": '%' + keyword + '%'}).fetchall()

    # Search by book title
    elif category == "title":
        keyword = keyword.capitalize()
        books = db.execute("SELECT * FROM books WHERE title LIKE :title",
                            {"title": '%' + keyword + '%'}).fetchall()

    # Search by author
    elif category == "author":
        keyword = keyword.capitalize()
        books = db.execute("SELECT * FROM books WHERE author LIKE :author",
                            {"author": '%' + keyword + '%'}).fetchall()
        
    # User did not pick category to search by
    else:
        return render_template("search.html", missing_category=True)
    
    # No book in the DB mached the search criteria
    if books == []:
        return render_template("search.html", no_book_found=True)
    else:
        return render_template("results.html", books=books)

@app.route("/book/<string:book_isbn>")
def book(book_isbn):
    """Lists details about a single book."""

    # Make sure book exists.
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": book_isbn}).fetchone()
    if book is None:
        return render_template("error.html", message="No such book.")
    
    # Update the session variable for book to the most recently viewed book
    session["book"] = book

    # Find all existing reviews for the selected book
    reviews = db.execute("SELECT username, text_opinion, rating FROM (SELECT * FROM reviews WHERE book_isbn=:isbn) AS r INNER JOIN users ON r.user_id=users.id", {"isbn": book_isbn}).fetchall()
    
    # Get review data from the Goodreads API
    goodreads_data = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "rILdgDWSEATeXeNiwPOzw", "isbns": book_isbn})
    if goodreads_data.status_code == 404:
        goodreads_data = False
    else:
        goodreads_data = goodreads_data.json()["books"][0] # Index 0 since there should only be a single book returned

    
    return render_template("book.html", book=book, reviews=reviews, goodreads_data=goodreads_data)

@app.route("/reviewSubmission", methods=["POST"])
def reviewSubmission():
    """User leaves a review on a book."""

    # Get the book we are reviewing from the user's session
    book = session["book"]
    book_isbn = book.isbn

    # Find all existing reviews for the selected book
    reviews = db.execute("SELECT username, text_opinion, rating FROM (SELECT * FROM reviews WHERE book_isbn=:isbn) AS r INNER JOIN users ON r.user_id=users.id", {"isbn": book_isbn}).fetchall()

    # Get review data from the Goodreads API
    goodreads_data = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "rILdgDWSEATeXeNiwPOzw", "isbns": book_isbn})
    if goodreads_data.status_code == 404:
        goodreads_data = False
    else:
        goodreads_data = goodreads_data.json()["books"][0] # Index 0 since there should only be a single book returned

    text_review = request.form.get("text_review")

    # Make sure the text field is used
    if text_review == "":
        return render_template("book.html", book=book, reviews=reviews, goodreads_data=goodreads_data, empty_text_review=True)

    # Make sure a rating was chosen
    rating = request.form.get("rating")
    if rating == "Choose a rating from 1 to 5":
        return render_template("book.html", book=book, reviews=reviews, goodreads_data=goodreads_data, no_rating=True)
    else:
        rating = int(rating)

    # Make sure user has not already reviewed this book
    if db.execute("SELECT * FROM reviews WHERE user_id = :user_id AND book_isbn = :book_isbn", {"user_id": session["user_id"], "book_isbn": session["book"].isbn}).rowcount != 0:
        return render_template("book.html", book=book, reviews=reviews, goodreads_data=goodreads_data, already_reviewed=True)

    # Add user review into DB
    db.execute("INSERT INTO reviews (user_id, book_isbn, text_opinion, rating) VALUES (:user_id, :book_isbn, :text_opinion, :rating)",
            {"user_id": session["user_id"], "book_isbn": session["book"].isbn, "text_opinion": text_review, "rating": rating})

    # This is the first review of the book
    if session["book"].review_count is None:
        db.execute("UPDATE books SET review_count = 1, avg_score = :rating WHERE isbn = :book_isbn", {"rating": rating, "book_isbn": session["book"].isbn})

    # Calculate new review count and average score for the book
    else:
        new_review_count = session["book"].review_count + 1
        new_avg_score = (session["book"].review_count * session["book"].avg_score + rating) / new_review_count
        db.execute("UPDATE books SET review_count = :new_review_count, avg_score = :new_avg_score WHERE isbn = :book_isbn", {"new_review_count": new_review_count, "new_avg_score": new_avg_score, "book_isbn": session["book"].isbn})

    db.commit()

    # Update the book session object and reviews variable so we have the updated review count and avg_score
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": session["book"].isbn}).fetchone()
    session["book"] = book
    reviews = db.execute("SELECT username, text_opinion, rating FROM (SELECT * FROM reviews WHERE book_isbn=:isbn) AS r INNER JOIN users ON r.user_id=users.id", {"isbn": book_isbn}).fetchall()


    return render_template("book.html", book=book, reviews=reviews, goodreads_data=goodreads_data, review_submission_successful=True)


@app.route("/register")
def register():
    """Register an account."""
    return render_template("register.html")


@app.route("/accountCreation", methods=["POST"])
def accountCreation():
    """Account created and added to DB."""

    desired_username = request.form.get("desired_username")
    pword = request.form.get("pword")

    # Make sure username is not taken
    if db.execute("SELECT * FROM users WHERE username = :username", {"username": desired_username}).rowcount != 0:
        return render_template("registrationError.html", message="That username is already taken. Please choose a different username.")
    
    db.execute("INSERT INTO users (username, pword) VALUES (:username, :pword)",
            {"username": desired_username, "pword": pword})

    # Create another user in the database with this info
    db.commit()
    return render_template("accountCreation.html")


@app.route("/api/<string:book_isbn>", methods=["GET"])
def api(book_isbn):
    """Website's API route."""

    # Make sure book exists.
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": book_isbn}).fetchone()
    if book is None:
        return abort(404, description="Book not found")
    
    # Return JSON containing book info
    return jsonify(title=book.title,
                   author=book.author,
                   year=book.pub_yr,
                   isbn=book.isbn,
                   review_count=book.review_count,
                   average_score=book.avg_score)