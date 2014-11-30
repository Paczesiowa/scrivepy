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


# 7/57
# remove
# symmetric_difference_update
# update
# clear
# difference
# discard
# intersection_update
# issubset
# pop
# symmetric_difference
# union
# __and__
# __contains__
# __eq__
# __getattribute__
# __iand__
# __isub__
# __le__
# __ne__
# __rand__
# __repr__
# __rxor__
# __str__
# __xor__
# __class__
# __delattr__
# __format__
# __gt__
# __iter__
# __len__
# __new__
# __reduce__
# __ror__
# __setattr__
# __sub__
# __cmp__
# __doc__
# __ge__
# __hash__
# __ior__
# __ixor__
# __lt__
# __or__
# __reduce_ex__
# __rsub__
# __sizeof__
# __subclasshook__
# _set_read_only
# _set_invalid
