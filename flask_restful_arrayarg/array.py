import collections

import six
from flask import current_app
from flask_restful import reqparse
from flask_restful.reqparse import Argument, Namespace
from werkzeug.datastructures import MultiDict

from flask_restful_arrayarg.util import cut_key

try:
    from collections.abc import MutableSequence
except ImportError:
    from collections import MutableSequence


class SubParser(object):
    def add_argument(self, *args, **kwargs):
        pass

    def get_argument(self, key):
        pass


class ArrayArgument(Argument):
    def __init__(self, name, *args, **kwargs):
        super(ArrayArgument, self).__init__(name, *args, **kwargs)
        if not isinstance(self.type, SubParser):
            raise TypeError('type of array argument must be a SubParser instance')

    def source(self, request):
        result = super(ArrayArgument, self).source(request)
        prefix = self.name + '['
        items = collections.OrderedDict()
        for k in list(result.keys()):
            if not k.startswith(prefix):
                continue
            segments = cut_key(k[len(self.name):])
            value = result.pop(k)

            items[tuple(segments)] = value

        if items:
            result[self.name] = items
        return result

    def parse_single(self, keys, values, bundle_errors):
        arg = self.type
        formatted_keys = []
        for idx, k in enumerate(keys):
            formatted_k, arg = arg.get_argument(k)
            formatted_keys.append(formatted_k)
            if isinstance(arg, Argument):
                # hit leaf argument
                if idx != len(keys) - 1:
                    return self.handle_validation_error(
                        ValueError('key %r exceeded desired level' % (keys,)),
                        bundle_errors
                    )
        if not isinstance(arg, Argument):
            return self.handle_validation_error(
                ValueError('key %r unmet desired level' % (keys,)),
                bundle_errors
            )

        if isinstance(arg.location, six.string_types):
            location = arg.location
        else:
            location = arg.location[0]
        req = Namespace()
        req['unparsed_arguments'] = dict()
        req[location] = {arg.name: values}

        result, found = arg.parse(req, bundle_errors)
        return tuple(formatted_keys), result, found

    def pack(self, results):
        packed = Namespace()
        for keys, value in results:
            target = packed
            for k in keys[:-1]:
                target = target.setdefault(k, Namespace())
            target[keys[-1]] = value
        return packed

    # noinspection PyProtectedMember
    def parse(self, request, bundle_errors=False):
        try:
            source = self.source(request)
        except Exception as error:
            if self.ignore:
                source = MultiDict()
            else:
                return self.handle_validation_error(error, bundle_errors)

        results = []

        # Sentinels
        _not_found = False
        _found = True

        name = self.name
        if name in source:
            extracted = source[name]
            for keys, values in extracted.items():
                formatted_keys, one, found = self.parse_single(keys, values, bundle_errors)
                if found:
                    results.append((formatted_keys, one))

        if not results and self.required:
            if isinstance(self.location, six.string_types):
                error_msg = u"Missing required parameter in {0}".format(
                    reqparse._friendly_location.get(self.location, self.location)
                )
            else:
                friendly_locations = [reqparse._friendly_location.get(loc, loc)
                                      for loc in self.location]
                error_msg = u"Missing required parameter in {0}".format(
                    ' or '.join(friendly_locations)
                )
            if current_app.config.get("BUNDLE_ERRORS", False) or bundle_errors:
                return self.handle_validation_error(ValueError(error_msg), bundle_errors)
            self.handle_validation_error(ValueError(error_msg), bundle_errors)

        if not results:
            if callable(self.default):
                return self.default(), _not_found
            else:
                return self.default, _not_found

        return self.pack(results), _found
