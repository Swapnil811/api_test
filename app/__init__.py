import json

from flask import Flask, Response, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy import and_, inspect, or_, asc, desc
from werkzeug.exceptions import HTTPException

from config import BASE_DIR

flaskapp = Flask(__name__, template_folder=BASE_DIR)
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
        book, bookshelf, book_bookshelves, author, book_authors, book_languages, language, book_format, subject, book_subjects)
    from book.schemas import BookReadArgsSchema, BookSchema
    from book.helpers import parse_args

    @app.route('/')
    def readme():
        f = open('readme.txt', 'r')
        lines = f.readlines()
        f.close()
        return render_template('index.html', **{"lines": lines})

    @app.route('/books')
    def books():

        result = {"total": 0}
        try:
            read_schema = BookReadArgsSchema()
            book_schema = BookSchema()
            # parse the request query arguments
            filters, sort, pagination, operator = parse_args(
                read_schema)

            # building query
            query = db.session.query(book)
            query_filters = []
            topics = filters.get("topic", [])
            for topic in topics:
                subject_ids = [_.id for _ in db.session.query(subject.c.id).filter(subject.c.name.ilike('%{}%'.format(topic))).all()]
                bookshelf_ids = [_.id for _ in db.session.query(bookshelf.c.id).filter(bookshelf.c.name.ilike('%{}%'.format(topic))).all()]

                shelf_book_ids = {_.book_id for _ in db.session.query(book_bookshelves.c.book_id).filter(book_bookshelves.c.bookshelf_id.in_(bookshelf_ids))}
                subject_book_ids = {_.book_id for _ in db.session.query(book_subjects.c.book_id).filter(book_subjects.c.subject_id.in_(subject_ids))}
                matching_book_ids = shelf_book_ids.union(subject_book_ids)
                query_filters.append(book.c.id.in_(matching_book_ids))

            book_ids = filters.get("book_id", [])
            for id in book_ids:
                query_filters.append(book.c.gutenberg_id==id)

            languages = filters.get('language', [])
            if languages:
                query = query.join(
                    book_languages, book_languages.c.book_id == book.c.id).join(
                    language, language.c.id == book_languages.c.language_id)
            for lang in languages:
                query_filters.append(language.c.code==lang)

            mimes = filters.get('mime_type', [])
            if mimes:
                query = query.join(
                    book_format, book_format.c.book_id == book.c.id)
            for mime in mimes:
                query_filters.append(book_format.c.mime_type==mime)

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

            result["total"] = query.count()
            order = []
            sort_columns = inspect(book).columns
            for column in sort['sort_by']:
                sort_fxn = desc
                if sort['sort'] == 'asc':
                    sort_fxn = asc
                if column in sort_columns:
                    order.append(sort_fxn(sort_columns[column]))

            query = query.order_by(*order).paginate(pagination['page'], pagination['per_page'], error_out=False)
            result["books"] = book_schema.dump(query.items, many=True)

            return Response(json.dumps(result), status=200, mimetype='application/json')
        except HTTPException as e:
            raise e
        except Exception as e:
            print(e)
            return "Internal server error", 500