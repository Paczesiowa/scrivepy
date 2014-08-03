from scrivepy import _signatory, _field, _exceptions
from tests import utils


S = _signatory.Signatory
F = _field


class SignatoryTest(utils.TestCase):

    def setUp(self):
        self.f1 = F.StandardField(name='first_name', value=u'John')
        self.f2 = F.CustomField(name=u'field', value=u'value')

    def s(self, *args, **kwargs):
        return S(*args, **kwargs)

    def test_flags(self):
        f1 = F.StandardField(name='first_name', value=u'John')
        f2 = F.CustomField(name=u'field', value=u'value')
        pass
        # s = self.s(fields=set([f1, f2]))

        # self.assertIsNone(s._check_getter())
        # self.assertIsNone(f1._check_getter())
        # self.assertIsNone(f2._check_getter())
        # self.assertIsNone(s._check_setter())
        # self.assertIsNone(f1._check_setter())
        # self.assertIsNone(f2._check_setter())

        # s._set_read_only()
        # self.assertIsNone(s._check_getter())
        # self.assertIsNone(f1._check_getter())
        # self.assertIsNone(f2._check_getter())
        # self.assertRaises(_exceptions.ReadOnlyScriveObject, None,
        #                   s._check_setter)
        # self.assertRaises(_exceptions.ReadOnlyScriveObject, None,
        #                   f1._check_setter)
        # self.assertRaises(_exceptions.ReadOnlyScriveObject, None,
        #                   f2._check_setter)

        # s._set_invalid()
        # self.assertRaises(_exceptions.InvalidScriveObject, None,
        #                   s._check_getter)
        # self.assertRaises(_exceptions.InvalidScriveObject, None,
        #                   f1._check_getter)
        # self.assertRaises(_exceptions.InvalidScriveObject, None,
        #                   f2._check_getter)
        # self.assertRaises(_exceptions.InvalidScriveObject, None,
        #                   s._check_setter)
        # self.assertRaises(_exceptions.InvalidScriveObject, None,
        #                   f1._check_setter)
        # self.assertRaises(_exceptions.InvalidScriveObject, None,
        #                   f2._check_setter)

    def test_to_json_obj(self):
        pass
        # s = self.s(fields=set([self.f1]))

        # json = {u'fields': [self.f1]}

        # self.assertEqual(json, s._to_json_obj())

    def test_modification_of_default_placements_value(self):
        pass
        # s1 = self.s()
        # s1._fields.add(1)
        # s2 = self.s()
        # self.assertEqual(set(), set(s2.fields))
