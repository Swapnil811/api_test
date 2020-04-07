import os

SQLALCHEMY_DATABASE_URI = 'postgresql://manishmaurya:231292@localhost' +\
    ':5432/gutendex'

# Define the application directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

DEBUG = False
