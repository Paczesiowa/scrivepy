# coding: utf-8
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

from tests.utils import IntegrationTestCase


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
            u'authentication_method_to_sign': u'standard',
            u'allows_highlighting': False,
            u'api_delivery_url': None}

    def make_field(self, num=1):
        if num == 1:
            return {u'type': u'name', u'is_obligatory': True, u'order': 1,
                    u'value': u'John', u'should_be_filled_by_sender': False,
                    u'placements': []}
        else:
            return {u'type': u'signature', u'is_obligatory': True,
                    u'placements': [], u'name': 'Signature 1'}

    def test_id(self):
        self._test_remote_id(attr_name='id', skip_preservation=False)

    def test_user_id(self):
        self._test_remote_id(attr_name='user_id', remote_null_ok=True)

    def test_is_author(self):
        self._test_remote_bool(attr_name='is_author', default_value=False)

    def test_is_viewer(self):
        self._test_bool(attr_name='is_viewer', required=False,
                        serialized_values=[(True, False), (False, True)],
                        serialized_name=u'is_signatory', default_value=False)

    def test_fields(self):
        self._test_set(Field, 'fields', self.make_field)

    def test_sign_order(self):
        self._test_positive_int(attr_name='sign_order', required=False,
                                default_value=1)

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

    def test_allows_highlighting(self):
        self._test_bool(attr_name='allows_highlighting', required=False,
                        default_value=False)

    def test_sign_url(self):
        self._test_remote_nullable_non_empty_text(attr_name='sign_url')
