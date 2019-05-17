# -*- encoding: utf-8 -*-
from flask_restful.reqparse import Namespace

from flask_restful_arrayarg.recipe import datatables
from tests.mock import MockRequest


def test_datatables():
    req = MockRequest()
    req.values = {
        'draw': '1',
        'start': '9',
        'length': '50',

        'search[value]': 'filter',
        'search[regex]': 'false',

        'order[1][column]': '3',
        'order[1][dir]': 'asc',

        'order[2][column]': '1',
        'order[2][dir]': 'desc',

        'columns[1][data]': 'date',
        'columns[1][name]': 'Date',
        'columns[1][searchable]': 'false',
        'columns[1][orderable]': 'true',

        'columns[2][data]': 'idx',
        'columns[2][name]': 'Index',
        'columns[2][searchable]': 'true',
        'columns[2][orderable]': 'true',
        'columns[2][search][value]': '112x3',
        'columns[2][search][regex]': 'true',

        'columns[3][data]': 'name',
        'columns[3][name]': 'Name',
        'columns[3][searchable]': 'true',
        'columns[3][orderable]': 'true',
    }
    expected = Namespace()
    expected['draw'] = 1
    expected['start'] = 9
    expected['length'] = 50
    expected['search'] = Namespace(value='filter', regex=False)
    expected['order'] = Namespace({
        1: Namespace(column=3, dir='asc'),
        2: Namespace(column=1, dir='desc'),
    })
    expected['columns'] = Namespace({
        1: Namespace(data='date', name='Date', searchable=False, orderable=True),
        2: Namespace(
            data='idx', name='Index', searchable=True, orderable=True,
            search=Namespace(value='112x3', regex=True)
        ),
        3: Namespace(data='name', name='Name', searchable=True, orderable=True),
    })

    arg = datatables.parser.parse_args(req)
    assert arg == expected
