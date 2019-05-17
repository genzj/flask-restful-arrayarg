# -*- encoding: utf-8 -*-
# DataTables server side parameters
# https://datatables.net/manual/server-side
from flask_restful import reqparse

from flask_restful_arrayarg.array import ArrayArgument
from flask_restful_arrayarg.nest import NestParser
from flask_restful_arrayarg.scalar import ScalarParser

parser = reqparse.RequestParser()
parser.add_argument('draw', type=int)
parser.add_argument('start', type=int)
parser.add_argument('length', type=int)

bool_str = lambda x: x.strip().lower() == 'true'
global_search_parser = NestParser()
global_search_parser.add_argument('value')
global_search_parser.add_argument('regex', type=bool_str)

order_parser = NestParser()
order_parser.add_argument('column', type=int)
order_parser.add_argument('dir', choices=('asc', 'desc'))

column_search_parser = NestParser(name='search')
column_search_parser.args = dict(global_search_parser.args)

columns_parser = NestParser()
columns_parser.add_argument('data')
columns_parser.add_argument('name')
columns_parser.add_argument('searchable', type=bool_str)
columns_parser.add_argument('orderable', type=bool_str)
columns_parser.add_argument(column_search_parser)

parser.add_argument(ArrayArgument('search', type=global_search_parser))
parser.add_argument(ArrayArgument('order', type=ScalarParser(type=order_parser)))
parser.add_argument(ArrayArgument('columns', type=ScalarParser(type=columns_parser)))
