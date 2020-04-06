from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy import and_, inspect, or_
from werkzeug.exceptions import HTTPException

flaskapp = Flask(__name__)
db = SQLAlchemy()
ma = Marshmallow()


def create_app(config):
    """
    Function that creates the app.
    """
    # global app object, configure it!
    flaskapp.config.from_object(config)
    db.init_app(flaskapp)
    flaskapp.app_context().push()

    configure_apis(flaskapp)
    return flaskapp


def configure_apis(app):

    from book.models import (
        book, bookshelf, book_bookshelves, author, book_authors, book_languages, language, format, subject, book_subjects)
    from book.schemas import BookReadArgsSchema, BookSchema
    from book.helpers import parse_args

    @app.route('/')
    def books():

        result = {"total": 0}
        try:
            read_schema = BookReadArgsSchema()
            book_schema = BookSchema()
            # parse the request query arguments
            filters, sort, pagination, operator = parse_args(
                read_schema)
            print(filters, sort, pagination, operator)
            # building query
            query = db.session.query(book.c.title.label('title'), book.c.id.label('id')).distinct(book.c.id)
            query_filters = []
            topics = filters.get("topic", [])
            for topic in topics:
                query = query.join(
                    book_bookshelves, book_bookshelves.c.book_id==book.c.id).join(
                    bookshelf, bookshelf.c.id==book_bookshelves.c.bookshelf_id).join(
                    book_subjects, book_subjects.c.book_id==book.c.id).join(
                    subject, book_subjects.c.subject_id==book_subjects.c.subject_id)

                # subject_ids = [_.id for _ in db.session.query(subject.c.id).filter(subject.c.name.ilike('%{}%'.format(topic))).all()]
                # bookshelf_ids = [_.id for _ in db.session.query(bookshelf.c.id).filter(subject.c.name.ilike('%{}%'.format(topic))).all()]

                # query_filters.append()
                query_filters.append(bookshelf.c.name.ilike('%{}%'.format(topic)))
                query_filters.append(subject.c.name.ilike('%{}%'.format(topic)))

            book_ids = filters.get("book_id", [])
            for id in book_ids:
                query_filters.append(book.c.gutenberg_id==id)

            languages = filters.get('language', [])
            for lang in languages:
                query = query.join(
                    book_languages, book_languages.c.book_id==book.c.id).join(
                    language, language.c.id==book_languages.c.language_id)
                query_filters.append(language.c.code==lang)

            mimes = filters.get('mime_type', [])
            for mime in mimes:
                query = query.join(
                    format, format.c.book_id==book.c.id)
                query_filters.append(format.c.mime_type==mime)

            authors = filters.get('author', [])
            if authors:
                query = query.join(
                    book_authors, book_authors.c.book_id == book.c.id).join(
                    author, author.c.id == book_authors.c.author_id)
                for authr in authors:
                    query_filters.append(author.c.name.ilike('%{}%'.format(authr)))

            titles = filters.get('title', [])
            for title in titles:
                query_filters.append(book.c.title.ilike('%{}%'.format(title)))

            if query_filters:
                op_fxn = or_
                if operator == 'and':
                    op_fxn = and_
                query = query.filter(op_fxn(*query_filters))
            print(query)
            result["total"] = query.count()
            # models = [m for m in query.items]
            query = query.paginate(pagination['page'], pagination['per_page'], error_out=False)

            result["books"] = book_schema.dump(query.items, many=True)
            return result
        except HTTPException as e:
            raise e
        except Exception as e:
            print(e)
            raise e
            return "Internal server error"