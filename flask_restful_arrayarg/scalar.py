# -*- encoding: utf-8 -*-
from collections import OrderedDict
from operator import itemgetter

from flask_restful.reqparse import text_type, Argument

from flask_restful_arrayarg.array import SubParser


class ExtractedValues(object):
    __slots__ = ['value', 'unparsed_arguments']

    def __init__(self, value):
        self.value = value

    @property
    def extracted(self):
        return {'': self.value}


class ScalarParser(SubParser):
    def __init__(self, type=text_type, *args, **kwargs):
        super(ScalarParser, self).__init__(*args, **kwargs)
        if isinstance(type, SubParser):
            self.add_argument(type)
        else:
            self.add_argument('', type=type)

    def add_argument(self, *args, **kwargs):
        if len(args) == 1 and isinstance(args[0], (Argument, SubParser)):
            self.arg = args[0]
        else:
            self.arg = Argument(*args, **kwargs)
        if isinstance(self.arg, Argument):
            self.arg.location = 'scalar'

    def get_argument(self, key):
        try:
            return int(key, 10), self.arg
        except (ValueError, TypeError):
            return key, None
