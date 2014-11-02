from scrivepy import _signatory, _field, _exceptions
from tests import utils


S = _signatory.Signatory
IDM = _signatory.InvitationDeliveryMethod
CDM = _signatory.ConfirmationDeliveryMethod
AM = _signatory.AuthenticationMethod
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
                     u'authentication': u'eleg',
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
                     u'signlink': u'/s/1/2/3',
                     u'fields': [self.f1._to_json_obj(),
                                 self.f2._to_json_obj()]}

    def o(self, *args, **kwargs):
        return S(*args, **kwargs)

    def test_flags(self):
        f1 = F.StandardField(name='first_name', value=u'John')
        f2 = F.CustomField(name=u'field', value=u'value')
        s = self.o(fields=set([f1, f2]))

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
        s = self.o(fields=set([self.f1]), sign_order=2,
                   invitation_delivery_method='api',
                   confirmation_delivery_method='none',
                   viewer=True, author=True,
                   sign_success_redirect_url=u'http://example.com/',
                   rejection_redirect_url=u'http://example.net/',
                   authentication_method='sms_pin')
        s._id = u'1'

        json = {u'fields': [self.f1],
                u'signorder': 2,
                u'delivery': u'api',
                u'confirmationdelivery': u'none',
                u'signs': False,
                u'author': True,
                u'signsuccessredirect': u'http://example.com/',
                u'rejectredirect': u'http://example.net/',
                u'authentication': u'sms_pin',
                u'id': u'1'}

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
        self.assertEqual(s.authentication_method, AM.eleg)
        self.assertEqual(s.sign_url, u'/s/1/2/3')

        self.assertEqual(sorted([f._to_json_obj()
                                 for f in s.fields]),
                         sorted([self.f1._to_json_obj(),
                                 self.f2._to_json_obj()]))

    def test_modification_of_default_fields_value(self):
        s1 = self.o()
        s1._fields.add(1)
        s2 = self.o()
        self.assertEqual(set(), set(s2.fields))

    def test_fields(self):
        err_msg = u'fields must be set, not 1'
        with self.assertRaises(TypeError, err_msg):
            self.o(fields=1)

        err_msg = u'fields must be set of Field objects, ' + \
            u'not: set([1])'
        with self.assertRaises(ValueError, err_msg):
            self.o(fields=set([1]))

        # check default ctor value
        s = self.o()
        self.assertEqual(set([]), set(s.fields))

        s = self.o(fields=set([self.f1]))
        self.assertEqual(set([self.f1]), set(s.fields))

        with self.assertRaises(TypeError, u'fields must be set, not 1'):
            s.fields = 1

        err_msg = u'fields must be set of Field objects, ' + \
            u'not: set([1])'
        with self.assertRaises(ValueError, err_msg):
            s.fields = set([1])

        s.fields = set([self.f2])
        self.assertEqual(set([self.f2]), set(s.fields))

        self.assertEqual([self.f2], s._to_json_obj()[u'fields'])

        s._set_read_only()
        self.assertEqual(set([self.f2]), set(s.fields))
        with self.assertRaises(_exceptions.ReadOnlyScriveObject, None):
            s.fields = set([self.f1])

        s._set_invalid()
        with self.assertRaises(_exceptions.InvalidScriveObject, None):
            s.fields
        with self.assertRaises(_exceptions.InvalidScriveObject, None):
            s.fields = set([self.f1])

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

        err_msg = \
            u'sign_order must be an integer greater or equal than 1, not: 0'
        with self.assertRaises(ValueError, err_msg):
            self.o(sign_order=0)

        err_msg = u'sign_order must be a round integer, not: 1.1'
        with self.assertRaises(ValueError, err_msg):
            self.o(sign_order=1.1)

        s = self.o()

        err_msg = \
            u'sign_order must be an integer greater or equal than 1, not: 0'
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

    def test_authentication_method(self):
        self._test_field('authentication_method',
                         bad_value=0, correct_type=AM,
                         default_good_value=AM.standard,
                         other_good_values=[AM.eleg, ('sms_pin', AM.sms_pin)],
                         serialized_name=u'authentication',
                         serialized_default_good_value=u'standard',
                         bad_enum_value='wrong')

    def test_sign_url(self):
        self._test_server_field('sign_url')
        json = self.json.copy()
        del json[u'signlink']
        s = S._from_json_obj(json)
        self.assertIsNone(s.sign_url)
