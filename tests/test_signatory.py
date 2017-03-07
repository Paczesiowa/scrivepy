# coding: utf-8
from datetime import datetime
from dateutil.tz import tzutc

from scrivepy import (
    ConfirmationDeliveryMethod,
    InvalidResponse,
    InvalidScriveObject,
    InvitationDeliveryMethod,
    SignAuthenticationMethod,
    Signatory,
    TextField,
    ViewAuthenticationMethod
    # AuthenticationMethod as AM,
    # ConfirmationDeliveryMethod as CDM,
    # TextField as CF,
    # InvitationDeliveryMethod as IDM,
    # Signatory as S,
    # SignatoryAttachment as A,
    # Scrive,
    # StandardField as SF,
    # StandardFieldType as SFT,
    # ReadOnlyScriveObject,
    # Error
)

from scrivepy._set import ScriveSet

from tests import utils


class SignatoryTest(utils.IntegrationTestCase):

    O = Signatory
    default_ctor_kwargs = {}
    json = {u'delivery_method': u'email',
            u'authentication_method_to_sign': u'standard',
            u'authentication_method_to_view': u'standard',
            u'is_signatory': True,
            u'sign_order': 1,
            u'sign_success_redirect_url': u'',
            u'reject_redirect_url': u'',
            u'allows_highlighting': False,
            u'id': u'123',
            u'user_id': None,
            u'is_author': False,
            u'seen_time': None,
            u'sign_time': None,
            u'read_invitation_time': None,
            u'rejected_time': None,
            u'confirmation_delivery_method': u'email'}

    def f1(self):
        return TextField(name='f1', value='v1')

    def f2(self):
        return TextField(name='f2', value='v2')

    def test_invitation_delivery(self):
        variant_err = r".*could be InvitationDeliveryMethod's variant name.*"
        self._test_attr(
            attr_name='invitation_delivery',
            good_values=[('email', InvitationDeliveryMethod.email),
                         ('pad', InvitationDeliveryMethod.pad),
                         ('mobile', InvitationDeliveryMethod.mobile),
                         ('api', InvitationDeliveryMethod.api),
                         ('email_and_mobile',
                          InvitationDeliveryMethod.email_and_mobile),
                         InvitationDeliveryMethod.email,
                         InvitationDeliveryMethod.pad,
                         InvitationDeliveryMethod.mobile,
                         InvitationDeliveryMethod.api,
                         InvitationDeliveryMethod.email_and_mobile],
            bad_type_values=[({}, u'InvitationDeliveryMethod'),
                             (0, u'InvitationDeliveryMethod')],
            bad_val_values=[('wrong', variant_err)],
            serialized_name='delivery_method',
            serialized_values=[(InvitationDeliveryMethod.email, u'email'),
                               (InvitationDeliveryMethod.pad, u'pad'),
                               (InvitationDeliveryMethod.mobile, u'mobile'),
                               (InvitationDeliveryMethod.api, u'api'),
                               (InvitationDeliveryMethod.email_and_mobile,
                                u'email_mobile')],
            default_value=InvitationDeliveryMethod.email,
            required=False)

    def test_confirmation_delivery(self):
        variant_err = r".*could be ConfirmationDeliveryMethod's variant name.*"
        self._test_attr(
            attr_name='confirmation_delivery',
            good_values=[('email', ConfirmationDeliveryMethod.email),
                         ('mobile', ConfirmationDeliveryMethod.mobile),
                         ('none', ConfirmationDeliveryMethod.none),
                         ('email_and_mobile',
                          ConfirmationDeliveryMethod.email_and_mobile),
                         ConfirmationDeliveryMethod.email,
                         ConfirmationDeliveryMethod.mobile,
                         ConfirmationDeliveryMethod.none,
                         ConfirmationDeliveryMethod.email_and_mobile],
            bad_type_values=[({}, u'ConfirmationDeliveryMethod'),
                             (0, u'ConfirmationDeliveryMethod')],
            bad_val_values=[('wrong', variant_err)],
            serialized_name='confirmation_delivery_method',
            serialized_values=[(ConfirmationDeliveryMethod.email, u'email'),
                               (ConfirmationDeliveryMethod.mobile, u'mobile'),
                               (ConfirmationDeliveryMethod.none, u'none'),
                               (ConfirmationDeliveryMethod.email_and_mobile,
                                u'email_mobile')],
            default_value=ConfirmationDeliveryMethod.email,
            required=False)

    def test_sign_auth(self):
        variant_err = r".*could be SignAuthenticationMethod's variant name.*"
        self._test_attr(
            attr_name='sign_auth',
            good_values=[('standard', SignAuthenticationMethod.standard),
                         ('swedish_bankid',
                          SignAuthenticationMethod.swedish_bankid),
                         ('sms_pin', SignAuthenticationMethod.sms_pin),
                         SignAuthenticationMethod.standard,
                         SignAuthenticationMethod.swedish_bankid,
                         SignAuthenticationMethod.sms_pin],
            bad_type_values=[({}, u'SignAuthenticationMethod'),
                             (0, u'SignAuthenticationMethod')],
            bad_val_values=[('wrong', variant_err)],
            serialized_name='authentication_method_to_sign',
            serialized_values=[(SignAuthenticationMethod.standard,
                                u'standard'),
                               (SignAuthenticationMethod.swedish_bankid,
                                u'se_bankid'),
                               (SignAuthenticationMethod.sms_pin, u'sms_pin')],
            default_value=SignAuthenticationMethod.standard,
            required=False)

    def test_viewer(self):
        self._test_attr(
            attr_name='viewer',
            good_values=[True, False],
            bad_type_values=[([], u'bool')],
            bad_val_values=[],
            serialized_name='is_signatory',
            serialized_values=[(True, False), (False, True)],
            default_value=False,
            required=False)

    def test_sign_order(self):
        self._test_attr(
            attr_name='sign_order',
            good_values=[1, 2, 100, (1., 1)],
            bad_type_values=[([], u'int or float')],
            bad_val_values=[(0, r'.*integer greater or equal to 1.*'),
                            (1.1, r'.*round number.*')],
            serialized_name='sign_order',
            serialized_values=[1, 2, 3, 100, (2., 2)],
            default_value=1,
            required=False)

    def test_sign_redirect_url(self):
        unicode_err = \
            u'sign_redirect_url must be unicode text, or ascii-only bytestring'
        self._test_attr(
            attr_name='sign_redirect_url',
            good_values=[u'foo', (b'bar', u'bar'), u'ą'],
            bad_type_values=[([], u'unicode or str')],
            bad_val_values=[(u'ą'.encode('utf-8'), unicode_err)],
            serialized_name='sign_success_redirect_url',
            serialized_values=[u'foo', u'ą'],
            default_value=u'',
            required=False)

    def test_reject_redirect_url(self):
        unicode_err = (u'reject_redirect_url must be unicode text, ' +
                       u'or ascii-only bytestring')
        self._test_attr(
            attr_name='reject_redirect_url',
            good_values=[u'foo', (b'bar', u'bar'), u'ą'],
            bad_type_values=[([], u'unicode or str')],
            bad_val_values=[(u'ą'.encode('utf-8'), unicode_err)],
            serialized_name='reject_redirect_url',
            serialized_values=[u'foo', u'ą'],
            default_value=u'',
            required=False)

    def test_view_auth(self):
        variant_err = r".*could be ViewAuthenticationMethod's variant name.*"
        self._test_attr(
            attr_name='view_auth',
            good_values=[('standard', ViewAuthenticationMethod.standard),
                         ('swedish_bankid',
                          ViewAuthenticationMethod.swedish_bankid),
                         ('norwegian_bankid',
                          ViewAuthenticationMethod.norwegian_bankid),
                         ViewAuthenticationMethod.standard,
                         ViewAuthenticationMethod.swedish_bankid,
                         ViewAuthenticationMethod.norwegian_bankid],
            bad_type_values=[({}, u'ViewAuthenticationMethod'),
                             (0, u'ViewAuthenticationMethod')],
            bad_val_values=[('wrong', variant_err)],
            serialized_name='authentication_method_to_view',
            serialized_values=[(ViewAuthenticationMethod.standard,
                                u'standard'),
                               (ViewAuthenticationMethod.swedish_bankid,
                                u'se_bankid'),
                               (ViewAuthenticationMethod.norwegian_bankid,
                                u'no_bankid')],
            default_value=ViewAuthenticationMethod.standard,
            required=False)

    def test_allows_highlighting(self):
        self._test_attr(
            attr_name='allows_highlighting',
            good_values=[True, False],
            bad_type_values=[([], u'bool')],
            bad_val_values=[],
            serialized_name='allows_highlighting',
            serialized_values=[True, False],
            default_value=False,
            required=False)

    def test_id(self):
        self._test_server_attr(attr_name='id', serialized_name=u'id',
                               serialized_values=[u'123', u'456'],
                               is_send_back=True)

    def test_user_id(self):
        self._test_server_attr(attr_name='user_id', serialized_name=u'user_id',
                               serialized_values=[u'123', None])

    def test_author(self):
        self._test_server_attr(attr_name='author',
                               serialized_name=u'is_author',
                               serialized_values=[True, False],
                               default_manual_val=False)

    def test_view_time(self):
        time_tuple = (datetime(2014, 10, 29, 15, 40, 20, tzinfo=tzutc()),
                      u'2014-10-29T15:40:20Z')
        self._test_server_attr(attr_name='view_time',
                               serialized_name=u'seen_time',
                               serialized_values=[None, time_tuple])

    def test_sign_time(self):
        time_tuple = (datetime(2014, 10, 29, 15, 40, 20, tzinfo=tzutc()),
                      u'2014-10-29T15:40:20Z')
        self._test_server_attr(attr_name='sign_time',
                               serialized_name=u'sign_time',
                               serialized_values=[None, time_tuple])

    def test_read_invitation_time(self):
        time_tuple = (datetime(2014, 10, 29, 15, 40, 20, tzinfo=tzutc()),
                      u'2014-10-29T15:40:20Z')
        self._test_server_attr(attr_name='invitation_view_time',
                               serialized_name=u'read_invitation_time',
                               serialized_values=[None, time_tuple])

    def test_rejection_time(self):
        time_tuple = (datetime(2014, 10, 29, 15, 40, 20, tzinfo=tzutc()),
                      u'2014-10-29T15:40:20Z')
        self._test_server_attr(attr_name='rejection_time',
                               serialized_name=u'rejected_time',
                               serialized_values=[None, time_tuple])

    # def setUp(self):
    #     self.O = S
    #     self.f1 = SF(name='first_name', value=u'John')
    #     self.f2 = CF(name=u'field', value=u'value')
    #     self.a1 = A(u'id1', u'Scan or picture of personal id1')
    #     self.a2 = A(u'id2', u'Scan or picture of personal id2')
    #     self.json = {u'id': u'123abc',
    #                  u'current': True,
    #                  u'signorder': 3,
    #                  u'undeliveredInvitation': True,
    #                  u'undeliveredMailInvitation': False,
    #                  u'undeliveredSMSInvitation': True,
    #                  u'deliveredInvitation': False,
    #                  u'delivery': u'email_mobile',
    #                  u'confirmationdelivery': u'none',
    #                  u'authentication': u'eleg',
    #                  u'signs': True,
    #                  u'author': True,
    #                  u'saved': True,
    #                  u'datamismatch': u'first name doesnt match',
    #                  u'allowshighlighting': True,
    #                  u'signdate': None,
    #                  u'seendate': None,
    #                  u'readdate': None,
    #                  u'rejecteddate': None,
    #                  u'rejectionreason': u'will not sign just because',
    #                  u'signsuccessredirect': u'http://example.com/',
    #                  u'rejectredirect': u'http://example.net/',
    #                  u'signlink': u'/s/1/2/3',
    #                  u'attachments': [self.a1._to_json_obj(),
    #                                   self.a2._to_json_obj()],
    #                  u'fields': [self.f1._to_json_obj(),
    #                              self.f2._to_json_obj()]}

    # def o(self, *args, **kwargs):
    #     return S(*args, **kwargs)

    # def test_flags(self):
    #     f1 = SF(name='first_name', value=u'John')
    #     f2 = CF(name=u'field', value=u'value')
    #     s = self.o()
    #     s.fields.update([f1, f2])

    #     self.assertIsNone(s._check_getter())
    #     self.assertIsNone(f1._check_getter())
    #     self.assertIsNone(f2._check_getter())
    #     self.assertIsNone(s._check_setter())
    #     self.assertIsNone(f1._check_setter())
    #     self.assertIsNone(f2._check_setter())

    #     s._set_read_only()
    #     self.assertIsNone(s._check_getter())
    #     self.assertIsNone(f1._check_getter())
    #     self.assertIsNone(f2._check_getter())
    #     self.assertRaises(ReadOnlyScriveObject, None,
    #                       s._check_setter)
    #     self.assertRaises(ReadOnlyScriveObject, None,
    #                       f1._check_setter)
    #     self.assertRaises(ReadOnlyScriveObject, None,
    #                       f2._check_setter)

    #     s._set_invalid()
    #     self.assertRaises(InvalidScriveObject, None,
    #                       s._check_getter)
    #     self.assertRaises(InvalidScriveObject, None,
    #                       f1._check_getter)
    #     self.assertRaises(InvalidScriveObject, None,
    #                       f2._check_getter)
    #     self.assertRaises(InvalidScriveObject, None,
    #                       s._check_setter)
    #     self.assertRaises(InvalidScriveObject, None,
    #                       f1._check_setter)
    #     self.assertRaises(InvalidScriveObject, None,
    #                       f2._check_setter)

    # def test_to_json_obj(self):
    #     s = self.o(sign_order=2, invitation_delivery_method='api',
    #                confirmation_delivery_method='none',
    #                viewer=True,
    #                sign_success_redirect_url=u'http://example.com/',
    #                rejection_redirect_url=u'http://example.net/',
    #                allows_highlighting=True,
    #                authentication_method='sms_pin')
    #     s.fields.add(self.f1)
    #     s.attachments.add(self.a1)
    #     s._id = u'1'

    #     json = {u'fields': [self.f1],
    #             u'attachments': [self.a1],
    #             u'signorder': 2,
    #             u'delivery': u'api',
    #             u'confirmationdelivery': u'none',
    #             u'signs': False,
    #             u'author': False,
    #             u'signsuccessredirect': u'http://example.com/',
    #             u'rejectredirect': u'http://example.net/',
    #             u'allowshighlighting': True,
    #             u'authentication': u'sms_pin',
    #             u'id': u'1'}

    #     self.assertEqual(json, s._to_json_obj())

    # def test_from_json_obj(self):
    #     s = S._from_json_obj(self.json)
    #     self.assertEqual(s.id, u'123abc')
    #     self.assertTrue(s.current)
    #     self.assertEqual(s.sign_order, 3)
    #     self.assertFalse(s.viewer)
    #     self.assertTrue(s.allows_highlighting)
    #     self.assertTrue(s.author)
    #     self.assertTrue(s.undelivered_invitation)
    #     self.assertFalse(s.undelivered_email_invitation)
    #     self.assertTrue(s.undelivered_sms_invitation)
    #     self.assertFalse(s.delivered_invitation)
    #     self.assertTrue(s.has_account)
    #     self.assertEqual(s.eleg_mismatch_message, u'first name doesnt match')
    #     self.assertEqual(s.invitation_delivery_method, IDM.email_and_mobile)
    #     self.assertEqual(s.confirmation_delivery_method, CDM.none)
    #     self.assertIsNone(s.sign_time)
    #     self.assertIsNone(s.view_time)
    #     self.assertIsNone(s.invitation_view_time)
    #     self.assertIsNone(s.rejection_time)
    #     self.assertEqual(s.rejection_message, u'will not sign just because')
    #     self.assertEqual(s.sign_success_redirect_url, u'http://example.com/')
    #     self.assertEqual(s.rejection_redirect_url, u'http://example.net/')
    #     self.assertEqual(s.authentication_method, AM.eleg)
    #     self.assertEqual(s.sign_url, u'/s/1/2/3')

    #     self.assertEqual(sorted([f._to_json_obj()
    #                              for f in s.fields]),
    #                      sorted([self.f1._to_json_obj(),
    #                              self.f2._to_json_obj()]))

    # def test_fields(self):
    #     # check default ctor value
    #     s = self.o()
    #     self.assertEqual(ScriveSet(), s.fields)

    #     s.fields.add(self.f1)
    #     self.assertEqual(ScriveSet([self.f1]), s.fields)

    #     err_msg = u'elem must be Field, not 1'
    #     with self.assertRaises(TypeError, err_msg):
    #         s.fields.add(1)

    #     s.fields.clear()
    #     s.fields.add(self.f2)
    #     self.assertEqual(ScriveSet([self.f2]), s.fields)

    #     self.assertEqual([self.f2], s._to_json_obj()[u'fields'])

    #     s._set_read_only()
    #     # set() is because the 2nd one is read only and not really equal
    #     self.assertEqual(set(ScriveSet([self.f2])), set(s.fields))
    #     with self.assertRaises(ReadOnlyScriveObject, None):
    #         s.fields.clear()
    #         s.fields.add(self.f1)

    #     flds = s.fields
    #     s._set_invalid()
    #     with self.assertRaises(InvalidScriveObject, None):
    #         s.fields
    #     with self.assertRaises(InvalidScriveObject, None):
    #         flds.add(self.f1)

    # def test_current(self):
    #     self._test_server_field('current')

    # def test_undelivered_invitation(self):
    #     self._test_server_field('undelivered_invitation')

    # def test_undelivered_email_invitation(self):
    #     self._test_server_field('undelivered_email_invitation')

    # def test_undelivered_sms_invitation(self):
    #     self._test_server_field('undelivered_sms_invitation')

    # def test_delivered_invitation(self):
    #     self._test_server_field('delivered_invitation')

    # def test_has_account(self):
    #     self._test_server_field('has_account')

    # def test_eleg_mismatch_message(self):
    #     self._test_server_field('eleg_mismatch_message')

    # def test_invitation_view_time(self):
    #     self._test_time_field('invitation_view_time', u'readdate')

    # def test_sign_url(self):
    #     self._test_server_field('sign_url')
    #     json = self.json.copy()
    #     del json[u'signlink']
    #     s = S._from_json_obj(json)
    #     self.assertIsNone(s.sign_url)

    # def test_absolute_sign_url(self):
    #     json = self.json.copy()
    #     s = S._from_json_obj(json)
    #     with self.assertRaises(Error, u'API not set'):
    #         s.absolute_sign_url()
    #     s._set_read_only()
    #     with self.assertRaises(Error, u'API not set'):
    #         s.absolute_sign_url()
    #     s._set_invalid()
    #     with self.assertRaises(InvalidScriveObject, None):
    #         s.absolute_sign_url()

    #     s = S._from_json_obj(json)
    #     api = Scrive(client_credentials_identifier='',
    #                  client_credentials_secret='',
    #                  token_credentials_identifier='',
    #                  token_credentials_secret='',
    #                  api_hostname='127.0.0.1:8000',
    #                  https=True)
    #     s._set_api(api, None)
    #     self.assertEqual('https://127.0.0.1:8000/s/1/2/3',
    #                      s.absolute_sign_url())
    #     s._set_read_only()
    #     self.assertEqual('https://127.0.0.1:8000/s/1/2/3',
    #                      s.absolute_sign_url())
    #     s._set_invalid()
    #     with self.assertRaises(InvalidScriveObject, None):
    #         s.absolute_sign_url()

    #     json = self.json.copy()
    #     del json[u'signlink']
    #     s = S._from_json_obj(json)
    #     self.assertIsNone(s.absolute_sign_url())
    #     s._set_read_only()
    #     self.assertIsNone(s.absolute_sign_url())
    #     s._set_invalid()
    #     with self.assertRaises(InvalidScriveObject, None):
    #         s.absolute_sign_url()

    #     s = S._from_json_obj(json)
    #     s._set_api(api, None)
    #     self.assertIsNone(s.absolute_sign_url())
    #     s._set_read_only()
    #     self.assertIsNone(s.absolute_sign_url())
    #     s._set_invalid()
    #     with self.assertRaises(InvalidScriveObject, None):
    #         s.absolute_sign_url()

    # def test_attachments(self):
    #     # check default ctor value
    #     s = self.o()
    #     self.assertEqual(ScriveSet(), s.attachments)

    #     s.attachments.add(self.a1)
    #     self.assertEqual(ScriveSet([self.a1]), s.attachments)

    #     err_msg = u'elem must be SignatoryAttachment, not 1'
    #     with self.assertRaises(TypeError, err_msg):
    #         s.attachments.add(1)

    #     s.attachments.clear()
    #     s.attachments.add(self.a2)
    #     self.assertEqual(ScriveSet([self.a2]), s.attachments)

    #     self.assertEqual([self.a2], s._to_json_obj()[u'attachments'])

    #     s._set_read_only()
    #     # set() is because the 2nd one is read only and not really equal
    #     self.assertEqual(set(ScriveSet([self.a2])), set(s.attachments))
    #     with self.assertRaises(ReadOnlyScriveObject, None):
    #         s.attachments.clear()
    #         s.attachments.add(self.a1)

    #     atts = s.attachments
    #     s._set_invalid()
    #     with self.assertRaises(InvalidScriveObject, None):
    #         s.attachments
    #     with self.assertRaises(InvalidScriveObject, None):
    #         atts.add(self.a1)

    # @utils.integration
    # def test_attachments_file(self):
    #     with self.new_document_from_file() as d:
    #         author = d.author
    #         sig = self.o()
    #         sig.invitation_delivery_method = 'pad'
    #         sig.confirmation_delivery_method = 'none'
    #         att1 = A(u'id1', u'Scan or picture of personal id1')
    #         att2 = A(u'id2', u'Scan or picture of personal id2')
    #         sig.attachments.update([att1, att2])
    #         d.signatories.add(sig)
    #         d = self.api.update_document(d)
    #         d = self.api.ready(d)
    #         author = d.author
    #         d = self.api._sign(d, author)
    #         sig = d.other_signatory()
    #         d = self.api._set_signatory_attachment(d, sig, 'id1', 'pic1.pdf',
    #                                                self.test_doc_contents,
    #                                                'application/pdf')
    #         sig = d.other_signatory()
    #         d = self.api._set_signatory_attachment(d, sig, 'id2', 'pic2.pdf',
    #                                                self.test_doc_contents,
    #                                                'application/pdf')
    #         sig = d.other_signatory()
    #         d = self.api._sign(d, sig)
    #         sig = d.other_signatory()

    #         for att in sig.attachments:
    #             if att.requested_name == u'id1':
    #                 self.assertEqual(att.description,
    #                                  u'Scan or picture of personal id1')
    #                 self.assertEqual(u'pic1.pdf', att.file.name)
    #             else:
    #                 self.assertEqual(att.description,
    #                                  u'Scan or picture of personal id2')
    #                 self.assertEqual(u'pic2.pdf', att.file.name)
    #             self.assertPDFsEqual(self.test_doc_contents,
    #                                  att.file.get_bytes())

    #         sig._set_read_only()
    #         for att in sig.attachments:
    #             self.assertTrue(att.file._read_only)

    #         files = [att.file for att in sig.attachments]
    #         sig._set_invalid()
    #         for file_ in files:
    #             with self.assertRaises(InvalidScriveObject, None):
    #                 file_.get_bytes()

    # def test_full_name(self):
    #     json = self.json.copy()
    #     json[u'fields'] = []
    #     s = S._from_json_obj(json)
    #     self.assertEqual(u'', s.full_name)
    #     s._set_read_only()
    #     self.assertEqual(u'', s.full_name)
    #     with self.assertRaises(ReadOnlyScriveObject, None):
    #         s.full_name = u'James'
    #     s._set_invalid()
    #     with self.assertRaises(InvalidScriveObject, None):
    #         s.full_name = u'James'
    #     with self.assertRaises(InvalidScriveObject, None):
    #         s.full_name

    #     s = S._from_json_obj(json)
    #     s.fields.add(SF(name='first_name', value=u'John'))
    #     self.assertEqual(u'John', s.full_name)

    #     s.fields.add(CF(name=u'field', value=u'value'))
    #     self.assertEqual(u'John', s.full_name)

    #     s.fields.clear()
    #     s.fields.add(SF(name='last_name', value=u'Smith'))
    #     self.assertEqual(u'Smith', s.full_name)

    #     s.fields.add(CF(name=u'field', value=u'value'))
    #     self.assertEqual(u'Smith', s.full_name)

    #     s.fields.add(SF(name='first_name', value=u'John'))
    #     self.assertEqual(u'John Smith', s.full_name)

    #     s = S._from_json_obj(json)
    #     s.full_name = u'John'

    #     self.assertEqual(u'John', s.full_name)
    #     self.assertEqual(2, len(s.fields))
    #     f1, f2 = list(s.fields)
    #     if f1.name != SFT.first_name:
    #         f1, f2 = f2, f1
    #     self.assertEqual(f1.name, SFT.first_name)
    #     self.assertEqual(f2.name, SFT.last_name)
    #     self.assertEqual(f1.value, u'John')
    #     self.assertEqual(f2.value, u'')

    #     s.full_name = u'John Smith'

    #     self.assertEqual(u'John Smith', s.full_name)
    #     self.assertEqual(2, len(s.fields))
    #     f1, f2 = list(s.fields)
    #     if f1.name != SFT.first_name:
    #         f1, f2 = f2, f1
    #     self.assertEqual(f1.name, SFT.first_name)
    #     self.assertEqual(f2.name, SFT.last_name)
    #     self.assertEqual(f1.value, u'John')
    #     self.assertEqual(f2.value, u'Smith')
