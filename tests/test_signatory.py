# coding: utf-8
from datetime import datetime

from dateutil.tz import tzutc

from scrivepy import (
    ConfirmationDeliveryMethod,
    DeliveryStatus,
    InvitationDeliveryMethod,
    NameField,
    Signatory,
    SignatureField,
    SignAuthenticationMethod,
    ViewAuthenticationMethod)

from scrivepy._field import Field

from tests.utils import IntegrationTestCase, describe


class SignatoryTest(IntegrationTestCase):

    O = Signatory
    default_ctor_kwargs = {}
    json = {u'id': u'123', u'user_id': u'456', u'is_author': False,
            u'is_signatory': False, u'fields': [], u'sign_order': 1,
            u'sign_time': None, u'seen_time': None,
            u'read_invitation_time': None,
            u'rejected_time': None,
            u'sign_success_redirect_url': u'',
            u'reject_redirect_url': u'',
            u'email_delivery_status': u'unknown',
            u'mobile_delivery_status': u'unknown',
            u'delivery_method': u'email',
            u'confirmation_delivery_method': u'email',
            u'authentication_method_to_view': u'standard',
            u'authentication_method_to_sign': u'standard'}

    def make_field(self, num=1):
        if num == 1:
            return NameField(value=u'John')
        else:
            return SignatureField(name=u'Signature 1')

    def _test_remote_attr(self, preset_values=None, **overrides):
        kwargs = {'serialized_values': [],
                  'bad_type_values': [],
                  'bad_val_values': [],
                  'serialized_name': None,
                  'skip_preservation': True,
                  'default_value': None}
        kwargs.update(preset_values or {}, **overrides)
        if kwargs['serialized_name'] is None:
            kwargs['serialized_name'] = kwargs['attr_name']
        serialized_name = kwargs['serialized_name']
        attr_name = kwargs['attr_name']

        self._test_attr_ctor(attr_name=attr_name,
                             good_values=[],
                             bad_type_values=[],
                             bad_val_values=[],
                             required=False,
                             default_value=kwargs['default_value'],
                             forbidden=True)

        self._test_attr_setter(attr_name=attr_name,
                               read_only=True,
                               good_values=[],
                               bad_type_values=[],
                               bad_val_values=[])

        # test that constructed objects dont serialize this field
        params, call_string = self._ctor_call()
        with describe('%s not in %s._to_json_obj()' % (serialized_name,
                                                       call_string)):
                o = self.O(**params)
                self.assertFalse(serialized_name in o._to_json_obj())

        # test that deserialized object serialize in the same way or skip
        for _, value in kwargs['serialized_values']:
            if kwargs['skip_preservation']:
                # test that for every _, v in serialized_values
                # serialized_name not in O._from_json_obj({serialized_name:v})
                # ...._to_json_obj()
                json = dict(self.json)
                json[serialized_name] = value
                str_attrs = (serialized_name, self._deser_call(json))
                with describe('%s not in %s._to_json_obj()' % str_attrs):
                    o = self.O._from_json_obj(json)
                    self.assertFalse(serialized_name in o._to_json_obj())
            else:
                # test that for every _, v in serialized_values
                # O._from_json_obj({serialized_name:v})._to_json_obj()
                # ...[serialized_name] == v
                json = dict(self.json)
                json[serialized_name] = value
                str_attrs = (self._deser_call(json), serialized_name,
                             repr(value))
                with describe('%s._to_json_obj()["%s"] == %s' % str_attrs):
                    o = self.O._from_json_obj(json)
                    self.assertEqual(o._to_json_obj()[attr_name], value)
                    self.assertEqual(type(o._to_json_obj()[attr_name]),
                                     type(value))

        self._test_attr_deserialization(
            attr_name=attr_name,
            serialized_name=serialized_name,
            serialized_values=kwargs['serialized_values'],
            bad_type_values=kwargs['bad_type_values'],
            bad_val_values=kwargs['bad_val_values'])

        self._test_invalid_field(attr_name + '77')

    def test_id(self):
        value_error = u'id must be non-empty digit-string'
        self._test_remote_attr({'attr_name': 'id',
                                'serialized_values': [(u'123', u'123'),
                                                      (u'456789', u'456789')],
                                'skip_preservation': False,
                                'bad_type_values': [([], u'unicode'),
                                                    (2, u'unicode'),
                                                    (None, u'unicode')],
                                'bad_val_values': [(u'', value_error),
                                                   (u'żółw', value_error),
                                                   (u'abc', value_error)]})

    def test_user_id(self):
        value_error = u'user_id must be non-empty digit-string'
        self._test_remote_attr({'attr_name': 'user_id',
                                'serialized_values': [(u'123', u'123'),
                                                      (u'456789', u'456789'),
                                                      (None, None)],
                                'bad_type_values': [([], u'unicode or None'),
                                                    (2, u'unicode or None')],
                                'bad_val_values': [(u'', value_error),
                                                   (u'żółw', value_error),
                                                   (u'abc', value_error)]})

    def test_is_author(self):
        self._test_remote_attr({'attr_name': 'is_author',
                                'serialized_values': [(True, True),
                                                      (False, False)],
                                'default_value': False,
                                'bad_type_values': [([], u'bool'),
                                                    (2, u'bool')],
                                'bad_val_values': []})

    def test_is_viewer(self):
        self._test_bool(attr_name='is_viewer', required=False,
                        serialized_values=[(True, False), (False, True)],
                        serialized_name=u'is_signatory', default_value=False)

    def test_fields(self):
        self._test_set(Field, 'fields', self.make_field)

    def test_sign_order(self):
        self._test_positive_int(attr_name='sign_order', required=False,
                                default_value=1)

    def _test_remote_time_attr(self, **kwargs):
        d1s = u'2014-10-29T15:40:20Z'
        d1 = datetime(2014, 10, 29, 15, 40, 20, tzinfo=tzutc())
        d2s = u'2017-04-22T12:56:00Z'
        d2 = datetime(2017, 4, 22, 12, 56, 0, tzinfo=tzutc())
        type_error = u'datetime, unicode or None'
        self._test_remote_attr({'serialized_values': [(d1, d1s), (d2, d2s)],
                                'bad_type_values': [([], type_error),
                                                    (2, type_error)],
                                'bad_val_values': [(u'2014-10-29T', u''),
                                                   (d1s + u'foo', u'')]},
                               **kwargs)

    def test_sign_time(self):
        self._test_remote_time_attr(attr_name='sign_time')

    def test_seen_time(self):
        self._test_remote_time_attr(attr_name='seen_time')

    def test_invitation_read_time(self):
        self._test_remote_time_attr(attr_name='invitation_read_time',
                                    serialized_name=u'read_invitation_time')

    def test_rejection_time(self):
        self._test_remote_time_attr(attr_name='rejection_time',
                                    serialized_name=u'rejected_time')

    def test_sign_success_redirect_url(self):
        self._test_text(attr_name='sign_success_redirect_url',
                        required=False, default_value=u'')

    def test_reject_redirect_url(self):
        self._test_text(attr_name='reject_redirect_url',
                        required=False, default_value=u'')

    def _test_remote_enum(self, enum_class, **kwargs):
        ename = enum_class.__name__
        serialized_values = [(enum_elem, enum_elem.value)
                             for enum_elem in enum_class]
        enum_variant_err = r'.*could be ' + ename + r"'s variant name.*"
        self._test_remote_attr({'serialized_values': serialized_values,
                               'bad_type_values': [({}, ename),
                                                   (0, ename),
                                                   ([], ename)],
                                'bad_val_values': [('wrong',
                                                    enum_variant_err)]},
                               **kwargs)

    def test_email_delivery_status(self):
        self._test_remote_enum(DeliveryStatus,
                               attr_name='email_delivery_status',
                               default_value=DeliveryStatus.unknown)

    def test_mobile_delivery_status(self):
        self._test_remote_enum(DeliveryStatus,
                               attr_name='mobile_delivery_status',
                               default_value=DeliveryStatus.unknown)

    def test_invitation_delivery_method(self):
        self._test_enum(InvitationDeliveryMethod,
                        attr_name='invitation_delivery_method',
                        required=False,
                        serialized_name=u'delivery_method',
                        default_value=InvitationDeliveryMethod.email)

    def test_confirmation_delivery_method(self):
        self._test_enum(ConfirmationDeliveryMethod,
                        attr_name='confirmation_delivery_method',
                        required=False,
                        default_value=ConfirmationDeliveryMethod.email)

    def test_view_authentication_method(self):
        self._test_enum(ViewAuthenticationMethod,
                        attr_name='view_authentication_method',
                        required=False,
                        serialized_name=u'authentication_method_to_view',
                        default_value=ViewAuthenticationMethod.standard)

    def test_sign_authentication_method(self):
        self._test_enum(SignAuthenticationMethod,
                        attr_name='sign_authentication_method',
                        required=False,
                        serialized_name=u'authentication_method_to_sign',
                        default_value=SignAuthenticationMethod.standard)
