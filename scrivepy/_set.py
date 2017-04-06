import itertools

import tvu

from scrivepy._exceptions import InvalidResponse
from scrivepy._object import ScriveObject, scrive_descriptor


class ScriveSet(set, ScriveObject):

    @tvu(iterable=tvu.tvus.iterable())
    def __init__(self, iterable=()):
        set.__init__(self, iterable)
        ScriveObject.__init__(self)
        self.__init_scrive_set__()

    def __init_scrive_set__(self):
        self._derived_objs = []
        self._elem_validator = None

    def add(self, elem):
        self._check_setter()
        if self._elem_validator is not None:
            elem = self._elem_validator('elem').unify_validate(elem)
        return set.add(self, elem)

    def copy(self):
        self._check_getter()
        result = set.copy(self)
        result.__init_scrive_set__()
        ScriveObject.__init__(result)
        self._derived_objs.append(result)
        if self._read_only:
            result._set_read_only()
        return result

    @tvu(iterables=tvu.tvus.iterable(tvu.tvus.iterable()))
    def difference_update(self, *iterables):
        self._check_setter()
        return set.difference_update(self, *iterables)

    @tvu(args=tvu.tvus.iterable(tvu.tvus.iterable()))
    def intersection(self, *args):
        self._check_getter()
        result = set.intersection(self, *args)
        result.__init_scrive_set__()
        ScriveObject.__init__(result)
        self._derived_objs.append(result)
        return result

    @tvu(iterable=tvu.tvus.iterable())
    def isdisjoint(self, iterable):
        self._check_getter()
        return set.isdisjoint(self, iterable)

    @tvu(iterable=tvu.tvus.iterable())
    def issuperset(self, iterable):
        self._check_getter()
        return set.issuperset(self, iterable)

    def remove(self, elem):
        self._check_setter()
        return set.remove(self, elem)

    @tvu(iterable=tvu.tvus.iterable())
    def symmetric_difference(self, iterable):
        self._check_getter()
        result = set.symmetric_difference(self, iterable)
        result.__init_scrive_set__()
        ScriveObject.__init__(result)
        self._derived_objs.append(result)
        return result

    @tvu(iterable=tvu.tvus.iterable())
    def symmetric_difference_update(self, iterable):
        self._check_setter()
        if self._elem_validator is not None:
            validator = self._elem_validator
            iterable = \
                [validator('iterable[%s]' % (i,)).unify_validate(elem)
                 for i, elem in enumerate(iterable)]
        return set.symmetric_difference_update(self, iterable)

    @tvu(iterables=tvu.tvus.iterable(tvu.tvus.iterable()))
    def update(self, *iterables):
        self._check_setter()
        if self._elem_validator is not None:
            validator = self._elem_validator
            iterables = \
                [[validator('iterables[%s][%s]' % (i, j)).unify_validate(elem)
                  for j, elem in enumerate(iterable)]
                 for i, iterable in enumerate(iterables)]
        return set.update(self, *iterables)

    def clear(self):
        self._check_setter()
        return set.clear(self)

    @tvu(args=tvu.tvus.iterable(tvu.tvus.iterable()))
    def difference(self, *args):
        self._check_getter()
        result = set.difference(self, *args)
        result.__init_scrive_set__()
        ScriveObject.__init__(result)
        self._derived_objs.append(result)
        return result

    def discard(self, elem):
        self._check_setter()
        return set.discard(self, elem)

    @tvu(args=tvu.tvus.iterable(tvu.tvus.iterable()))
    def intersection_update(self, *args):
        self._check_setter()
        return set.intersection_update(self, *args)

    @tvu(iterable=tvu.tvus.iterable())
    def issubset(self, iterable):
        self._check_getter()
        return set.issubset(self, iterable)

    def pop(self):
        self._check_setter()
        return set.pop(self)

    @tvu(args=tvu.tvus.iterable(tvu.tvus.iterable()))
    def union(self, *args):
        self._check_getter()
        result = set.union(self, *args)
        result.__init_scrive_set__()
        ScriveObject.__init__(result)
        self._derived_objs.append(result)
        return result

    @tvu(other=tvu.instance(set))
    def __and__(self, other):
        self._check_getter()
        result = set.__and__(self, other)
        result.__init_scrive_set__()
        ScriveObject.__init__(result)
        self._derived_objs.append(result)
        return result

    @tvu(other=tvu.instance(set))
    def __xor__(self, other):
        self._check_getter()
        result = set.__xor__(self, other)
        result.__init_scrive_set__()
        ScriveObject.__init__(result)
        self._derived_objs.append(result)
        return result

    @tvu(other=tvu.instance(set))
    def __sub__(self, other):
        self._check_getter()
        result = set.__sub__(self, other)
        result.__init_scrive_set__()
        ScriveObject.__init__(result)
        self._derived_objs.append(result)
        return result

    @tvu(other=tvu.instance(set))
    def __or__(self, other):
        self._check_getter()
        result = set.__or__(self, other)
        result.__init_scrive_set__()
        ScriveObject.__init__(result)
        self._derived_objs.append(result)
        return result

    @tvu(other=tvu.instance(set))
    def __ge__(self, other):
        self._check_getter()
        return set.__ge__(self, other)

    @tvu(other=tvu.instance(set))
    def __le__(self, other):
        self._check_getter()
        return set.__le__(self, other)

    # this redirects to __or__ anyway, so no need for tvu wrapper
    def __ior__(self, other):
        self._check_setter()
        if self._elem_validator is not None:
            validator = self._elem_validator
            other = \
                [validator('other[%s]' % (i,)).unify_validate(elem)
                 for i, elem in enumerate(other)]
        return set.__ior__(self, other)

    # this redirects to __and__ anyway, so no need for tvu wrapper
    def __iand__(self, other):
        self._check_setter()
        if self._elem_validator is not None:
            validator = self._elem_validator
            other = \
                [validator('other[%s]' % (i,)).unify_validate(elem)
                 for i, elem in enumerate(other)]
        return set.__iand__(self, other)

    # this redirects to __sub__ anyway, so no need for tvu wrapper
    def __isub__(self, other):
        self._check_setter()
        if self._elem_validator is not None:
            validator = self._elem_validator
            other = \
                [validator('other[%s]' % (i,)).unify_validate(elem)
                 for i, elem in enumerate(other)]
        return set.__isub__(self, other)

    # this redirects to __xor__ anyway, so no need for tvu wrapper
    def __ixor__(self, other):
        self._check_setter()
        if self._elem_validator is not None:
            validator = self._elem_validator
            other = \
                [validator('other[%s]' % (i,)).unify_validate(elem)
                 for i, elem in enumerate(other)]
        return set.__ixor__(self, other)

    def __contains__(self, item):
        self._check_getter()
        return set.__contains__(self, item)

    @tvu(other=tvu.instance(set))
    def __gt__(self, other):
        self._check_getter()
        return set.__gt__(self, other)

    @tvu(other=tvu.instance(set))
    def __lt__(self, other):
        self._check_getter()
        return set.__lt__(self, other)

    @tvu(other=tvu.instance(set))
    def __eq__(self, other):
        self._check_getter()

        if not isinstance(other, ScriveSet):
            return False

        return self._read_only == other._read_only and set.__eq__(self, other)

    @tvu(other=tvu.instance(set))
    def __ne__(self, other):
        self._check_getter()

        if not isinstance(other, ScriveSet):
            return True

        return self._read_only != other._read_only or set.__ne__(self, other)

    def __len__(self):
        self._check_getter()
        return set.__len__(self)

    def __iter__(self):
        self._check_getter()
        return set.__iter__(self)

    def _set_read_only(self):
        for item in itertools.chain(
                set.__iter__(self),  # iterate even if self already invalid/ro
                iter(self._derived_objs)):
            if isinstance(item, ScriveObject):
                item._set_read_only()
        super(ScriveSet, self)._set_read_only()

    def _set_invalid(self):
        for item in itertools.chain(
                set.__iter__(self),  # iterate even if self already invalid/ro
                iter(self._derived_objs)):
            if isinstance(item, ScriveObject):
                item._set_invalid()
        super(ScriveSet, self)._set_invalid()

    @tvu(other=tvu.instance(set))
    def __rxor__(self, other):
        self._check_getter()
        # proxy to __xor__, it's ok cause it's symmetric
        result = set.__xor__(self, other)
        result.__init_scrive_set__()
        ScriveObject.__init__(result)
        self._derived_objs.append(result)
        return result

    @tvu(other=tvu.instance(set))
    def __rand__(self, other):
        self._check_getter()
        # proxy to __and__, it's ok cause it's symmetric
        result = set.__and__(self, other)
        result.__init_scrive_set__()
        ScriveObject.__init__(result)
        self._derived_objs.append(result)
        return result

    @tvu(other=tvu.instance(set))
    def __ror__(self, other):
        self._check_getter()
        # proxy to __or__, it's ok cause it's symmetric
        result = set.__or__(self, other)
        result.__init_scrive_set__()
        ScriveObject.__init__(result)
        self._derived_objs.append(result)
        return result

    @tvu(other=tvu.instance(set))
    def __rsub__(self, other):
        self._check_getter()
        # __sub__ isn't symmetric, we have to be creative
        result = ScriveSet(other)
        result -= self
        self._derived_objs.append(result)
        return result

    def get_by_attrs(self, **kwargs):
        '''
        Return first object matching all key=val attributes. or None.
        '''
        self._check_getter()
        for x in self:
            for key, val in kwargs.items():
                try:
                    if getattr(x, key) != val:
                        break
                except AttributeError:
                    break
            else:
                return x
        return None


class scrive_set_descriptor(scrive_descriptor):

    def __init__(self, elem_class):
        self._elem_class = elem_class
        super(scrive_set_descriptor, self).__init__()

    def _init(self, obj, kwargs_dict):
        # set arguments are not allowed as ctor params
        # so just don't pop it from kwargs
        empty_set = ScriveSet()
        empty_set._elem_validator = tvu.instance(self._elem_class)
        setattr(obj, self._attr_name, empty_set)

    def _serialize(self, obj, json_obj):
        json_obj[self._serialized_name] = list(getattr(obj, self._attr_name))

    def _deserialize(self, obj, json_obj):
        child_jsons = self._retrieve_from_json(obj, json_obj)

        try:
            children_list = [self._elem_class._from_json_obj(child_json)
                             for child_json in child_jsons]
        except TypeError:
            err_msg = (u"'" + self._serialized_name + u"' in " +
                       u"server's JSON response for " + type(obj).__name__ +
                       u'is not a list')
            raise InvalidResponse(err_msg)

        children = ScriveSet()
        children._elem_validator = tvu.instance(self._elem_class)
        children.update(children_list)
        setattr(obj, self._attr_name, children)
