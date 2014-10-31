from scrivepy import _signatory, _field, _exceptions
from tests import utils


S = _signatory.Signatory
IDM = _signatory.InvitationDeliveryMethod
CDM = _signatory.ConfirmationDeliveryMethod
F = _field


class SignatoryTest(utils.TestCase):

    def setUp(self):
        self.f1 = F.StandardField(name='first_name', value=u'John')
        self.f2 = F.CustomField(name=u'field', value=u'value')
        self.json = {u'id': u'123abc',
                     u'current': True,
                     u'signorder': 3,
                     u'undeliveredInvitation': True,
                     u'undeliveredMailInvitation': False,
                     u'undeliveredSMSInvitation': True,
                     u'deliveredInvitation': False,
                     u'delivery': u'email_mobile',
                     u'confirmationdelivery': u'none',
                     u'signs': True,
                     u'author': True,
                     u'saved': True,
                     u'datamismatch': u'first name doesnt match',
                     u'signdate': None,
                     u'seendate': None,
                     u'readdate': None,
                     u'rejecteddate': None,
                     u'rejectionreason': u'will not sign just because',
                     u'signsuccessredirect': u'http://example.com/',
                     u'rejectredirect': u'http://example.net/',
                     u'fields': [self.f1._to_json_obj(),
                                 self.f2._to_json_obj()]}

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
        s = self.s(fields=set([self.f1]), sign_order=2,
                   invitation_delivery_method='api',
                   confirmation_delivery_method='none',
                   viewer=True, author=True,
                   sign_success_redirect_url=u'http://example.com/',
                   rejection_redirect_url=u'http://example.net/')

        json = {u'fields': [self.f1],
                u'signorder': 2,
                u'delivery': u'api',
                u'confirmationdelivery': u'none',
                u'signs': False,
                u'author': True,
                u'signsuccessredirect': u'http://example.com/',
                u'rejectredirect': u'http://example.net/'}

        self.assertEqual(json, s._to_json_obj())

    def test_from_json_obj(self):
        s = S._from_json_obj(self.json)
        self.assertEqual(s.id, u'123abc')
        self.assertEqual(s.current, True)
        self.assertEqual(s.sign_order, 3)
        self.assertEqual(s.viewer, False)
        self.assertEqual(s.author, True)
        self.assertEqual(s.undelivered_invitation, True)
        self.assertEqual(s.undelivered_email_invitation, False)
        self.assertEqual(s.undelivered_sms_invitation, True)
        self.assertEqual(s.delivered_invitation, False)
        self.assertEqual(s.has_account, True)
        self.assertEqual(s.eleg_mismatch_message, u'first name doesnt match')
        self.assertEqual(s.invitation_delivery_method, IDM.email_and_mobile)
        self.assertEqual(s.confirmation_delivery_method, CDM.none)
        self.assertEqual(s.sign_time, None)
        self.assertEqual(s.view_time, None)
        self.assertEqual(s.invitation_view_time, None)
        self.assertEqual(s.rejection_time, None)
        self.assertEqual(s.rejection_message, u'will not sign just because')
        self.assertEqual(s.sign_success_redirect_url, u'http://example.com/')
        self.assertEqual(s.rejection_redirect_url, u'http://example.net/')

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
        self._test_server_field('id')

    def test_current(self):
        self._test_server_field('current')

    def test_sign_order(self):
        self._test_field('sign_order',
                         bad_value=[], correct_type='int or float',
                         default_good_value=1,
                         other_good_values=[(8., 8), 2],
                         serialized_name=u'signorder')

        err_msg = u'sign_order must be a positive integer, not: 0'
        with self.assertRaises(ValueError, err_msg):
            self.s(sign_order=0)

        err_msg = u'sign_order must be a round integer, not: 1.1'
        with self.assertRaises(ValueError, err_msg):
            self.s(sign_order=1.1)

        s = self.s()

        err_msg = u'sign_order must be a positive integer, not: 0'
        with self.assertRaises(ValueError, err_msg):
            s.sign_order = 0

        err_msg = u'sign_order must be a round integer, not: 1.1'
        with self.assertRaises(ValueError, err_msg):
            s.sign_order = 1.1

    def test_undelivered_invitation(self):
        self._test_server_field('undelivered_invitation')

    def test_undelivered_email_invitation(self):
        self._test_server_field('undelivered_email_invitation')

    def test_undelivered_sms_invitation(self):
        self._test_server_field('undelivered_sms_invitation')

    def test_delivered_invitation(self):
        self._test_server_field('delivered_invitation')

    def _test_server_field(self, field_name):
        s = self.s()
        self.assertIsNone(getattr(s, field_name))

        s._set_read_only()
        self.assertIsNone(getattr(s, field_name))

        s._set_invalid()
        with self.assertRaises(_exceptions.InvalidScriveObject, None):
            getattr(s, field_name)

    def test_invitation_delivery_method(self):
        self._test_field('invitation_delivery_method',
                         bad_value={}, correct_type=IDM,
                         default_good_value=IDM.email,
                         other_good_values=[IDM.pad,
                                            ('email_and_mobile',
                                             IDM.email_and_mobile),
                                            IDM.mobile],
                         serialized_name=u'delivery',
                         serialized_default_good_value=u'email',
                         bad_enum_value='wrong')

    def test_confirmation_delivery_method(self):
        self._test_field('confirmation_delivery_method',
                         bad_value=0, correct_type=CDM,
                         default_good_value=CDM.email,
                         other_good_values=[CDM.none,
                                            ('email_and_mobile',
                                             CDM.email_and_mobile),
                                            CDM.mobile],
                         serialized_name=u'confirmationdelivery',
                         serialized_default_good_value=u'email',
                         bad_enum_value='wrong')

    def test_viewer(self):
        self._test_field('viewer',
                         bad_value=[], correct_type=bool,
                         default_good_value=False,
                         other_good_values=[True],
                         serialized_name=u'signs',
                         serialized_default_good_value=True)

    def _test_field(self, field_name, bad_value, correct_type,
                    default_good_value, other_good_values,
                    serialized_name=None, serialized_default_good_value=None,
                    bad_enum_value=None):
        if serialized_name is None:
            serialized_name = field_name
        if serialized_default_good_value is None:
            serialized_default_good_value = default_good_value
        if isinstance(correct_type, str):
            correct_type_name = correct_type
        else:
            correct_type_name = correct_type.__name__

        type_err_msg = (field_name + u' must be ' + correct_type_name +
                        ', not ' + str(bad_value))
        with self.assertRaises(TypeError, type_err_msg):
            self.s(**{field_name: bad_value})

        if bad_enum_value is not None:
            enum_type_err_msg = (field_name + u' could be ' +
                                 correct_type_name +
                                 "'s variant name, not: " + bad_enum_value)
            with self.assertRaises(ValueError, enum_type_err_msg):
                self.s(**{field_name: bad_enum_value})

        # check default ctor value
        s = self.s()
        self.assertEqual(default_good_value, getattr(s, field_name))

        for good_value in other_good_values:
            if isinstance(good_value, tuple):
                good_value, unified_good_value = good_value
            else:
                unified_good_value = good_value
            s = self.s(**{field_name: good_value})
            self.assertEqual(unified_good_value, getattr(s, field_name))

        with self.assertRaises(TypeError, type_err_msg):
            setattr(s, field_name, bad_value)

        setattr(s, field_name, default_good_value)
        self.assertEqual(default_good_value, getattr(s, field_name))

        self.assertEqual(serialized_default_good_value,
                         s._to_json_obj()[serialized_name])

        s._set_read_only()
        self.assertEqual(default_good_value, getattr(s, field_name))
        for good_value in other_good_values:
            with self.assertRaises(_exceptions.ReadOnlyScriveObject, None):
                setattr(s, field_name, good_value)

        s._set_invalid()
        with self.assertRaises(_exceptions.InvalidScriveObject, None):
            getattr(s, field_name)
        for good_value in other_good_values:
            with self.assertRaises(_exceptions.InvalidScriveObject, None):
                setattr(s, field_name, good_value)

    def test_author(self):
        self._test_field('author',
                         bad_value=[], correct_type=bool,
                         default_good_value=False,
                         other_good_values=[True])

    def test_has_account(self):
        self._test_server_field('has_account')

    def test_eleg_mismatch_message(self):
        self._test_server_field('eleg_mismatch_message')

    def _test_time_field(self, field_name, serialized_field_name):
        self._test_server_field(field_name)
        json = dict(self.json)
        json[serialized_field_name] = u'2014-10-29T15:40:20Z'
        s = S._from_json_obj(json)
        date_field = getattr(s, field_name)
        self.assertEqual(date_field.year, 2014)
        self.assertEqual(date_field.month, 10)
        self.assertEqual(date_field.day, 29)
        self.assertEqual(date_field.hour, 15)
        self.assertEqual(date_field.minute, 40)
        self.assertEqual(date_field.second, 20)
        self.assertEqual(date_field.microsecond, 0)

    def test_sign_time(self):
        self._test_time_field('sign_time', u'signdate')

    def test_view_time(self):
        self._test_time_field('view_time', u'seendate')

    def test_invitation_view_time(self):
        self._test_time_field('invitation_view_time', u'readdate')

    def test_rejection_time(self):
        self._test_time_field('rejection_time', u'rejecteddate')

    def test_rejection_message(self):
        self._test_server_field('rejection_message')

    def test_sign_success_redirect_url(self):
        self._test_field('sign_success_redirect_url',
                         bad_value=[], correct_type='unicode or NoneType',
                         default_good_value=None,
                         other_good_values=[u'http://example.com/'],
                         serialized_name=u'signsuccessredirect')

    def test_rejection_redirect_url(self):
        self._test_field('rejection_redirect_url',
                         bad_value=[], correct_type='unicode or NoneType',
                         default_good_value=None,
                         other_good_values=[u'http://example.net/'],
                         serialized_name=u'rejectredirect')
