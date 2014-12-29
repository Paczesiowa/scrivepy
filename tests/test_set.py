from scrivepy import _set, _object, _exceptions
from tests import utils

S = _set.ScriveSet
RO = _exceptions.ReadOnlyScriveObject
INV = _exceptions.InvalidScriveObject


class ScriveSetTest(utils.TestCase):

    def setUp(self):
        pass

    def test_init(self):
        s = S()
        self.assertTrue(isinstance(s, set))
        self.assertTrue(isinstance(s, _object.ScriveObject))

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
        self.assertTrue(isinstance(s2, S))

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
        self.assertFalse(s2._read_only)

        s2._set_invalid()
        self.assertFalse(s1._invalid)
        self.assertTrue(s2._invalid)

        s = S()
        s._set_read_only()
        s.copy()
        s._set_invalid()
        with self.assertRaises(INV):
            s.copy()

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

    def test_intersection(self):
        s1 = S([1, 2, 3])
        s2 = S([1, 2])
        s3 = S([1])
        s = s1.intersection(s2, s3)
        self.assertTrue(isinstance(s, S))
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
        self.assertTrue(isinstance(s, S))
        self.assertEqual(2, len(s))
        self.assertTrue(1 in s)
        self.assertTrue(4 in s)

        s = S()
        s._set_read_only()
        s.symmetric_difference([])
        s._set_invalid()
        with self.assertRaises(INV):
            s.symmetric_difference([])

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
        self.assertEqual(1, len(s2))
        self.assertTrue(4 in s2)

        s._set_read_only()
        s.difference()
        s._set_invalid()
        with self.assertRaises(INV):
            s.difference()

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
