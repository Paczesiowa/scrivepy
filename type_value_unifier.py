# coding: utf-8
import inspect


class TypeValueUnifier(object):

    def __init__(self, variable_name=None):
        self._variable_name = \
            variable_name or self.__class__.__name__ + u'() argument'

    def type_check(self, value):
        types = self.__class__.TYPES
        if isinstance(value, types):
            return

        if len(types) == 1:
            possible_types_string = types[0].__name__
        else:
            possible_types_string = \
                u', '.join([type_.__name__ for type_ in types[:-1]]) \
                + u' or ' + types[-1].__name__

        err_msg = u'%s must be %s, not %s' % (self._variable_name,
                                              possible_types_string,
                                              unicode(self._value))
        raise TypeError(err_msg)

    def unify_validate(self, value):
        self._value = value
        self.type_check(value)
        unified_value = self.unify(value)
        self.validate(unified_value)
        return unified_value

    def error(self, msg):
        full_msg = (u'%s should be ' + msg + u', not: %s') % \
            (self._variable_name, unicode(self._value))
        raise ValueError(full_msg)

    def unify(self, value):
        return value

    def validate(self, value):
        pass


def validate_and_unify(**arg_validators):
    def wrapper(fun):
        def inner_wrapper(*args, **kwargs):
            args_values = inspect.getcallargs(fun, *args, **kwargs)
            for arg in args_values:
                try:
                    validator = arg_validators[arg]
                except KeyError:
                    pass
                else:
                    args_values[arg] = \
                        validator(arg).unify_validate(args_values[arg])
            return fun(**args_values)
        return inner_wrapper
    return wrapper


def instance(class_):
    class InstanceTypeValueUnifier(TypeValueUnifier):
        TYPES = (class_,)

    return InstanceTypeValueUnifier


##############################
class NonNegativeInt(TypeValueUnifier):

    TYPES = (str, unicode, int)

    def unify(self, value):
        try:
            return int(value)
        except (ValueError, UnicodeEncodeError):
            self.error(u'invalid value')

    def validate(self, value):
        if value < 0:
            self.error(u'unexpected negative integer')


class AsciiString(TypeValueUnifier):

    TYPES = (str, unicode)

    def unify(self, value):
        if isinstance(value, unicode):
            try:
                return value.encode('ascii')
            except UnicodeEncodeError:
                self.error(u'ascii only')
        else:
            return value
