import os

from flask import Flask, session, render_template, request
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

    return render_template("search.html")

@app.route("/search", methods=["POST"])
def search():
    """User Searches for a book in the DB."""

    category = request.form.get("category")
    keyword = request.form.get("keyword")

    if category == "isbn":
        keyword = keyword.upper()
        books = db.execute("SELECT * FROM books WHERE isbn LIKE :isbn",
                            {"isbn": '%' + keyword + '%'}).fetchall()

    elif category == "title":
        keyword = keyword.capitalize()
        books = db.execute("SELECT * FROM books WHERE title LIKE :title",
                            {"title": '%' + keyword + '%'}).fetchall()

    elif category == "author":
        keyword = keyword.capitalize()
        books = db.execute("SELECT * FROM books WHERE author LIKE :author",
                            {"author": '%' + keyword + '%'}).fetchall()
        
    else:
        return render_template("search.html", missing_category=True)

    #TODO: MAKE SURE TEXT BOX IS NOT EMPTY STRING
    
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

    return render_template("book.html", book=book)

@app.route("/reviewSubmission", methods=["POST"])
def reviewSubmission():
    """User leaves a review on a book."""

    text_review = request.form.get("text_review")
    rating = int(request.form.get("rating"))
    book = session["book"]

    # Make sure the text field is used
    if text_review == "":
        return render_template("book.html", book=book, empty_text_review=True)

    # Make sure a rating was chosen
    if rating == "Choose a rating from 1 to 5":
        return render_template("book.html", book=book, no_rating=True)

    # Make sure user has not already reviewed this book
    if db.execute("SELECT * FROM reviews WHERE user_id = :user_id AND book_isbn = :book_isbn", {"user_id": session["user_id"], "book_isbn": session["book"].isbn}).rowcount != 0:
        return render_template("book.html", book=book, already_reviewed=True)

    db.execute("INSERT INTO reviews (user_id, book_isbn, text_opinion, rating) VALUES (:user_id, :book_isbn, :text_opinion, :rating)",
            {"user_id": session["user_id"], "book_isbn": session["book"].isbn, "text_opinion": text_review, "rating": rating})

    #TODO: modify review count and average score for selected book
    # This is the first review of the book
    if session["book"].review_count is None:
        db.execute("UPDATE books SET review_count = 1, avg_score = :rating WHERE isbn = :book_isbn", {"rating": rating, "book_isbn": session["book"].isbn})

    else:
        new_review_count = session["book"].review_count + 1
        new_avg_score = (session["book"].review_count * session["book"].avg_score + rating) / new_review_count
        db.execute("UPDATE books SET review_count = :new_review_count, avg_score = :new_avg_score WHERE isbn = :book_isbn", {"new_review_count": new_review_count, "new_avg_score": new_avg_score, "book_isbn": session["book"].isbn})

    db.commit()

    # Update the book session object so we have the updated review count and avg_score
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": session["book"].isbn}).fetchone()
    session["book"] = book

    return render_template("book.html", book=book, review_submission_successful=True)


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



