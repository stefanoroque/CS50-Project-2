class User:

    def __init__(self, id, username, pword):
        self.id = id
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
        review_count = 0
        avg_score = None


class Review:

    def __init__(self, user_id, book_isbn, text_opinion, rating):
        self.user_id = user_id
        self.book_isbn = book_isbn
        self.text_opinion = text_opinion
        self.rating = rating

        
