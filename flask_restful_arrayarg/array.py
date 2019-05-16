import collections

import six
from flask import current_app
from flask_restful import reqparse
from flask_restful.reqparse import Argument
from operator import itemgetter
from werkzeug.datastructures import MultiDict


class ArrayArgument(Argument):
    def __init__(self, name, *args, **kwargs):
        if 'action' in kwargs and kwargs['actions'] != 'append':
            raise ValueError('ArrayArgument only support the append action')
        kwargs['action'] = 'append'
        super().__init__(name, *args, **kwargs)

    def source(self, request):
        result = super().source(request)
        prefix = self.name + '['
        items = []
        for k in list(result.keys()):
            if k.startswith(prefix) and ']' in k[len(prefix):]:
                pass
            else:
                continue
            idx = k[len(prefix):len(prefix) + k[len(prefix):].index(']')]
            items.append((int(idx, 10), result.pop(k)))
        if items:
            if hasattr(result, 'setlist'):
                result.setlist(self.name, items)
            else:
                result[self.name] = items
        return result

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
                    if not (isinstance(values, collections.MutableSequence)):
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

        sorted(results, key=itemgetter(0))

        return collections.OrderedDict(results), _found
