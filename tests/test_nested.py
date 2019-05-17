from flask_restful import reqparse
from flask_restful.reqparse import Namespace

from flask_restful_arrayarg.array import ArrayArgument
from flask_restful_arrayarg.nest import NestParser
from tests.mock import MockRequest


def test_nested():
    req = MockRequest()
    req.values = {
        'rate': 10,
        'name': 'request1',
        'arr[0][x]': 'a',
        'arr[0][y]': '1',
        'arr[0][z]': 'z',

        'arr[1][x]': 'b',
        'arr[1][y]': '3',
        'arr[1][z]': 's',

        'arr[2][x]': 'c',
        'arr[2][z]': 'z',
    }
    parser = reqparse.RequestParser()
    parser.add_argument('rate', type=int, help='Rate cannot be converted')
    parser.add_argument('name')

    sub_parser = NestParser()
    sub_parser.add_argument('x')
    sub_parser.add_argument('y', type=int, help='y should be int')
    sub_parser.add_argument('z')

    parser.add_argument(ArrayArgument('arr', type=sub_parser))

    args = parser.parse_args(req)
    assert args['rate'] == 10
    assert args['name'] == 'request1'

    assert args['arr'][0] == Namespace(
        x='a', y=1, z='z'
    )
    assert args['arr'][1] == Namespace(
        x='b', y=3, z='s'
    )
    assert args['arr'][2] == Namespace(
        x='c', y=None, z='z'
    )
