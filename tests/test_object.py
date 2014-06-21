from scrivepy import _object, _exceptions
from tests import utils


class ScriveObjectTest(utils.TestCase):

    def test_flags(self):
        obj = _object.ScriveObject()
        self.assertIsNone(obj._check_getter())
        self.assertIsNone(obj._check_setter())
        obj._set_read_only()
        self.assertIsNone(obj._check_getter())
        self.assertRaises(_exceptions.ReadOnlyScriveObject, None,
                          obj._check_setter)
        obj._set_invalid()
        self.assertRaises(_exceptions.InvalidScriveObject, None,
                          obj._check_getter)
        self.assertRaises(_exceptions.InvalidScriveObject, None,
                          obj._check_setter)

    def test_serialization(self):
        class DerivedObject(_object.ScriveObject):
            def _to_json_obj(self):
                return self._json

        obj = DerivedObject()
        obj._json = {u'key': u'val'}

        result = obj._to_json()
        self.assertEqual(u'{"key": "val"}', result)

        obj2 = DerivedObject()
        obj2._json = {u'key2': u'val2'}
        obj._json[u'key'] = obj2

        result = obj._to_json()
        self.assertEqual(u'{"key": {"key2": "val2"}}', result)
