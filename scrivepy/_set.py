from scrivepy import _object


class ScriveSet(set, _object.ScriveObject):

    def __init__(self, iterable=()):
        set.__init__(self, iterable)
        _object.ScriveObject.__init__(self)

    def add(self, elem):
        self._check_setter()
        return set.add(self, elem)

    def copy(self):
        self._check_getter()
        result = set.copy(self)
        result._read_only = self._read_only
        result._invalid = False
        return result

    def difference_update(self, *args):
        self._check_setter()
        return set.difference_update(self, *args)

    def intersection(self, *args):
        self._check_getter()
        return set.intersection(self, *args)

    def isdisjoint(self, iterable):
        self._check_getter()
        return set.isdisjoint(self, iterable)

    def issuperset(self, iterable):
        self._check_getter()
        return set.issuperset(self, iterable)

    def remove(self, elem):
        self._check_setter()
        return set.remove(self, elem)

    def symmetric_difference(self, iterable):
        self._check_getter()
        return set.symmetric_difference(self, iterable)

    def symmetric_difference_update(self, iterable):
        self._check_setter()
        return set.symmetric_difference_update(self, iterable)

    def update(self, *args):
        self._check_setter()
        return set.update(self, *args)

    def clear(self):
        self._check_setter()
        return set.clear(self)

    def difference(self, *args):
        self._check_getter()
        return set.difference(self, *args)

    def discard(self, elem):
        self._check_setter()
        return set.discard(self, elem)

    def intersection_update(self, *args):
        self._check_setter()
        return set.intersection_update(self, *args)

    def issubset(self, iterable):
        self._check_getter()
        return set.issubset(self, iterable)

    def pop(self):
        self._check_setter()
        return set.pop(self)

    def union(self, *args):
        self._check_getter()
        return set.union(self, *args)

    def __and__(self, other):
        self._check_getter()
        return set.__and__(self, other)

    def __xor__(self, other):
        self._check_getter()
        return set.__xor__(self, other)

    def __sub__(self, other):
        self._check_getter()
        return set.__sub__(self, other)

    def __or__(self, other):
        self._check_getter()
        return set.__or__(self, other)

    def __ge__(self, other):
        self._check_getter()
        return set.__ge__(self, other)

    def __le__(self, other):
        self._check_getter()
        return set.__le__(self, other)


# 20/57
# __contains__
# __eq__
# __getattribute__
# __iand__
# __isub__
# __ne__
# __repr__
# __str__
# __class__
# __delattr__
# __format__
# __gt__
# __iter__
# __len__
# __new__
# __reduce__
# __setattr__
# __cmp__
# __doc__
# __hash__
# __ior__
# __ixor__
# __lt__
# __reduce_ex__
# __sizeof__
# __subclasshook__
# _set_read_only
# _set_invalid

# HOW DO THESE WORK?!
# __rand__
# __rxor__
# __ror__
# __rsub__
