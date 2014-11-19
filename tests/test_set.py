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
        s.difference_update([2, 4])
        self.assertEqual(2, len(s))
        self.assertTrue(1 in s)
        self.assertFalse(2 in s)
        self.assertTrue(3 in s)
        self.assertFalse(4 in s)

        s._set_read_only()
        with self.assertRaises(RO):
            s.difference_update([])
        s._set_invalid()
        with self.assertRaises(INV):
            s.difference_update([])
