from collections import OrderedDict

from flask_restful import reqparse

from flask_restful_arrayarg import __version__
from flask_restful_arrayarg.array import ArrayArgument


class MockRequest(object):
    # noinspection PyProtectedMember
    __slots__ = list(reqparse._friendly_location.keys()) + ['unparsed_arguments', ]


def test_version():
    assert __version__ == '0.1.0'


def test_plain_parse():
    req = MockRequest()
    req.values = {
        'rate': 10,
        'name': 'request1',
        'arr[0]': 'a',
    }
    parser = reqparse.RequestParser()
    parser.add_argument('rate', type=int, help='Rate cannot be converted')
    parser.add_argument('name')
    args = parser.parse_args(req)
    assert args['rate'] == 10
    assert args['name'] == 'request1'


def test_simple_array():
    req = MockRequest()
    req.values = {
        'rate': 10,
        'name': 'request1',
        'arr1[0]': 'a',
        'arr1[1]': 'b',
        'arr1[2]': '999',
        'arr2[0]': '1',
        'arr2[1]': 3,
    }
    parser = reqparse.RequestParser()
    parser.add_argument('rate', type=int, help='Rate cannot be converted')
    parser.add_argument('name')
    parser.add_argument(ArrayArgument(
        'arr1'
    ))
    parser.add_argument(ArrayArgument(
        'arr2', type=int
    ))
    args = parser.parse_args(req)
    assert args['rate'] == 10
    assert args['name'] == 'request1'
    assert args['arr1'] == OrderedDict([
        (0, 'a'), (1, 'b'), (2, '999'),
    ])
    assert args['arr2'] == OrderedDict([
        (0, 1), (1, 3)
    ])


def test_sparse_array():
    req = MockRequest()
    req.values = {
        'rate': 10,
        'name': 'request1',
        'arr2[1]': '1',
        'arr2[2]': 3,
    }
    parser = reqparse.RequestParser()
    parser.add_argument('rate', type=int, help='Rate cannot be converted')
    parser.add_argument('name')
    parser.add_argument(ArrayArgument(
        'arr2', type=int
    ))
    args = parser.parse_args(req)
    assert args['rate'] == 10
    assert args['name'] == 'request1'
    assert args['arr2'] == OrderedDict([
        (1, 1), (2, 3)
    ])


def test_single_location_array():
    req = MockRequest()
    req.values = {
        'rate': 10,
        'name': 'request1',
        'arr2[1]': '1',
        'arr2[2]': 3,
    }
    parser = reqparse.RequestParser()
    parser.add_argument('rate', type=int, help='Rate cannot be converted')
    parser.add_argument('name')
    parser.add_argument(ArrayArgument(
        'arr2', type=int, location='values',
    ))
    args = parser.parse_args(req)
    assert args['rate'] == 10
    assert args['name'] == 'request1'
    assert args['arr2'] == OrderedDict([
        (1, 1), (2, 3)
    ])
