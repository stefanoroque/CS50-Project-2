import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine("postgres://gtxdubrxzbnzmk:63ac9ab681fdced525b0cba7fbeb7c04eef07192dac6309955cda15fecf7084f@ec2-18-214-211-47.compute-1.amazonaws.com:5432/d1js80b39pfvan")
#engine = create_engine(os.getenv("postgres://gtxdubrxzbnzmk:63ac9ab681fdced525b0cba7fbeb7c04eef07192dac6309955cda15fecf7084f@ec2-18-214-211-47.compute-1.amazonaws.com:5432/d1js80b39pfvan"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    f = open("books.csv")
    reader = csv.reader(f)
    first_row = True
    
    for isbn, title, author, pub_yr in reader:
        #print(isbn, title, author, pub_yr)
        if first_row:
            first_row=False
            continue
        
        db.execute("INSERT INTO books (isbn, title, author, pub_yr) VALUES (:isbn, :title, :author, :pub_yr)",
                    {"isbn": isbn, "title": title, "author": author, "pub_yr": pub_yr})
        print(f"Added {title} by {author} written in {pub_yr} with isbn {isbn}")
    db.commit()

if __name__ == "__main__":
    main()
