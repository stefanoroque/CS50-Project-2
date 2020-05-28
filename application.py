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

@app.route("/register")
def register():
    """Register an account."""
    return render_template("register.html")

@app.route("/accountCreation", methods=["POST"])
def accountCreation():
    """search for a book."""

    desired_username = request.form.get("desired_username")
    pword = request.form.get("pword")

    print("-----------")
    print(desired_username)
    print(pword)
    print("-----------")

    #TODO: now need to make sure username is not taken, and password is acceptable
    if db.execute("SELECT * FROM users WHERE username = :username", {"username": desired_username}).rowcount != 0:
        return render_template("registrationError.html", message="That username is already taken. Please choose a different username.")
    db.execute("INSERT INTO users (username, pword) VALUES (:username, :pword)",
            {"username": desired_username, "pword": pword})
    db.commit()

    #TODO: create another user in the database with this info

    # try:
    #     flight_id = int(request.form.get("flight_id"))
    # except ValueError:
    #     return render_template("error.html", message="Something went wrong. Try another username")

    #   # Make sure the flight exists.
    #   if db.execute("SELECT * FROM flights WHERE id = :id", {"id": flight_id}).rowcount == 0:
    #       return render_template("error.html", message="No such flight with that id.")
    #   db.execute("INSERT INTO passengers (name, flight_id) VALUES (:name, :flight_id)",
    #           {"name": name, "flight_id": flight_id})
    #   db.commit()
    return render_template("accountCreation.html")



