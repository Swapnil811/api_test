from app import ma, db
from marshmallow import validate, pre_load, pre_dump, post_dump
from webargs import fields
from book import models as m


class BaseReadArgsSchema(ma.Schema):
    """
    A base schema for reading filters, pagination, sort from args using
    webargs.
    """
    page = fields.Integer(missing=1)
    per_page = fields.Integer(missing=25)
    sort_by = fields.List(fields.String(), missing=['download_count'])
    sort = fields.String(validate=validate.OneOf(['asc', 'desc']),
                         missing='desc')
    operator = fields.String(validate=validate.OneOf(['and', 'or']),
                             missing='or')


class BookReadArgsSchema(BaseReadArgsSchema):
    book_id = fields.DelimitedList(fields.Integer(), )
    language = fields.DelimitedList(fields.String(), )
    mime_type = fields.DelimitedList(fields.String(), )
    topic = fields.DelimitedList(fields.String(), )
    author = fields.DelimitedList(fields.String(), )
    title = fields.DelimitedList(fields.String(), )


class FormatSchema(ma.Schema):
    mime_type = fields.String()
    url = fields.String()


class BookShelfSchema(ma.Schema):
    name = fields.String()


class SubjectSchema(ma.Schema):
    name = fields.String()


class LanguageSchema(ma.Schema):
    code = fields.String(dump_only=True)


class AuthorSchema(ma.Schema):
    name = fields.String(dump_only=True)
    birth_year = fields.String(dump_only=True)
    death_year = fields.String(dump_only=True)


class BookSchema(ma.Schema):
    title = fields.String(dump_only=True)
    id = fields.Integer(dump_only=True)
    gutenberg_id = fields.Integer()
    download_count = fields.Integer()

    @post_dump()
    def dump_related_data(self, data, many):
        author_ids = [_.author_id for _ in db.session.query(m.book_authors.c.author_id).filter(m.book_authors.c.book_id==data['id']).all()]
        author_rows = db.session.query(m.author).filter(m.author.c.id.in_(author_ids)).all()
        author_schema = AuthorSchema()
        data['authors'] = author_schema.dump(author_rows, many=True)

        language_ids = [_.language_id for _ in db.session.query(m.book_languages.c.language_id).filter(m.book_languages.c.book_id==data['id']).all()]
        language_rows = db.session.query(m.language).filter(m.language.c.id.in_(language_ids)).all()
        language_schema = LanguageSchema()
        data['languages'] = language_schema.dump(language_rows, many=True)

        shelf_ids = [_.bookshelf_id for _ in db.session.query(m.book_bookshelves.c.bookshelf_id).filter(
            m.book_bookshelves.c.book_id == data['id']).all()]
        shelf_rows = db.session.query(m.bookshelf).filter(m.bookshelf.c.id.in_(shelf_ids)).all()
        shelf_schema = BookShelfSchema()
        data['bookshelfs'] = shelf_schema.dump(shelf_rows, many=True)

        sub_ids = [_.subject_id for _ in db.session.query(m.book_subjects.c.subject_id).filter(
            m.book_subjects.c.book_id == data['id']).all()]
        sub_rows = db.session.query(m.subject).filter(m.subject.c.id.in_(sub_ids)).all()
        sub_schema = SubjectSchema()
        data['subjects'] = sub_schema.dump(sub_rows, many=True)

        format_rows = db.session.query(m.book_format).filter(m.book_format.c.book_id==data['id']).all()
        format_schema = FormatSchema()
        data['download_links'] = format_schema.dump(format_rows, many=True)

        return data
