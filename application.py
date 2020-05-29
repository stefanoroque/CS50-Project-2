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
    """Search for a book."""

    username = request.form.get("username")
    pword = request.form.get("pword")

    if db.execute("SELECT * FROM users WHERE username = :username AND pword = :pword", {"username": username, "pword": pword}).rowcount == 0:  
        return render_template("loginError.html", message="Incorrect username or password.")

    return render_template("loginError.html", message="LOGGED IN")

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



