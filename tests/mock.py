from flask_restful import reqparse


class MockRequest(object):
    # noinspection PyProtectedMember
    __slots__ = list(reqparse._friendly_location.keys()) + ['unparsed_arguments', ]