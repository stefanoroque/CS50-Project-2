import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine("postgres://ryrmnnlocwkikr:7474a4338387f21e422b38960226d79bea3d1ee85c4d213fe17b90d48acea52f@ec2-54-234-28-165.compute-1.amazonaws.com:5432/dea8evbomlivbl")
db = scoped_session(sessionmaker(bind=engine))

def main():
    f = open("books.csv")
    reader = csv.reader(f)
    first_row = True
    
    for isbn, title, author, pub_yr in reader:
        if first_row:
            first_row=False
            continue
        
        db.execute("INSERT INTO books (isbn, title, author, pub_yr) VALUES (:isbn, :title, :author, :pub_yr)",
                    {"isbn": isbn, "title": title, "author": author, "pub_yr": pub_yr})
        print(f"Added {title} by {author} written in {pub_yr} with isbn {isbn}")
    db.commit()
    print("All books added successfully!!!")

if __name__ == "__main__":
    main()
