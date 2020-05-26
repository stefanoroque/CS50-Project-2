class User:

    counter = 1

    def __init__(self, id, username, pword):
        self.id = User.counter
        User.counter += 1
        self.username = username
        self.pword = pword

        # Keep track of all the reviews that the user writes
        self.reviews = []


class Book:

    def __init__(self, isbn, title, author, pub_yr):
        self.isbn = isbn
        self.title = title
        self.author = author
        self.pub_yr = pub_yr

        #Keep track of review count and average score of book
        self.review_count = 0
        self.avg_score = None


class Review:

    def __init__(self, user_id, book_isbn, text_opinion, rating):
        self.user_id = user_id
        self.book_isbn = book_isbn
        self.text_opinion = text_opinion
        self.rating = rating


# from flask_sqlalchemy import SQLAlchemy

# db = SQLAlchemy()

# class User(db.Model):

#     counter = 1

#     def __init__(self, username, pword):
#         __tablename__ = "users"
#         id = db.Column(db.Integer, primary_key=True)
#         username = db.Column(db.String, nullable=False)
#         pword = db.Column(db.String, nullable=False)




# class Book(db.Model):

#     def __init__(self, isbn, title, author, pub_yr):
#         __tablename__ = "books"
#         isbn = db.Column(db.String, primary_key=True)
#         title = db.Column(db.String, nullable=False)
#         author = db.Column(db.String, nullable=False)
#         pub_yr = db.Column(db.Integer)
#         review_count = db.Column(db.Integer)
#         avg_score = db.Column(db.Integer)





# class Review:

#     def __init__(self, user_id, book_isbn, text_opinion, rating):
#         __tablename__ = "reviews"
#         user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
#         book_isbn = db.Column(db.String, db.ForeignKey("books.id"), nullable=False)
#         text_opinion = db.Column(db.String, nullable=False)
#         rating = db.Column(db.Integer, nullable=False)


