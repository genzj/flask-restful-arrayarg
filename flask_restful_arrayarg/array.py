import collections

import six
from flask import current_app
from flask_restful import reqparse
from flask_restful.reqparse import Argument
from operator import itemgetter
from werkzeug.datastructures import MultiDict

from flask_restful_arrayarg.nest import NestParser

try:
    from collections.abc import MutableSequence
except ImportError:
    from collections import MutableSequence


class ArrayArgument(Argument):
    def __init__(self, name, *args, **kwargs):
        if 'action' in kwargs and kwargs['actions'] != 'append':
            raise ValueError('ArrayArgument only support the append action')
        kwargs['action'] = 'append'
        super(ArrayArgument, self).__init__(name, *args, **kwargs)

    def source(self, request):
        result = super(ArrayArgument, self).source(request)
        prefix = self.name + '['
        items = collections.OrderedDict()
        for k in list(result.keys()):
            if k.startswith(prefix) and ']' in k[len(prefix):]:
                pass
            else:
                continue
            idx = k[len(prefix):k.index(']')]
            idx_int = int(idx, 10)
            remaining = k[k.index(']') + 1:]
            value = result[k]

            if self.nested:
                value, ok = self.extract_value(remaining, value, items.get(idx_int, MultiDict()))
                if not ok:
                    continue

            del result[k]
            items[idx_int] = value

        if items:
            if hasattr(result, 'setlist'):
                result.setlist(self.name, list(items.items()))
            else:
                result[self.name] = list(items.items())
        return result

    def extract_value(self, remaining, value, existing):
        _parsed = True
        _ill = False
        if not remaining:
            if not self.ignore:
                raise ValueError('residuals in array name')
            return value, _ill
        if remaining.startswith('[') and remaining.endswith(']'):
            existing[remaining[1:-1]] = value
        else:
            if not self.ignore:
                raise ValueError('illegal nest key name')
            else:
                return value, _ill
        return existing, _parsed

    @property
    def nested(self):
        return isinstance(self.type, NestParser)

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

        for operator in self.operators:
            name = self.name + operator.replace("=", "", 1)
            if name in source:
                # Account for MultiDict and regular dict
                if hasattr(source, "getlist"):
                    values = source.getlist(name)
                else:
                    values = source.get(name)
                    if not (isinstance(values, MutableSequence)):
                        values = [values]

                for idx, value in values:
                    if hasattr(value, "strip") and self.trim:
                        value = value.strip()
                    if hasattr(value, "lower") and not self.case_sensitive:
                        value = value.lower()

                        if hasattr(self.choices, "__iter__"):
                            self.choices = [choice.lower()
                                            for choice in self.choices]

                    try:
                        value = self.convert(value, operator)
                    except Exception as error:
                        if self.ignore:
                            continue
                        return self.handle_validation_error(error, bundle_errors)

                    if self.choices and value not in self.choices:
                        if current_app.config.get("BUNDLE_ERRORS", False) or bundle_errors:
                            return self.handle_validation_error(
                                ValueError(u"{0} is not a valid choice".format(
                                    value)), bundle_errors)
                        self.handle_validation_error(
                            ValueError(u"{0} is not a valid choice".format(
                                value)), bundle_errors)

                    if name in request.unparsed_arguments:
                        request.unparsed_arguments.pop(name)
                    results.append((idx, value))

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

        return collections.OrderedDict(sorted(results, key=itemgetter(0))), _found
