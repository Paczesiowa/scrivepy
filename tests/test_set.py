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
