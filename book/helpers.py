from webargs.flaskparser import parser
from flask import request


def parse_args(read_schema):
        """
        Parses the request arguments for field filters, sort and pagination
        """
        try:
            input_data = parser.parse(read_schema, location='querystring')
        except Exception as e:
            raise e

        # all good with incoming data, so continue
        filters = {}
        pfields = []
        sort = {}
        pagination = {}  # per_page, page number
        operator = ''
        if not input_data:
            return filters, pfields, sort, pagination, operator

        # there are filter arguments, so parse them, and separate into
        # filters, sort, pagination
        for k in input_data:
            if k in ['sort_by', 'sort', 'per_page', 'page']:
                # sort out sorting
                if k == 'sort':
                    sort['sort'] = input_data['sort']
                if k == 'sort_by':
                    sort['sort_by'] = input_data['sort_by']
                # sort out pagination
                if k == 'per_page':
                    try:
                        pagination['per_page'] = int(input_data['per_page'])
                    except Exception:
                        pagination['per_page'] = 25
                if k == 'page':
                    try:
                        pagination['page'] = int(input_data['page'])
                    except Exception:
                        pagination['page'] = 1
                continue

            # operator
            if k == 'operator':
                operator = input_data[k]
                continue
            # filters
            if input_data[k] or input_data[k] is False or input_data[k] == 0:
                filters[k] = input_data[k]
        return filters, sort, pagination, operator


