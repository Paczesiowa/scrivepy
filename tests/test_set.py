import tvu
from scrivepy import (
    InvalidScriveObject as INV,
    ReadOnlyScriveObject as RO,
    _object,
    _set
)
from tests import utils


S = _set.ScriveSet
O = _object.ScriveObject


class ScriveSetTest(utils.TestCase):

    def setUp(self):
        pass

    def assertProperScriveSet(self, s):
        self.assertTrue(isinstance(s, S))
        self.assertTrue(hasattr(s, '_invalid'))
        self.assertTrue(hasattr(s, '_read_only'))

    def test_init(self):
        s = S()
        self.assertTrue(isinstance(s, set))
        self.assertTrue(isinstance(s, O))
        self.assertProperScriveSet(s)

        self.assertEqual(0, len(s))

        self.assertFalse(s._read_only)
        self.assertFalse(s._invalid)

        s._set_read_only()
        self.assertTrue(s._read_only)
        self.assertFalse(s._invalid)

        s._set_invalid()
        self.assertTrue(s._read_only)
        self.assertTrue(s._invalid)

        s = S([1, 2])
        self.assertEqual(2, len(s))
        self.assertTrue(1 in s)
        self.assertTrue(2 in s)

        with self.assertRaises(TypeError,
                               u'iterable must be iterable, not None'):
            S(None)

    def test_add(self):
        s = S([1])
        self.assertEqual(1, len(s))
        self.assertTrue(1 in s)
        self.assertFalse(2 in s)
        self.assertFalse(3 in s)

        s.add(2)
        self.assertEqual(2, len(s))
        self.assertTrue(1 in s)
        self.assertTrue(2 in s)
        self.assertFalse(3 in s)

        s._set_read_only()
        with self.assertRaises(RO):
            s.add(3)
        s._set_invalid()
        with self.assertRaises(INV):
            s.add(3)

        s = S()
        s._elem_validator = tvu.instance(int)
        err_msg = u'elem must be int, not []'
        with self.assertRaises(TypeError, err_msg):
            s.add([])

    def test_copy(self):
        o1 = _object.ScriveObject()
        o2 = _object.ScriveObject()
        o3 = _object.ScriveObject()

        s1 = S([o1])
        self.assertEqual(1, len(s1))
        self.assertTrue(o1 in s1)
        self.assertFalse(o2 in s1)
        self.assertFalse(o3 in s1)

        s2 = s1.copy()
        self.assertProperScriveSet(s2)

        self.assertTrue(o1 in s2)
        self.assertFalse(o2 in s2)
        self.assertFalse(o3 in s2)

        s1.add(o2)

        self.assertTrue(o1 in s1)
        self.assertTrue(o2 in s1)
        self.assertFalse(o3 in s1)

        self.assertTrue(o1 in s2)
        self.assertFalse(o2 in s2)
        self.assertFalse(o3 in s2)

        s2.add(o3)

        self.assertTrue(o1 in s1)
        self.assertTrue(o2 in s1)
        self.assertFalse(o3 in s1)

        self.assertTrue(o1 in s2)
        self.assertFalse(o2 in s2)
        self.assertTrue(o3 in s2)

        s1._set_read_only()
        self.assertTrue(s1._read_only)
        self.assertTrue(s2._read_only)

        s2._set_invalid()
        self.assertFalse(s1._invalid)
        self.assertTrue(s2._invalid)

        s = S()
        s._set_read_only()
        s.copy()
        s._set_invalid()
        with self.assertRaises(INV):
            s.copy()

        s1 = S()
        s2 = s1.copy()
        s1._set_read_only()
        self.assertTrue(s2._read_only)
        s1._set_invalid()
        self.assertTrue(s2._invalid)

    def test_difference_update(self):
        s = S([1, 2, 3])
        s.difference_update([2, 4], [5])
        self.assertEqual(2, len(s))
        self.assertTrue(1 in s)
        self.assertFalse(2 in s)
        self.assertTrue(3 in s)
        self.assertFalse(4 in s)
        self.assertFalse(5 in s)

        s._set_read_only()
        with self.assertRaises(RO):
            s.difference_update([])
        s._set_invalid()
        with self.assertRaises(INV):
            s.difference_update([])

        with self.assertRaises(TypeError,
                               u'iterables[1] must be iterable, not None'):
            s.difference_update([], None)

    def test_intersection(self):
        s1 = S([1, 2, 3])
        s2 = S([1, 2])
        s3 = S([1])
        s = s1.intersection(s2, s3)
        self.assertProperScriveSet(s)
        self.assertEqual(1, len(s))
        self.assertTrue(1 in s)
        self.assertFalse(2 in s)
        self.assertFalse(3 in s)

        s = S()
        s._set_read_only()
        s.intersection()
        s._set_invalid()
        with self.assertRaises(INV):
            s.intersection()

        s1 = S()
        s2 = s1.intersection()
        s1._set_read_only()
        self.assertTrue(s2._read_only)
        s1._set_invalid()
        self.assertTrue(s2._invalid)

        s = S()
        with self.assertRaises(TypeError,
                               u'args[3] must be iterable, not 2'):
            s.intersection([], set(), S(), 2)

    def test_isdisjoint(self):
        s = S([1, 2, 3])
        self.assertTrue(s.isdisjoint([4, 5]))
        self.assertFalse(s.isdisjoint([1]))
        self.assertFalse(s.isdisjoint([2, 4, 5]))

        s = S()
        s._set_read_only()
        s.isdisjoint([])
        s._set_invalid()
        with self.assertRaises(INV):
            s.isdisjoint([])

        s = S()
        with self.assertRaises(TypeError,
                               u'iterable must be iterable, not 7'):
            s.isdisjoint(7)

    def test_issuperset(self):
        s = S([1, 2, 3])
        self.assertTrue(s.issuperset([1, 2, 3]))
        self.assertTrue(s.issuperset([2]))
        self.assertFalse(s.issuperset([4]))
        self.assertFalse(s.issuperset([1, 2, 3, 4]))

        s = S()
        s._set_read_only()
        s.issuperset([])
        s._set_invalid()
        with self.assertRaises(INV):
            s.issuperset([])

        s = S()
        with self.assertRaises(TypeError,
                               u'iterable must be iterable, not 1.5'):
            s.issuperset(1.5)

    def test_remove(self):
        s = S([1, 2])
        s.remove(1)
        self.assertEqual(1, len(s))
        self.assertTrue(2 in s)
        self.assertFalse(1 in s)
        s.remove(2)
        self.assertEqual(0, len(s))
        self.assertFalse(1 in s)
        self.assertFalse(2 in s)
        with self.assertRaises(KeyError):
            s.remove(0)

        s = S([1])
        s._set_read_only()
        with self.assertRaises(RO):
            s.remove(1)
        s._set_invalid()
        with self.assertRaises(INV):
            s.remove(1)

    def test_symmetric_difference(self):
        s1 = S([1, 2, 3])
        s = s1.symmetric_difference([2, 3, 4])
        self.assertProperScriveSet(s)
        self.assertEqual(2, len(s))
        self.assertTrue(1 in s)
        self.assertTrue(4 in s)

        s = S()
        s._set_read_only()
        s.symmetric_difference([])
        s._set_invalid()
        with self.assertRaises(INV):
            s.symmetric_difference([])

        s1 = S()
        s2 = s1.symmetric_difference([])
        s1._set_read_only()
        self.assertTrue(s2._read_only)
        s1._set_invalid()
        self.assertTrue(s2._invalid)

        s = S()
        with self.assertRaises(TypeError,
                               u'iterable must be iterable, not 7'):
            s.symmetric_difference(7)

    def test_symmetric_difference_update(self):
        s = S([1, 2, 3])
        s.symmetric_difference_update([2, 4])
        self.assertEqual(3, len(s))
        self.assertTrue(1 in s)
        self.assertTrue(3 in s)
        self.assertTrue(4 in s)

        s._set_read_only()
        with self.assertRaises(RO):
            s.symmetric_difference_update([])
        s._set_invalid()
        with self.assertRaises(INV):
            s.symmetric_difference_update([])

        s = S()
        s._elem_validator = tvu.instance(int)
        err_msg = u'iterable[2] must be int, not {}'
        with self.assertRaises(TypeError, err_msg):
            s.symmetric_difference_update([2, 3, {}])

        s = S()
        with self.assertRaises(TypeError,
                               u'iterable must be iterable, not None'):
            s.symmetric_difference_update(None)

    def test_update(self):
        s = S([1, 2, 3])
        s.update([2, 4], [1, 5], [6])
        self.assertEqual(6, len(s))
        self.assertTrue(1 in s)
        self.assertTrue(2 in s)
        self.assertTrue(3 in s)
        self.assertTrue(4 in s)
        self.assertTrue(5 in s)
        self.assertTrue(6 in s)

        s._set_read_only()
        with self.assertRaises(RO):
            s.update()
        s._set_invalid()
        with self.assertRaises(INV):
            s.update()

        s = S()
        s._elem_validator = tvu.instance(int)
        err_msg = u'iterables[1][2] must be int, not {}'
        with self.assertRaises(TypeError, err_msg):
            s.update([1], [2, 3, {}])

        with self.assertRaises(TypeError,
                               u'iterables[3] must be iterable, not 2'):
            s.update([], set(), S(), 2)

    def test_clear(self):
        s = S([1, 2])
        s.clear()
        self.assertEqual(0, len(s))

        s._set_read_only()
        with self.assertRaises(RO):
            s.clear()
        s._set_invalid()
        with self.assertRaises(INV):
            s.clear()

    def test_difference(self):
        s = S([1, 2, 3, 4])
        s2 = s.difference([1], [2, 3], [5])
        self.assertProperScriveSet(s2)
        self.assertEqual(1, len(s2))
        self.assertTrue(4 in s2)

        s._set_read_only()
        s.difference()
        s._set_invalid()
        with self.assertRaises(INV):
            s.difference()

        s1 = S()
        s2 = s1.difference()
        s1._set_read_only()
        self.assertTrue(s2._read_only)
        s1._set_invalid()
        self.assertTrue(s2._invalid)

        s = S()
        with self.assertRaises(TypeError,
                               u'args[3] must be iterable, not 2'):
            s.difference([], set(), S(), 2)

    def test_discard(self):
        s = S([1, 2])
        s.discard(3)
        self.assertEqual(2, len(s))
        s.discard(2)
        self.assertEqual(1, len(s))
        self.assertTrue(1 in s)

        s._set_read_only()
        with self.assertRaises(RO):
            s.discard(1)
        s._set_invalid()
        with self.assertRaises(INV):
            s.discard(1)

    def test_intersection_update(self):
        s = S([1, 2, 3])
        s.intersection_update([2, 4], [2, 5])
        self.assertEqual(1, len(s))
        self.assertTrue(2 in s)

        s._set_read_only()
        with self.assertRaises(RO):
            s.intersection_update([])
        s._set_invalid()
        with self.assertRaises(INV):
            s.intersection_update([])

        s = S()
        with self.assertRaises(TypeError,
                               u'args[3] must be iterable, not 2'):
            s.intersection_update([], set(), S(), 2)

    def test_issubset(self):
        s = S([2])
        self.assertTrue(s.issubset([1, 2, 3]))
        self.assertTrue(s.issubset([2]))
        self.assertFalse(s.issubset([4]))
        self.assertFalse(s.issubset([1, 3, 4]))

        s = S()
        s._set_read_only()
        s.issubset([])
        s._set_invalid()
        with self.assertRaises(INV):
            s.issubset([])

        s = S()
        with self.assertRaises(TypeError,
                               u'iterable must be iterable, not 1.5'):
            s.issubset(1.5)

    def test_pop(self):
        s = S([1, 2])
        self.assertTrue(s.pop() in [1, 2])
        self.assertEqual(1, len(s))
        self.assertTrue(s.pop() in [1, 2])
        self.assertEqual(0, len(s))
        with self.assertRaises(KeyError):
            s.pop()

        s = S([1])
        s._set_read_only()
        with self.assertRaises(RO):
            s.pop()
        s._set_invalid()
        with self.assertRaises(INV):
            s.pop()

    def test_union(self):
        s1 = S([1, 2, 3])
        s2 = S([1, 2, 4])
        s3 = S([5])
        s = s1.union(s2, s3)
        self.assertProperScriveSet(s)
        self.assertEqual(5, len(s))
        self.assertTrue(1 in s)
        self.assertTrue(2 in s)
        self.assertTrue(3 in s)
        self.assertTrue(4 in s)
        self.assertTrue(5 in s)

        s = S()
        s._set_read_only()
        s.union()
        s._set_invalid()
        with self.assertRaises(INV):
            s.union()

        s1 = S()
        s2 = s1.union()
        s1._set_read_only()
        self.assertTrue(s2._read_only)
        s1._set_invalid()
        self.assertTrue(s2._invalid)

        s = S()
        with self.assertRaises(TypeError,
                               u'args[3] must be iterable, not 2'):
            s.union([], set(), S(), 2)

    def test___and__(self):
        s1 = S([1, 2, 3])
        s2 = S([1, 2])
        s3 = S([1])
        s = s1 & (s2 & s3)
        self.assertProperScriveSet(s)
        self.assertEqual(1, len(s))
        self.assertTrue(1 in s)
        self.assertFalse(2 in s)
        self.assertFalse(3 in s)

        s = S()
        s._set_read_only()
        s & S()
        s._set_invalid()
        with self.assertRaises(INV):
            s & S()

        s1 = S()
        s2 = s1 & S()
        s1._set_read_only()
        self.assertTrue(s2._read_only)
        s1._set_invalid()
        self.assertTrue(s2._invalid)

        s = S()
        with self.assertRaises(TypeError,
                               u'other must be set, not 2'):
            s & 2

    def test___xor__(self):
        s1 = S([1, 2, 3])
        s = s1 ^ S([2, 3, 4])
        self.assertProperScriveSet(s)
        self.assertEqual(2, len(s))
        self.assertTrue(1 in s)
        self.assertTrue(4 in s)

        s = S()
        s._set_read_only()
        s ^ S()
        s._set_invalid()
        with self.assertRaises(INV):
            s ^ S()

        s1 = S()
        s2 = s1 ^ S()
        s1._set_read_only()
        self.assertTrue(s2._read_only)
        s1._set_invalid()
        self.assertTrue(s2._invalid)

        s = S()
        with self.assertRaises(TypeError,
                               u'other must be set, not 2'):
            s ^ 2

    def test___sub__(self):
        s = S([1, 2, 3, 4])
        s2 = s - S([2, 3])
        self.assertProperScriveSet(s2)
        self.assertEqual(2, len(s2))
        self.assertTrue(1 in s2)
        self.assertTrue(4 in s2)

        s._set_read_only()
        s - S()
        s._set_invalid()
        with self.assertRaises(INV):
            s - S()

        s1 = S()
        s2 = s1 - S()
        s1._set_read_only()
        self.assertTrue(s2._read_only)
        s1._set_invalid()
        self.assertTrue(s2._invalid)

        s = S()
        with self.assertRaises(TypeError,
                               u'other must be set, not 2'):
            s - 2

    def test___or__(self):
        s1 = S([1, 2, 3])
        s2 = S([1, 2, 4])
        s3 = S([5])
        s = s1 | (s2 | s3)
        self.assertProperScriveSet(s)
        self.assertEqual(5, len(s))
        self.assertTrue(1 in s)
        self.assertTrue(2 in s)
        self.assertTrue(3 in s)
        self.assertTrue(4 in s)
        self.assertTrue(5 in s)

        s = S()
        s._set_read_only()
        s | S()
        s._set_invalid()
        with self.assertRaises(INV):
            s | S()

        s1 = S()
        s2 = s1 | S()
        s1._set_read_only()
        self.assertTrue(s2._read_only)
        s1._set_invalid()
        self.assertTrue(s2._invalid)

        s = S()
        with self.assertRaises(TypeError,
                               u'other must be set, not 2'):
            s | 2

    def test___ge__(self):
        s = S([1, 2, 3])
        self.assertTrue(s >= S([1, 2, 3]))
        self.assertTrue(s >= S([2]))
        self.assertFalse(s >= S([4]))
        self.assertFalse(s >= S([1, 2, 3, 4]))

        s = S()
        s._set_read_only()
        s >= S()
        s._set_invalid()
        with self.assertRaises(INV):
            s >= S()

        s = S()
        with self.assertRaises(TypeError,
                               u'other must be set, not 2'):
            s >= 2

    def test___le__(self):
        s = S([2])
        self.assertTrue(s <= S([1, 2, 3]))
        self.assertTrue(s <= S([2]))
        self.assertFalse(s <= S([4]))
        self.assertFalse(s <= S([1, 3, 4]))

        s = S()
        s._set_read_only()
        s <= S()
        s._set_invalid()
        with self.assertRaises(INV):
            s <= S()

        s = S()
        with self.assertRaises(TypeError,
                               u'other must be set, not 2'):
            s <= 2

    def test___ior__(self):
        s = S([1, 2, 3])
        s |= S([2, 4])
        s |= S([1, 5])
        s |= S([6])
        self.assertEqual(6, len(s))
        self.assertTrue(1 in s)
        self.assertTrue(2 in s)
        self.assertTrue(3 in s)
        self.assertTrue(4 in s)
        self.assertTrue(5 in s)
        self.assertTrue(6 in s)

        s._set_read_only()
        with self.assertRaises(RO):
            s |= S()
        s._set_invalid()
        with self.assertRaises(INV):
            s |= S()

        s = S()
        s._elem_validator = tvu.instance(int)
        err_msg = u'other\[\d\] must be int, not None'
        with self.assertRaises(TypeError, err_msg, regex=True):
            s |= S([2, 3, None])

        s = S()
        with self.assertRaises(TypeError,
                               u'other must be set, not None'):
            s |= None

    def test___iand__(self):
        s = S([1, 2, 3])
        s &= S([2, 4])
        s &= S([2, 5])
        self.assertEqual(1, len(s))
        self.assertTrue(2 in s)

        s._set_read_only()
        with self.assertRaises(RO):
            s &= S()
        s._set_invalid()
        with self.assertRaises(INV):
            s &= S()

        s = S()
        s._elem_validator = tvu.instance(int)
        err_msg = u'other\[\d\] must be int, not None'
        with self.assertRaises(TypeError, err_msg, regex=True):
            s &= S([2, 3, None])

        s = S()
        with self.assertRaises(TypeError,
                               u'other must be set, not None'):
            s &= None

    def test___isub__(self):
        s = S([1, 2, 3])
        s -= S([2, 4])
        s -= S([5])
        self.assertEqual(2, len(s))
        self.assertTrue(1 in s)
        self.assertFalse(2 in s)
        self.assertTrue(3 in s)
        self.assertFalse(4 in s)
        self.assertFalse(5 in s)

        s._set_read_only()
        with self.assertRaises(RO):
            s -= S()
        s._set_invalid()
        with self.assertRaises(INV):
            s -= S()

        s = S()
        s._elem_validator = tvu.instance(int)
        err_msg = u'other\[\d\] must be int, not None'
        with self.assertRaises(TypeError, err_msg, regex=True):
            s -= S([2, 3, None])

        s = S()
        with self.assertRaises(TypeError,
                               u'other must be set, not None'):
            s -= None

    def test___ixor__(self):
        s = S([1, 2, 3])
        s ^= S([2, 4])
        self.assertEqual(3, len(s))
        self.assertTrue(1 in s)
        self.assertTrue(3 in s)
        self.assertTrue(4 in s)

        s._set_read_only()
        with self.assertRaises(RO):
            s ^= S()
        s._set_invalid()
        with self.assertRaises(INV):
            s ^= S()

        s = S()
        s._elem_validator = tvu.instance(int)
        err_msg = u'other\[\d\] must be int, not None'
        with self.assertRaises(TypeError, err_msg, regex=True):
            s ^= S([2, 3, None])

        s = S()
        with self.assertRaises(TypeError,
                               u'other must be set, not None'):
            s ^= None

    def test___contains__(self):
        s = S([1, 2])
        self.assertTrue(1 in s)
        self.assertTrue(2 in s)
        self.assertFalse(3 in s)
        self.assertFalse(4 in s)

        s._set_read_only()
        self.assertTrue(1 in s)
        self.assertTrue(2 in s)
        self.assertFalse(3 in s)
        self.assertFalse(4 in s)
        s._set_invalid()
        with self.assertRaises(INV):
            1 in s

    def test___gt__(self):
        s = S([1, 2])
        self.assertTrue(s > S())
        self.assertTrue(s > S([1]))
        self.assertFalse(s > S([1, 2]))
        self.assertTrue(s > S([2]))
        self.assertFalse(s > S([4]))
        self.assertFalse(s > S([1, 2, 3, 4]))

        s = S()
        s._set_read_only()
        s > S()
        s._set_invalid()
        with self.assertRaises(INV):
            s > S()

        s = S()
        with self.assertRaises(TypeError,
                               u'other must be set, not 1.5'):
            s > 1.5

    def test___lt__(self):
        s = S([2])
        self.assertTrue(s < S([1, 2]))
        self.assertFalse(s < S([2]))
        self.assertFalse(s < S([4]))
        self.assertFalse(s < S([1, 3, 4]))

        s = S()
        s._set_read_only()
        s < S()
        s._set_invalid()
        with self.assertRaises(INV):
            s < S()

        s = S()
        with self.assertRaises(TypeError,
                               u'other must be set, not 1.5'):
            s < 1.5

    def test___eq__(self):
        self.assertFalse(S() == set())

        self.assertTrue(S([1, 2]) == S([1, 2]))
        self.assertFalse(S([1]) == S([1, 2]))
        self.assertFalse(S([1, 2]) == S([2]))

        s1 = S([1, 2])
        s1._set_read_only()
        s2 = S([1, 2])
        self.assertFalse(s1 == s2)
        s2._set_read_only()
        self.assertTrue(s1 == s2)

        s = S()
        s._set_invalid()
        with self.assertRaises(INV):
            s == S()

        s = S()
        with self.assertRaises(TypeError,
                               u'other must be set, not 1.5'):
            s == 1.5

    def test___ne__(self):
        self.assertTrue(S() != set())

        self.assertFalse(S([1, 2]) != S([1, 2]))
        self.assertTrue(S([1]) != S([1, 2]))
        self.assertTrue(S([1, 2]) != S([2]))

        s1 = S([1, 2])
        s1._set_read_only()
        s2 = S([1, 2])
        self.assertTrue(s1 != s2)
        s2._set_read_only()
        self.assertFalse(s1 != s2)

        s = S()
        s._set_invalid()
        with self.assertRaises(INV):
            s != S()

        s = S()
        with self.assertRaises(TypeError,
                               u'other must be set, not 1.5'):
            s != 1.5

    def test___len__(self):
        self.assertEqual(3, len(S([1, 2, 3])))
        self.assertEqual(2, len(S([1, 2])))
        self.assertEqual(1, len(S([1])))
        self.assertEqual(0, len(S()))

        s = S([1, 2])
        s._set_read_only()
        self.assertEqual(2, len(s))
        s._set_invalid()
        with self.assertRaises(INV):
            len(s)

    def test___iter__(self):
        self.assertEqual(set(iter(S([1, 2, 3]))), set([1, 2, 3]))
        iterator = iter(S([1, 2, 3]))
        self.assertTrue(iterator.next() in [1, 2, 3])
        self.assertTrue(iterator.next() in [1, 2, 3])
        self.assertTrue(iterator.next() in [1, 2, 3])
        with self.assertRaises(StopIteration):
            iterator.next()

        s = S([1, 2])
        s._set_read_only()
        self.assertEqual(set(iter(s)), set([1, 2]))
        s._set_invalid()
        with self.assertRaises(INV):
            iter(s)

    def test__set_read_only(self):
        o = O()
        s = S([o, 3])
        self.assertFalse(s._read_only)
        self.assertFalse(o._read_only)
        s._set_read_only()
        self.assertTrue(s._read_only)
        self.assertTrue(o._read_only)

        o2 = O()
        s2 = S([o, 3])
        s2.add(o2)
        s2._set_invalid()
        s2._set_read_only()
        self.assertTrue(s2._read_only)
        self.assertTrue(o2._read_only)

    def test__set_invalid(self):
        o = O()
        s = S([o, 3])
        self.assertFalse(s._invalid)
        self.assertFalse(o._invalid)
        s._set_invalid()
        self.assertTrue(s._invalid)
        self.assertTrue(o._invalid)

        o2 = O()
        s2 = S([o2, 3])
        s2._set_read_only()
        s2._set_invalid()
        self.assertTrue(s2._invalid)
        self.assertTrue(o2._invalid)

    def test___rxor__(self):
        s1 = set([1, 2, 3])
        s = s1 ^ S([2, 3, 4])
        self.assertProperScriveSet(s)
        self.assertEqual(2, len(s))
        self.assertTrue(1 in s)
        self.assertTrue(4 in s)

        s = S()
        s._set_read_only()
        set() ^ s
        s._set_invalid()
        with self.assertRaises(INV):
            set() ^ s

        s1 = S()
        s2 = set() ^ s1
        s1._set_read_only()
        self.assertTrue(s2._read_only)
        s1._set_invalid()
        self.assertTrue(s2._invalid)

        s = S()
        with self.assertRaises(TypeError,
                               u'other must be set, not 1.5'):
            1.5 ^ s

    def test___rand__(self):
        s1 = S([1])
        s2 = set([1, 2]) & s1
        self.assertProperScriveSet(s2)
        self.assertEqual(1, len(s2))
        self.assertTrue(1 in s2)
        self.assertFalse(2 in s2)
        self.assertFalse(3 in s2)

        s = S()
        s._set_read_only()
        set() & s
        s._set_invalid()
        with self.assertRaises(INV):
            set() & s

        s1 = S()
        s2 = set() & s1
        s1._set_read_only()
        self.assertTrue(s2._read_only)
        s1._set_invalid()
        self.assertTrue(s2._invalid)

        s = S()
        with self.assertRaises(TypeError,
                               u'other must be set, not 1.5'):
            1.5 & s

    def test___ror__(self):
        s1 = S([2, 3])
        s2 = set([1, 2]) | s1
        self.assertProperScriveSet(s2)
        self.assertEqual(3, len(s2))
        self.assertTrue(1 in s2)
        self.assertTrue(2 in s2)
        self.assertTrue(3 in s2)

        s = S()
        s._set_read_only()
        set() | s
        s._set_invalid()
        with self.assertRaises(INV):
            set() | s

        s1 = S()
        s2 = set() | s1
        s1._set_read_only()
        self.assertTrue(s2._read_only)
        s1._set_invalid()
        self.assertTrue(s2._invalid)

        s = S()
        with self.assertRaises(TypeError,
                               u'other must be set, not 1.5'):
            1.5 | s

    def test___rsub__(self):
        s1 = S([2, 3])
        s2 = set([1, 2, 3, 4]) - s1
        self.assertProperScriveSet(s2)
        self.assertEqual(2, len(s2))
        self.assertTrue(1 in s2)
        self.assertTrue(4 in s2)

        s = S()
        s._set_read_only()
        set() - s
        s._set_invalid()
        with self.assertRaises(INV):
            set() - s

        s1 = S()
        s2 = set() - s1
        s1._set_read_only()
        self.assertTrue(s2._read_only)
        s1._set_invalid()
        self.assertTrue(s2._invalid)

        s = S()
        with self.assertRaises(TypeError,
                               u'other must be set, not 1.5'):
            1.5 - s

    def test_get_by_attrs(self):
        class O(object):
            pass
        o1 = O()
        o1.key1 = 'val1'
        o1.key2 = 'val2'
        o2 = O()
        o2.key1 = 'val3'
        o2.key2 = 'val4'
        s = S([o1, o2])
        self.assertEqual(o1, s.get_by_attrs(key1='val1'))
        self.assertEqual(o1, s.get_by_attrs(key2='val2'))
        self.assertEqual(o1, s.get_by_attrs(key1='val1', key2='val2'))
        self.assertEqual(o2, s.get_by_attrs(key2='val4'))

        self.assertIsNone(s.get_by_attrs(key='val'))
        self.assertIsNone(s.get_by_attrs(key1='val2'))

        s._set_read_only()
        self.assertEqual(o1, s.get_by_attrs(key1='val1'))
        self.assertIsNone(s.get_by_attrs(key1='val2'))

        s._set_invalid()
        with self.assertRaises(INV):
            s.get_by_attrs(key1='val1')
            s.get_by_attrs(key1='val2')
