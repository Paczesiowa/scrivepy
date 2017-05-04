from tvu import instance, nullable
from tvu.tvus import NonEmptyText, PositiveInt, Text

from scrivepy._field import Field
from scrivepy._object import (
     ScriveEnum,
     ScriveObject,
     enum_descriptor,
     id_descriptor,
     remote_descriptor,
     scrive_descriptor)
from scrivepy._set import scrive_set_descriptor
from scrivepy._tvus import TimeTVU


DeliveryStatus = ScriveEnum('DeliveryStatus',
                            'unknown not_delivered delivered deferred')

InvitationDeliveryMethod = ScriveEnum('InvitationDeliveryMethod',
                                      'email pad api mobile email_and_mobile')

ConfirmationDeliveryMethod = ScriveEnum('ConfirmationDeliveryMethod',
                                        'email mobile email_and_mobile none')


SignAuthenticationMethod = ScriveEnum('SignAuthenticationMethod',
                                      {'standard': 'standard',
                                       'swedish_bankid': 'se_bankid',
                                       'sms_pin': 'sms_pin'})

ViewAuthenticationMethod = ScriveEnum('ViewAuthenticationMethod',
                                      {'standard': 'standard',
                                       'swedish_bankid': 'se_bankid',
                                       'norwegian_bankid': 'no_bankid',
                                       'danish_nemid': 'dk_nemid'})


class viewer_descriptor(scrive_descriptor):

    def __init__(self):
        super(viewer_descriptor, self).__init__(
            instance(bool), default_ctor_value=False,
            serialized_name=u'is_signatory')

    def _serialize(self, obj, json_obj):
        json_obj[u'is_signatory'] = not obj._is_viewer

    def _deserialize(self, obj, json_obj):
        super(viewer_descriptor, self)._deserialize(obj, json_obj)
        obj._is_viewer = not obj._is_viewer


class Signatory(ScriveObject):

    allows_highlighting = scrive_descriptor(instance(bool),
                                            default_ctor_value=False)
    confirmation_delivery_method = enum_descriptor(
        ConfirmationDeliveryMethod,
        default_ctor_value=ConfirmationDeliveryMethod.email)
    email_delivery_status = remote_descriptor(
        instance(DeliveryStatus, enum=True),
        default_ctor_value=DeliveryStatus.unknown)
    fields = scrive_set_descriptor(Field)
    id = id_descriptor(preserve=True)
    invitation_delivery_method = enum_descriptor(
        InvitationDeliveryMethod,
        default_ctor_value=InvitationDeliveryMethod.email,
        serialized_name=u'delivery_method')
    invitation_read_time = remote_descriptor(
        nullable(TimeTVU), serialized_name=u'read_invitation_time')
    is_author = remote_descriptor(instance(bool), default_ctor_value=False)
    is_viewer = viewer_descriptor()
    mobile_delivery_status = remote_descriptor(
        instance(DeliveryStatus, enum=True),
        default_ctor_value=DeliveryStatus.unknown)
    reject_redirect_url = scrive_descriptor(Text, default_ctor_value=u'')
    rejection_time = remote_descriptor(nullable(TimeTVU),
                                       serialized_name=u'rejected_time')
    seen_time = remote_descriptor(nullable(TimeTVU))
    sign_authentication_method = enum_descriptor(
        SignAuthenticationMethod,
        default_ctor_value=SignAuthenticationMethod.standard,
        serialized_name=u'authentication_method_to_sign')
    sign_order = scrive_descriptor(PositiveInt, default_ctor_value=1)
    sign_success_redirect_url = scrive_descriptor(Text, default_ctor_value=u'')
    sign_time = remote_descriptor(nullable(TimeTVU))
    sign_url = remote_descriptor(nullable(NonEmptyText),
                                 serialized_name=u'api_delivery_url')
    user_id = id_descriptor(nullable_=True)
    view_authentication_method = enum_descriptor(
        ViewAuthenticationMethod,
        default_ctor_value=ViewAuthenticationMethod.standard,
        serialized_name=u'authentication_method_to_view')
