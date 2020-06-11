# Project 1

This is a book review website that I made for my Harvard CS50 web programming course. It is not pretty, as the focus was more on the functionality of the site. I wanted to move onto the next project without spending too much time on the visual asthetic of this one. 

Users are able to register for the website and then log in using their username and password. Once they log in, they are able to search for books, leave reviews for individual books, and see the reviews made by other people. The site also uses the third-party API by Goodreads, another book review website, to pull in ratings from a broader audience. Finally, users are able to query for book details and book reviews programmatically via the website’s API.

## What is contained in each file:
- application.py: Main flask application that is the backend of the website
- books.csv: CSV file that was used to populate the database
- create.sql: SQL file that was used to create the database
- import.py: Python script that was used to import the data from the CSV file into the database
- requirements.txt: requirements file
- templates folder: This folder contains all the HTML files that are used to create the UI of the website. Contains 11 HTML files
