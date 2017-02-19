import json

import tvu

from scrivepy._exceptions import InvalidScriveObject, ReadOnlyScriveObject


class _JSONEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, ScriveObject):
            return obj._to_json_obj()
        return super(_JSONEncoder, self).default(obj)


class ScriveObject(object):

    def __init__(self):
        self._invalid = False
        self._read_only = False
        self._api = None

    def _to_json(self):
        return json.dumps(self, cls=_JSONEncoder)

    def _check_invalid(self):
        if self._invalid:
            raise InvalidScriveObject()

    def _set_invalid(self):
        self._invalid = True

    def _set_read_only(self):
        self._read_only = True

    def _check_getter(self):
        self._check_invalid()

    def _check_setter(self):
        self._check_invalid()
        if self._read_only:
            raise ReadOnlyScriveObject()

    def _set_api(self, api, document):
        self._api = api

    def __setattr__(self, attr, value):
        if attr.startswith('_') or attr in dir(self):
            # private properties and already existing attributes are allowed
            super(ScriveObject, self).__setattr__(attr, value)
        elif self._invalid:
            # invalid objects are still invalid
            raise InvalidScriveObject()
        else:
            # adding new attributes is not allowed
            raise AttributeError(attr)

ID = tvu.tvus.NonEmptyText


def _scrive_method_wrap(fun, pre_fun_name):
    if fun is None:
        return None

    if hasattr(fun, '__scrive_property_wrapped__'):
        return fun

    def wrapper(self, *args):
        getattr(self, pre_fun_name)()
        return fun(self, *args)

    wrapper.__scrive_property_wrapped__ = True

    return wrapper


class scrive_property(property):

    def __init__(self, fget=None, fset=None, fdel=None, doc=None):
        fget = _scrive_method_wrap(fget, '_check_getter')
        fset = _scrive_method_wrap(fset, '_check_setter')
        super(scrive_property, self).__init__(fget, fset, fdel, doc)


class scrive_descriptor(object):

    def __init__(self, tvu_):
        self._name = None
        self._attr_name = None
        self._tvu = tvu_

    def _resolve_name(self, obj_type):
        if self._name is None:
            for attr in dir(obj_type):
                if getattr(obj_type, attr) is self:
                    self._name = attr
                    self._attr_name = '_' + attr
                    break

    def __get__(self, obj, obj_type):
        if obj is None:
            return self
        self._resolve_name(obj_type)
        obj._check_getter()
        return getattr(obj, self._attr_name)

    def __set__(self, obj, value):
        obj._check_setter()
        self._resolve_name(type(obj))
        value = self._tvu(self._name).unify_validate(value)
        setattr(obj, self._attr_name, value)

'''
class Foo(ScriveObject):

The following properties are all equivalent:

(1)
    @property
    def bar(self):
        self._check_getter()
        return self._bar

    @bar.setter
    @tvu(value=tvu.instance(int))
    def bar(self, value):
        self._check_setter()
        self._bar = value

(2)
    @scrive_property
    def baz(self):
        return self._baz

    @baz.setter
    @tvu(value=tvu.instance(int))
    def baz(self, value):
        self._baz = value

(3)

    quux = scrive_descriptor(tvu.instance(int))
'''
