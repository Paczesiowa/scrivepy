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
        result = set.intersection(self, *args)
        _object.ScriveObject.__init__(result)
        return result

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
        result = set.symmetric_difference(self, iterable)
        _object.ScriveObject.__init__(result)
        return result

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
        result = set.difference(self, *args)
        _object.ScriveObject.__init__(result)
        return result

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
        result = set.union(self, *args)
        _object.ScriveObject.__init__(result)
        return result

    def __and__(self, other):
        self._check_getter()
        result = set.__and__(self, other)
        _object.ScriveObject.__init__(result)
        return result

    def __xor__(self, other):
        self._check_getter()
        result = set.__xor__(self, other)
        _object.ScriveObject.__init__(result)
        return result

    def __sub__(self, other):
        self._check_getter()
        result = set.__sub__(self, other)
        _object.ScriveObject.__init__(result)
        return result

    def __or__(self, other):
        self._check_getter()
        result = set.__or__(self, other)
        _object.ScriveObject.__init__(result)
        return result

    def __ge__(self, other):
        self._check_getter()
        return set.__ge__(self, other)

    def __le__(self, other):
        self._check_getter()
        return set.__le__(self, other)

    def __ior__(self, other):
        self._check_setter()
        return set.__ior__(self, other)

    def __iand__(self, other):
        self._check_setter()
        return set.__iand__(self, other)

    def __isub__(self, other):
        self._check_setter()
        return set.__isub__(self, other)

    def __ixor__(self, other):
        self._check_setter()
        return set.__ixor__(self, other)

    def __contains__(self, item):
        self._check_getter()
        return set.__contains__(self, item)

    def __gt__(self, other):
        self._check_getter()
        return set.__gt__(self, other)

    def __lt__(self, other):
        self._check_getter()
        return set.__lt__(self, other)

    def __eq__(self, other):
        self._check_getter()

        if not isinstance(other, ScriveSet):
            return False

        return self._read_only == other._read_only and set.__eq__(self, other)

    def __ne__(self, other):
        self._check_getter()

        if not isinstance(other, ScriveSet):
            return True

        return self._read_only != other._read_only or set.__ne__(self, other)
