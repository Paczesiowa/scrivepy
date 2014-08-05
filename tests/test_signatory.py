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
        s = self.s(fields=set([f1, f2]))

        self.assertIsNone(s._check_getter())
        self.assertIsNone(f1._check_getter())
        self.assertIsNone(f2._check_getter())
        self.assertIsNone(s._check_setter())
        self.assertIsNone(f1._check_setter())
        self.assertIsNone(f2._check_setter())

        s._set_read_only()
        self.assertIsNone(s._check_getter())
        self.assertIsNone(f1._check_getter())
        self.assertIsNone(f2._check_getter())
        self.assertRaises(_exceptions.ReadOnlyScriveObject, None,
                          s._check_setter)
        self.assertRaises(_exceptions.ReadOnlyScriveObject, None,
                          f1._check_setter)
        self.assertRaises(_exceptions.ReadOnlyScriveObject, None,
                          f2._check_setter)

        s._set_invalid()
        self.assertRaises(_exceptions.InvalidScriveObject, None,
                          s._check_getter)
        self.assertRaises(_exceptions.InvalidScriveObject, None,
                          f1._check_getter)
        self.assertRaises(_exceptions.InvalidScriveObject, None,
                          f2._check_getter)
        self.assertRaises(_exceptions.InvalidScriveObject, None,
                          s._check_setter)
        self.assertRaises(_exceptions.InvalidScriveObject, None,
                          f1._check_setter)
        self.assertRaises(_exceptions.InvalidScriveObject, None,
                          f2._check_setter)

    def test_to_json_obj(self):
        s = self.s(fields=set([self.f1]), sign_order=2)

        json = {u'fields': [self.f1],
                u'signorder': 2}

        self.assertEqual(json, s._to_json_obj())

    def test_from_json_obj(self):
        json = {u'id': u'123abc',
                u'current': True,
                u'signorder': 3,
                u'undeliveredInvitation': True,
                u'undeliveredMailInvitation': False,
                u'undeliveredSMSInvitation': True,
                u'fields': [self.f1._to_json_obj(),
                            self.f2._to_json_obj()]}
        s = S._from_json_obj(json)
        self.assertEqual(s.id, u'123abc')
        self.assertEqual(s.current, True)
        self.assertEqual(s.sign_order, 3)
        self.assertEqual(s.undelivered_invitation, True)
        self.assertEqual(s.undelivered_email_invitation, False)
        self.assertEqual(s.undelivered_sms_invitation, True)

        self.assertEqual(sorted([f._to_json_obj()
                                 for f in s.fields]),
                         sorted([self.f1._to_json_obj(),
                                 self.f2._to_json_obj()]))

    def test_modification_of_default_placements_value(self):
        s1 = self.s()
        s1._fields.add(1)
        s2 = self.s()
        self.assertEqual(set(), set(s2.fields))

    def test_fields(self):
        err_msg = u'fields must be set, not 1'
        with self.assertRaises(TypeError, err_msg):
            self.s(fields=1)

        err_msg = u'fields must be set of Field objects, ' + \
            u'not: set([1])'
        with self.assertRaises(ValueError, err_msg):
            self.s(fields=set([1]))

        # check default ctor value
        f = self.s()
        self.assertEqual(set([]), set(f.fields))

        f = self.s(fields=set([self.f1]))
        self.assertEqual(set([self.f1]), set(f.fields))

        with self.assertRaises(TypeError, u'fields must be set, not 1'):
            f.fields = 1

        err_msg = u'fields must be set of Field objects, ' + \
            u'not: set([1])'
        with self.assertRaises(ValueError, err_msg):
            f.fields = set([1])

        f.fields = set([self.f2])
        self.assertEqual(set([self.f2]), set(f.fields))

        self.assertEqual([self.f2], f._to_json_obj()[u'fields'])

        f._set_read_only()
        self.assertEqual(set([self.f2]), set(f.fields))
        with self.assertRaises(_exceptions.ReadOnlyScriveObject, None):
            f.fields = set([self.f1])

        f._set_invalid()
        with self.assertRaises(_exceptions.InvalidScriveObject, None):
            f.fields
        with self.assertRaises(_exceptions.InvalidScriveObject, None):
            f.fields = set([self.f1])

    def test_id(self):
        s = self.s()
        self.assertIsNone(s.id)

        s._set_read_only()
        self.assertIsNone(s.id)

        s._set_invalid()
        with self.assertRaises(_exceptions.InvalidScriveObject, None):
            s.id

    def test_current(self):
        s = self.s()
        self.assertIsNone(s.current)

        s._set_read_only()
        self.assertIsNone(s.current)

        s._set_invalid()
        with self.assertRaises(_exceptions.InvalidScriveObject, None):
            s.current

    def test_sign_order(self):
        with self.assertRaises(TypeError,
                               u'sign_order must be int or float, not []'):
            self.s(sign_order=[])

        err_msg = u'sign_order must be a positive integer, not: 0'
        with self.assertRaises(ValueError, err_msg):
            self.s(sign_order=0)

        err_msg = u'sign_order must be a round integer, not: 1.1'
        with self.assertRaises(ValueError, err_msg):
            self.s(sign_order=1.1)

        # check default ctor value
        s = self.s()
        self.assertEqual(1, s.sign_order)

        s = self.s(sign_order=8.)
        self.assertEqual(8, s.sign_order)

        s = self.s(sign_order=2)
        self.assertEqual(2, s.sign_order)

        with self.assertRaises(TypeError,
                               u'sign_order must be int or float, not []'):
            s.sign_order = []

        err_msg = u'sign_order must be a positive integer, not: 0'
        with self.assertRaises(ValueError, err_msg):
            s.sign_order = 0

        err_msg = u'sign_order must be a round integer, not: 1.1'
        with self.assertRaises(ValueError, err_msg):
            s.sign_order = 1.1

        s.sign_order = 8.
        self.assertEqual(8, s.sign_order)

        s.sign_order = 3
        self.assertEqual(3, s.sign_order)

        self.assertEqual(3, s._to_json_obj()[u'signorder'])

        s._set_read_only()
        self.assertEqual(3, s.sign_order)
        with self.assertRaises(_exceptions.ReadOnlyScriveObject, None):
            s.sign_order = 4

        s._set_invalid()
        with self.assertRaises(_exceptions.InvalidScriveObject, None):
            s.sign_order
        with self.assertRaises(_exceptions.InvalidScriveObject, None):
            s.sign_order = 4

    def test_undelivered_invitation(self):
        s = self.s()
        self.assertIsNone(s.undelivered_invitation)

        s._set_read_only()
        self.assertIsNone(s.undelivered_invitation)

        s._set_invalid()
        with self.assertRaises(_exceptions.InvalidScriveObject, None):
            s.undelivered_invitation

    def test_undelivered_email_invitation(self):
        s = self.s()
        self.assertIsNone(s.undelivered_email_invitation)

        s._set_read_only()
        self.assertIsNone(s.undelivered_email_invitation)

        s._set_invalid()
        with self.assertRaises(_exceptions.InvalidScriveObject, None):
            s.undelivered_email_invitation

    def test_undelivered_sms_invitation(self):
        s = self.s()
        self.assertIsNone(s.undelivered_sms_invitation)

        s._set_read_only()
        self.assertIsNone(s.undelivered_sms_invitation)

        s._set_invalid()
        with self.assertRaises(_exceptions.InvalidScriveObject, None):
            s.undelivered_sms_invitation
