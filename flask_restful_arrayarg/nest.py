from flask_restful.reqparse import RequestParser


class NestedValue(object):
    def __init__(self, value):
        self.value = value

    @property
    def nested(self):
        return self.value


class NestParser(RequestParser):
    def add_argument(self, *args, **kwargs):
        super(NestParser, self).add_argument(*args, **kwargs)
        self.args[-1].location = 'nested'

    def __call__(self, value, name, op):
        ans = self.parse_args(req=NestedValue(value))
        return ans
