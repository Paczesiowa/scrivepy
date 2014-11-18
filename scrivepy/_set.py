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
        return result

    def difference_update(self, iterable=()):
        self._check_setter()
        return set.difference_update(self, iterable)

# x.add                          x.copy                         x.difference_update            x.intersection                 x.isdisjoint                   x.issuperset                   x.remove                       x.symmetric_difference_update  x.update
# x.clear                        x.difference                   x.discard                      x.intersection_update          x.issubset                     x.pop                          x.symmetric_difference         x.union


# x.__and__           x.__contains__      x.__eq__            x.__getattribute__  x.__iand__          x.__isub__          x.__le__            x.__ne__            x.__rand__          x.__repr__          x.__rxor__          x.__str__           x.__xor__
# x.__class__         x.__delattr__       x.__format__        x.__gt__            x.__init__          x.__iter__          x.__len__           x.__new__           x.__reduce__        x.__ror__           x.__setattr__       x.__sub__
# x.__cmp__           x.__doc__           x.__ge__            x.__hash__          x.__ior__           x.__ixor__          x.__lt__            x.__or__            x.__reduce_ex__     x.__rsub__          x.__sizeof__        x.__subclasshook__
 
# s = ScriveSet()
# s._read_only = True
# print s, type(s), s._read_only
# s2 = s.copy()
# print s2, type(s2), s2._read_only


# x = ScriveSet([1,2,3])
# y = ScriveSet([2,3])
# print x.difference_update()
# print x, y

