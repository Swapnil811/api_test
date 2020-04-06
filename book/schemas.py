from app import ma
from marshmallow import validate, pre_load
from webargs import fields


class BaseReadArgsSchema(ma.Schema):
    """
    A base schema for reading filters, pagination, sort from args using
    webargs.
    """
    page = fields.Integer(load_only=True, missing=1)
    per_page = fields.Integer(load_only=True, missing=25)
    sort_by = fields.List(fields.String(), load_only=True, missing=['download_count'])
    sort = fields.String(validate=validate.OneOf(['asc', 'desc']),
                         missing='desc')


class BookReadArgsSchema(BaseReadArgsSchema):
    book_id = fields.DelimitedList(fields.Integer(), load_only=True)
    language = fields.DelimitedList(fields.String(), load_only=True)
    mime_type = fields.DelimitedList(fields.String(), load_only=True)
    topic = fields.DelimitedList(fields.String(), load_only=True)
    author = fields.DelimitedList(fields.String(), load_only=True)
    title = fields.DelimitedList(fields.String(), load_only=True)


    # @pre_load()
    # def split_data(self, data, **kwargs):
    #     print(data['language'])
    #     return data


class BookSchema(ma.Schema):
    title = fields.String(dump_only=True)
    id = fields.Integer(dump_only=True)
