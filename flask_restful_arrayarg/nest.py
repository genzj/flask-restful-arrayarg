from flask_restful.reqparse import RequestParser, Argument

from flask_restful_arrayarg.array import SubParser


class NestedValue(object):
    __slots__ = ['value', 'unparsed_arguments']

    def __init__(self, value):
        self.value = value

    @property
    def nested(self):
        return self.value


class NestParser(SubParser):
    def __init__(self, name='', *args, **kwargs):
        super(SubParser, self).__init__(*args, **kwargs)
        self.name = name
        self.args = dict()

    def add_argument(self, *args, **kwargs):
        if len(args) == 1 and isinstance(args[0], (Argument, SubParser)):
            arg = args[0]
        else:
            arg = Argument(*args, **kwargs)

        if isinstance(arg, Argument):
            arg.location = 'nest'

        self.args[arg.name or ''] = arg

    def get_argument(self, key):
        return key, self.args.get(key)
