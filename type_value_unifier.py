# coding: utf-8
import inspect

import enum


class TypeValueUnifier(object):

    def __init__(self, variable_name=None):
        self._variable_name = \
            variable_name or self.__class__.__name__ + u'() argument'

    def type_check(self):
        value = self._value
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
        self.type_check()
        unified_value = self.unify(self._value)
        self.validate(unified_value)
        return unified_value

    def error(self, msg, soft=False):
        word = u'could' if soft else u'must'
        full_msg = (u'%s %s be ' + msg + u', not: %s') % \
            (self._variable_name, word, unicode(self._value))
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


class EnumTypeValueUnifier(TypeValueUnifier):

    def _get_enum_type(self):
        for type_ in self.TYPES:
            if issubclass(type_, enum.Enum):
                return type_

    def type_check(self):
        value = self._value
        if isinstance(value, str):
            enum_type = self._get_enum_type()
            try:
                self._value = getattr(enum_type, value)
            except AttributeError:
                msg = enum_type.__name__ + u"'s variant name"
                self.error(msg, soft=True)
            return
        super(EnumTypeValueUnifier, self).type_check()


def instance(class_, enum=False):
    base = EnumTypeValueUnifier if enum else TypeValueUnifier

    class InstanceTypeValueUnifier(base):
        TYPES = (class_,)

    return InstanceTypeValueUnifier
