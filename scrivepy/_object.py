import json
import sys
from types import MethodType

from enum import Enum
import tvu

from scrivepy._exceptions import (InvalidScriveObject,
                                  ReadOnlyScriveObject,
                                  InvalidResponse)
from scrivepy._tvus import IDTVU


class scrive_descriptor(object):

    ###########################################################################
    #                            descriptor setup                             #
    ###########################################################################
    def __init__(self, tvu_=None, default_ctor_value=None,
                 serialized_name=None, read_only=False):
        self._name = None
        self._attr_name = None
        self._tvu = tvu_
        self._default_ctor_value = default_ctor_value
        self._serialized_name = serialized_name
        self._read_only = read_only

    def _resolve_name(self, name):
        '''
        Figure out what name was descriptor instance bound in obj's class.
        Must be called at the begining of obj's __init__(),
        '''
        if self._name is None:
            self._name = name
            self._attr_name = '_' + name
            self._serialized_name = self._serialized_name or name

    ###########################################################################
    #                            descriptor stuff                             #
    ###########################################################################
    def __get__(self, obj, obj_type):
        '''
        `obj.attr` returns `obj._attr`, unless `obj._check_getter()`
        throws exception.
        '''
        if obj is None:
            # attribute read from a class not instance
            return self
        obj._check_getter()
        return getattr(obj, self._attr_name)

    def __set__(self, obj, value):
        '''
        obj.attr = val assigns validated val to obj._attr, unless
        obj._check_setter() throws exception or validation fails.
        If descriptor's tvu is None, or explicitly read_only,
        this is read only attribute (setter throws AttributeError)
        '''
        if self._tvu is None or self._read_only:
            # read only attribute
            raise AttributeError()
        obj._check_setter()
        value = self._tvu(self._name).unify_validate(value)
        setattr(obj, self._attr_name, value)

    ###########################################################################
    #                        descriptor behaviour stuff                       #
    ###########################################################################
    def _init(self, obj, kwargs_dict):
        '''
        Initialize attribute inside obj's __init__() using its **kwargs

        _init() methods of all descriptors are used to construct obj instance
        without providing __init__() method for it.
        '''
        try:
            val = kwargs_dict.pop(self._name)
        except KeyError:
            # value was not provided to obj's __init__()
            if self._default_ctor_value is not None:
                # but it's optional, with a default value
                val = self._default_ctor_value
            else:
                raise TypeError('__init__() requires ' +
                                self._name + ' keyword argument')
        # validate argument
        if self._tvu is not None:
            val = self._tvu(self._name).unify_validate(val)

        # finally set it inside object
        setattr(obj, self._attr_name, val)

    def _serialize(self, obj, json_obj):
        '''
        Serialize obj's attribute  to json_obj being constructed.
        '''
        val = getattr(obj, self._attr_name)
        json_obj[self._serialized_name] = val

    def _retrieve_from_json(self, obj, json_obj):
        '''
        Get serialized value from json obj for this attribute.

        Useful when overriding _deserialize() because it throws nice exception.
        '''
        try:
            return json_obj[self._serialized_name]
        except KeyError:
            err_msg = (u"'" + self._serialized_name + u"' missing in " +
                       u"server's JSON response for " + type(obj).__name__)
            raise InvalidResponse(err_msg)

    def _deserialize(self, obj, json_obj):
        '''
        Perform deserialization of obj's attribute from JSON object to bare
        instance of object.
        '''
        val = self._retrieve_from_json(obj, json_obj)

        # validate value
        if self._tvu is not None:
            try:
                val = self._tvu(self._name).unify_validate(val)
            except (ValueError, TypeError) as e:
                raise InvalidResponse(e), None, sys.exc_info()[2]

        # finally set it inside object
        setattr(obj, self._attr_name, val)

    ###########################################################################
    #                      descriptor behaviour overriding                    #
    ###########################################################################
    def __call__(self, f):
        fname = f.__name__
        if fname not in ['_deserialize', '_serialize', '_init']:
            raise TypeError('Unknown descriptor method: ' + fname)
        setattr(self, fname, MethodType(f, self))


class ScriveObject(object):

    ###########################################################################
    #                                 setup                                   #
    ###########################################################################
    def _bare_init(self):
        '''
        Initialize object without setting all attributes.
        '''
        # setup required flags for every object
        self._invalid = False
        self._read_only = False
        self._api = None

        cls = type(self)
        if '_scrive_descriptors' not in cls.__dict__:
            # resolve descriptor names and cache descriptors
            cls._scrive_descriptors = []
            for attr_name in dir(cls):
                attr = getattr(cls, attr_name)
                if isinstance(attr, scrive_descriptor):
                    attr._resolve_name(attr_name)
                    cls._scrive_descriptors.append(attr)

    def __init__(self, *args, **kwargs):
        self._bare_init()
        if args:
            raise TypeError('__init__() only supports keyword arguments')

        # ask descriptors to initialize their fields using kwargs
        for descr in self._scrive_descriptors:
            descr._init(self, kwargs)

        # look for leftover arguments
        try:
            (attr, _) = kwargs.popitem()
            raise TypeError("__init__() got an unexpected keyword argument '" +
                            attr + "'")
        except KeyError:
            pass

    ###########################################################################
    #                      read only/invalid flags stuff                      #
    ###########################################################################
    def _set_invalid(self):
        '''
        Invalidate this object (even getters will stop working)
        and all its subobjects.
        '''
        for descr in self._scrive_descriptors:
            value = getattr(self, descr._attr_name)
            if isinstance(value, ScriveObject):
                value._set_invalid()
        self._invalid = True

    def _set_read_only(self):
        '''
        Mark this object as read only (setters will stop working), including
        all its subobjects.
        '''
        for descr in self._scrive_descriptors:
            value = getattr(self, descr._attr_name)
            if isinstance(value, ScriveObject):
                value._set_read_only()
        self._read_only = True

    def _check_getter(self):
        if self._invalid:
            raise InvalidScriveObject()

    def _check_setter(self):
        if self._invalid:
            raise InvalidScriveObject()
        if self._read_only:
            raise ReadOnlyScriveObject()

    def _set_api(self, api, document):
        '''
        Sets api instance in object for use in methods using remote server.
        Subclasses should override this when they need to use document as well.
        '''
        self._api = api

    ###########################################################################
    #                             serialization                               #
    ###########################################################################
    def _to_json(self):
        '''
        Serializes object to JSON string.
        Subclasses shouldn't override, but implement/override _to_json_obj().
        '''
        class _JSONEncoder(json.JSONEncoder):
            '''
            JSONEncoder that tries to serialize objects using their
            _to_json_obj() method before falling back to generic way.
            '''
            def default(self, obj):
                try:
                    return obj._to_json_obj()
                except TypeError:
                    return super(_JSONEncoder, self).default(obj)

        return json.dumps(self, cls=_JSONEncoder)

    def _to_json_obj(self):
        '''
        Serializes object to JSON dictionary object, by delegating
        serialization to all attribute descriptors.
        '''
        result = {}
        for descr in self._scrive_descriptors:
            descr._serialize(self, result)
        return result

    @classmethod
    def _from_json_obj(cls, json, class_override=None):
        '''
        Deserialize and construct an object from JSON object, by delegating
        new object initialization to attribute descriptors _deserialize()
        method.
        '''
        cls = class_override or cls
        obj = cls.__new__(cls)
        obj._bare_init()

        for descr in cls._scrive_descriptors:
            descr._deserialize(obj, json)

        return obj

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


class ScriveEnumMixin(unicode):

    @classmethod
    def _deserialize(cls, value):
        try:
            return cls[cls._deserialization_mapping[value]]
        except (KeyError, TypeError):
            raise ValueError(value)

    def _serialize(self):
        return self._serialization_mapping[self.name]


def ScriveEnum(name, values):
    if isinstance(values, str):
        names = values.split(' ')
        serialization_mapping = {name: unicode(name) for name in names}
        deserialization_mapping = {unicode(name): name for name in names}
    else:
        names = values.keys()
        serialization_mapping = values
        deserialization_mapping = {value: name
                                   for name, value in values.items()}
    result = Enum(name, names={name: name for name in names},
                  type=ScriveEnumMixin)
    result._serialization_mapping = serialization_mapping
    result._deserialization_mapping = deserialization_mapping
    return result


class enum_descriptor(scrive_descriptor):

    def __init__(self, enum_class, *args, **kwargs):
        self._enum_class = enum_class
        kwargs['tvu_'] = tvu.instance(enum_class, enum=True)
        return super(enum_descriptor, self).__init__(*args, **kwargs)

    def _serialize(self, obj, json_obj):
        val = getattr(obj, self._attr_name)
        json_obj[self._serialized_name] = val._serialize()

    def _deserialize(self, obj, json_obj):
        val = self._retrieve_from_json(obj, json_obj)
        try:
            setattr(obj, self._attr_name,
                    self._enum_class._deserialize(val))
        except ValueError:
            err_msg = u'%s must be %s, not %s' % (self._name,
                                                  self._enum_class.__name__,
                                                  repr(val))
            raise InvalidResponse(err_msg)


class remote_descriptor(scrive_descriptor):

    def __init__(self, *args, **kwargs):
        super(remote_descriptor, self).__init__(*args, read_only=True,
                                                **kwargs)

    def _init(self, obj, kwargs_dict):
        setattr(obj, self._attr_name, self._default_ctor_value)

    def _serialize(self, obj, json_obj):
        pass


class id_descriptor(remote_descriptor):

    def __init__(self, nullable_=False, preserve=False):
        tvu_ = tvu.nullable(IDTVU) if nullable_ else IDTVU
        super(id_descriptor, self).__init__(tvu_)
        self._preserve = preserve

    def _serialize(self, obj, json_obj):
        if self._preserve:
            value = getattr(obj, self._attr_name)
            if value is not None:
                json_obj[self._serialized_name] = value
