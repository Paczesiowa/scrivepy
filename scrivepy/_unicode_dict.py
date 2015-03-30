import type_value_unifier as tvu
from scrivepy import _object


class TextMappingOrIterable(tvu.TypeValueUnifier):

    def type_check(self):
        value = self._value
        if isinstance(value, dict):
            return
        try:
            iter(value)
            return
        except TypeError:
            err_msg = (u'%s must be a mapping or iterable, not %s'
                       % (self._variable_name, unicode(self._value)))
            raise TypeError(err_msg)

    def unify(self, value):
        if isinstance(value, dict):
            value = value.items()
        result = {}
        for pair in iter(value):
            try:
                key, val = pair
            except Exception:
                self.error(u'')
            else:
                key = \
                    tvu.Text(self._variable_name + u' key').unify_validate(key)
                val = tvu.Text(self._variable_name + u' value') \
                         .unify_validate(val)
                result[key] = val
        return result


class UnicodeDict(dict, _object.ScriveObject):

    @tvu.validate_and_unify(iterable=TextMappingOrIterable,
                            kwargs=TextMappingOrIterable)
    def __init__(self, iterable=(), **kwargs):
        dict.__init__(self, iterable, **kwargs)
        _object.ScriveObject.__init__(self)
        self._derived_objs = []

    def _set_read_only(self):
        for obj in self._derived_objs:
            obj._set_read_only()
        super(UnicodeDict, self)._set_read_only()

    def _set_invalid(self):
        for obj in self._derived_objs:
            obj._set_invalid()
        super(UnicodeDict, self)._set_invalid()

    def clear(self):
        self._check_setter()
        return dict.clear(self)

    def copy(self):
        self._check_getter()
        result = UnicodeDict(self)
        self._derived_objs.append(result)
        if self._read_only:
            result._set_read_only()
        return result

    @classmethod
    @tvu.validate_and_unify(keys=tvu.Iterable, value=tvu.Text)
    def fromkeys(cls, keys, value=u''):
        keys = [tvu.Text('keys[%d]' % (i,)).unify_validate(key)
                for i, key in enumerate(keys)]
        return UnicodeDict([(key, value) for key in keys])


# get
# has_key
# items
# iteritems
# iterkeys
# itervalues
# keys
# pop
# popitem
# setdefault
# update
# values
# viewitems
# viewkeys
# viewvalues
# __contains__
# __delitem__
# __eq__
# __ge__
# __getitem__
# __hash__
# __iter__
# __len__
# __ne__
# __repr__
# __setitem__
# __str__
# __cmp__
# __format__
# __gt__
# __le__
# __lt__
