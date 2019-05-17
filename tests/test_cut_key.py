# -*- encoding: utf-8 -*-
from flask_restful_arrayarg.util import cut_key


def test_cut_array():
    k = '[0][1]'
    cut = cut_key(k)
    assert cut == ['0', '1']

def test_cut_struct():
    k = '[x]'
    cut = cut_key(k)
    assert cut == ['x']


def test_cut_nested():
    k = '[1][xx][yy]'
    cut = cut_key(k)
    assert cut == ['1', 'xx', 'yy']
