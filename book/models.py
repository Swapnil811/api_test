from app import db


# class Book(db.Model):
#     __tablename__ = 'books_book'
#
#     id = db.Column(db.BigInteger, primary_key=True)
#     download_count = db.Column(db.BigInteger)

book = db.Table('books_book', db.metadata, autoload=True, autoload_with=db.engine)
bookshelf = db.Table('books_bookshelf', db.metadata, autoload=True, autoload_with=db.engine)
book_bookshelves = db.Table('books_book_bookshelves', db.metadata, autoload=True, autoload_with=db.engine)
language = db.Table('books_language', db.metadata, autoload=True, autoload_with=db.engine)
book_languages = db.Table('books_book_languages', db.metadata, autoload=True, autoload_with=db.engine)
subject = db.Table('books_subject', db.metadata, autoload=True, autoload_with=db.engine)
book_subjects = db.Table('books_book_subjects', db.metadata, autoload=True, autoload_with=db.engine)
format = db.Table('books_format', db.metadata, autoload=True, autoload_with=db.engine)
author = db.Table('books_author', db.metadata, autoload=True, autoload_with=db.engine)
book_authors = db.Table('books_book_authors', db.metadata, autoload=True, autoload_with=db.engine)