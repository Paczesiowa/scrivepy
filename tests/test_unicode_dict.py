import type_value_unifier as tvu
from scrivepy import _unicode_dict, _object, _exceptions
from tests import utils


D = _unicode_dict.UnicodeDict
O = _object.ScriveObject
RO = _exceptions.ReadOnlyScriveObject
INV = _exceptions.InvalidScriveObject


class UnicodeDictTest(utils.TestCase):

    def assertProperUnicodeDict(self, d):
        self.assertTrue(isinstance(d, D))
        self.assertTrue(isinstance(d, dict))
        self.assertTrue(isinstance(d, _object.ScriveObject))
        self.assertTrue(hasattr(d, '_invalid'))
        self.assertTrue(hasattr(d, '_read_only'))

    def test_init(self):
        d = D()
        self.assertProperUnicodeDict(d)
        self.assertEqual(0, len(d))

        d2 = D({u'foo': u'bar', u'baz': u'quux'})
        self.assertProperUnicodeDict(d2)
        self.assertEqual(2, len(d2))
        self.assertEqual(d2[u'foo'], u'bar')
        self.assertEqual(d2[u'baz'], u'quux')

        d3 = D([(u'foo', u'bar'), (u'baz', u'quux')])
        self.assertProperUnicodeDict(d3)
        self.assertEqual(2, len(d3))
        self.assertEqual(d3[u'foo'], u'bar')
        self.assertEqual(d3[u'baz'], u'quux')

        d4 = D(foo=u'bar', baz=u'quux')
        self.assertProperUnicodeDict(d4)
        self.assertEqual(2, len(d4))
        self.assertEqual(d4[u'foo'], u'bar')
        self.assertEqual(d4[u'baz'], u'quux')

        d5 = D({u'foo': u'bar', u'baz': u'quux'}, corge=u'grault')
        self.assertProperUnicodeDict(d5)
        self.assertEqual(3, len(d5))
        self.assertEqual(d5[u'foo'], u'bar')
        self.assertEqual(d5[u'baz'], u'quux')
        self.assertEqual(d5[u'corge'], u'grault')

        self.assertFalse(d._read_only)
        self.assertFalse(d._invalid)

        d._set_read_only()
        self.assertTrue(d._read_only)
        self.assertFalse(d._invalid)

        d._set_invalid()
        self.assertTrue(d._read_only)
        self.assertTrue(d._invalid)

        err_msg = u'iterable must be a mapping or iterable, not None'
        with self.assertRaises(TypeError, err_msg):
            D(None)
        err_msg = u'iterable value must be unicode or str, not 2'
        with self.assertRaises(TypeError, err_msg):
            D({u'foo': u'bar', u'baz': 2})
        err_msg = u'iterable key must be unicode or str, not 2'
        with self.assertRaises(TypeError, err_msg):
            D({u'foo': u'bar', 2: u'baz'})
        err_msg = u'iterable value must be unicode or str, not 3'
        with self.assertRaises(TypeError, err_msg):
            D([(u'foo', u'bar'), (u'baz', 3)])
        err_msg = u'iterable key must be unicode or str, not 3'
        with self.assertRaises(TypeError, err_msg):
            D([(u'foo', u'bar'), (3, u'baz')])
        err_msg = u'kwargs value must be unicode or str, not 4'
        with self.assertRaises(TypeError, err_msg):
            D(foo=4)

    def test_clear(self):
        d = D(foo=u'bar')
        d.clear()
        self.assertEqual(0, len(d))

        d._set_read_only()
        with self.assertRaises(RO):
            d.clear()
        d._set_invalid()
        with self.assertRaises(INV):
            d.clear()

    def test_copy(self):
        d1 = D(foo=u'bar')
        self.assertEqual(1, len(d1))
        self.assertEqual(d1[u'foo'], u'bar')

        d2 = d1.copy()
        self.assertProperUnicodeDict(d2)
        self.assertEqual(1, len(d2))
        self.assertEqual(d2[u'foo'], u'bar')

        d1[u'baz'] = u'quux'

        self.assertEqual(2, len(d1))
        self.assertEqual(d1[u'foo'], u'bar')
        self.assertEqual(d1[u'baz'], u'quux')

        self.assertEqual(1, len(d2))
        self.assertEqual(d2[u'foo'], u'bar')

        d2[u'corge'] = u'grault'

        self.assertEqual(2, len(d1))
        self.assertEqual(d1[u'foo'], u'bar')
        self.assertEqual(d1[u'baz'], u'quux')

        self.assertEqual(2, len(d2))
        self.assertEqual(d2[u'foo'], u'bar')
        self.assertEqual(d2[u'corge'], u'grault')

        d1._set_read_only()
        self.assertTrue(d1._read_only)
        self.assertTrue(d2._read_only)

        d2._set_invalid()
        self.assertFalse(d1._invalid)
        self.assertTrue(d2._invalid)

        d = D()
        d._set_read_only()
        d.copy()
        d._set_invalid()
        with self.assertRaises(INV):
            d.copy()

        d1 = D()
        d2 = d1.copy()
        d1._set_read_only()
        self.assertTrue(d2._read_only)
        d1._set_invalid()
        self.assertTrue(d2._invalid)

    def test_fromkeys(self):
        with self.assertRaises(TypeError, None):
            d = D.fromkeys()

        d = D.fromkeys(set())
        self.assertProperUnicodeDict(d)
        self.assertEqual(0, len(d))

        d2 = D.fromkeys(set(['foo', 'bar']))
        self.assertProperUnicodeDict(d2)
        self.assertEqual(2, len(d2))
        self.assertEqual(d2[u'foo'], u'')
        self.assertEqual(d2[u'bar'], u'')

        d3 = D.fromkeys(['foo', 'bar'], 'baz')
        self.assertProperUnicodeDict(d3)
        self.assertEqual(2, len(d3))
        self.assertEqual(d3[u'foo'], u'baz')
        self.assertEqual(d3[u'bar'], 'baz')

        # TODO: typechecking
        err_msg = u'keys must be iterable, not None'
        with self.assertRaises(TypeError, err_msg):
            D.fromkeys(None)
        err_msg = u'keys[0] must be unicode or str, not 2'
        with self.assertRaises(TypeError, err_msg):
            D.fromkeys([2])
        err_msg = u'value must be unicode or str, not None'
        with self.assertRaises(TypeError, err_msg):
            D.fromkeys(set(), value=None)

    def test_get(self):
        d = D(foo=u'bar')
        self.assertEqual(d.get(u'foo'), u'bar')
        self.assertEqual(d.get(u'baz'), None)
        self.assertEqual(d.get(u'baz', 3), 3)

        d._set_read_only()
        d.get(u'foo')
        d._set_invalid()
        with self.assertRaises(INV):
            d.get(u'foo')

    def test_has_key(self):
        d = D(foo=u'bar')
        self.assertTrue(u'foo' in d)
        self.assertFalse(u'baz' in d)

        d._set_read_only()
        u'foo' in d
        d._set_invalid()
        with self.assertRaises(INV):
            u'foo' in d

    def test_items(self):
        d = D(foo=u'bar', baz=u'quux')
        items = d.items()
        self.assertEqual(sorted(items),
                         [(u'baz', u'quux'), (u'foo', u'bar')])

        d._set_read_only()
        d.items()
        d._set_invalid()
        with self.assertRaises(INV):
            d.items()

    def test_iteritems(self):
        d = D(foo=u'bar', baz=u'quux')
        items = d.iteritems()
        self.assertEqual(sorted(items),
                         [(u'baz', u'quux'), (u'foo', u'bar')])

        d._set_read_only()
        d.iteritems()
        d._set_invalid()
        with self.assertRaises(INV):
            d.iteritems()

    def test_iterkeys(self):
        d = D(foo=u'bar', baz=u'quux')
        keys = d.iterkeys()
        self.assertEqual(sorted(keys), [u'baz', u'foo'])

        d._set_read_only()
        d.iterkeys()
        d._set_invalid()
        with self.assertRaises(INV):
            d.iterkeys()

    def test_itervalues(self):
        d = D(foo=u'bar', baz=u'quux')
        values = d.itervalues()
        self.assertEqual(sorted(values), [u'bar', u'quux'])

        d._set_read_only()
        d.itervalues()
        d._set_invalid()
        with self.assertRaises(INV):
            d.itervalues()

    def test_keys(self):
        d = D(foo=u'bar', baz=u'quux')
        keys = d.keys()
        self.assertEqual(sorted(keys), [u'baz', u'foo'])

        d._set_read_only()
        d.keys()
        d._set_invalid()
        with self.assertRaises(INV):
            d.keys()

    def test_values(self):
        d = D(foo=u'bar', baz=u'quux')
        values = d.values()
        self.assertEqual(sorted(values), [u'bar', u'quux'])

        d._set_read_only()
        d.values()
        d._set_invalid()
        with self.assertRaises(INV):
            d.values()

    def test_viewkeys(self):
        d = D(foo=u'bar', baz=u'quux')
        keys = d.viewkeys()
        self.assertEqual(sorted(keys), [u'baz', u'foo'])

        d._set_read_only()
        d.viewkeys()
        d._set_invalid()
        with self.assertRaises(INV):
            d.viewkeys()

    def test_viewvalues(self):
        d = D(foo=u'bar', baz=u'quux')
        values = d.viewvalues()
        self.assertEqual(sorted(values), [u'bar', u'quux'])

        d._set_read_only()
        d.viewvalues()
        d._set_invalid()
        with self.assertRaises(INV):
            d.viewvalues()

    def test_viewitems(self):
        d = D(foo=u'bar', baz=u'quux')
        items = d.viewitems()
        self.assertEqual(sorted(items),
                         [(u'baz', u'quux'), (u'foo', u'bar')])

        d._set_read_only()
        d.viewitems()
        d._set_invalid()
        with self.assertRaises(INV):
            d.viewitems()

    def test_pop(self):
        d = D(foo=u'bar')

        self.assertEqual(1, len(d))
        self.assertEqual(d.pop(u'baz', 3), 3)
        self.assertEqual(1, len(d))

        with self.assertRaises(KeyError):
            d.pop(u'baz')

        self.assertEqual(d.pop(u'foo'), u'bar')
        self.assertEqual(0, len(d))

        d._set_read_only()
        with self.assertRaises(RO):
            d.pop(u'baz')
        d._set_invalid()
        with self.assertRaises(INV):
            d.pop(u'baz')

    def test_popitem(self):
        d = D(foo=u'bar')

        self.assertEqual(1, len(d))
        self.assertEqual(d.popitem(), (u'foo', u'bar'))
        self.assertEqual(0, len(d))

        with self.assertRaises(KeyError):
            d.popitem()

        d._set_read_only()
        with self.assertRaises(RO):
            d.popitem()
        d._set_invalid()
        with self.assertRaises(INV):
            d.popitem()

    def test_setdefault(self):
        d = D(foo=u'bar')

        self.assertEqual(d.setdefault(u'foo'), u'bar')

        self.assertEqual(1, len(d))
        self.assertEqual(d.setdefault(u'baz'), u'')
        self.assertEqual(2, len(d))
        self.assertEqual(d.setdefault(u'baz'), u'')
        self.assertEqual(2, len(d))

        self.assertEqual(d.setdefault(u'quux', u'corge'), u'corge')
        self.assertEqual(3, len(d))
        self.assertEqual(d.setdefault(u'quux'), u'corge')
        self.assertEqual(3, len(d))

        err_msg = u'default must be unicode or str, not None'
        with self.assertRaises(TypeError, err_msg):
            d.setdefault(u'foo', None)

        d._set_read_only()
        with self.assertRaises(RO):
            d.setdefault(u'foo')
        d._set_invalid()
        with self.assertRaises(INV):
            d.setdefault(u'foo')
