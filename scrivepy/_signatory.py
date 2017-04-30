from datetime import datetime
import re

from dateutil.tz import tzutc
import tvu

from scrivepy._field import Field
from scrivepy._object import \
     enum_descriptor, scrive_descriptor, ScriveEnum, ScriveObject
from scrivepy._set import scrive_set_descriptor


DeliveryStatus = ScriveEnum('DeliveryStatus',
                            'unknown not_delivered delivered, deferred')

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


class IDTVU(tvu.TVU):

    TYPES = unicode,

    def validate(self, value):
        if not re.search(r'^[0-9]+$', value):
            self.error(u'non-empty digit-string')


class remote_descriptor(scrive_descriptor):

    def _init(self, obj, kwargs_dict):
        setattr(obj, self._attr_name, self._default_ctor_value)

    def _serialize(self, obj, json_obj):
        pass


class id_descriptor(remote_descriptor):

    def _serialize(self, obj, json_obj):
        value = obj._id
        if value is not None:
            json_obj[u'id'] = value


class viewer_descriptor(scrive_descriptor):

    def _serialize(self, obj, json_obj):
        json_obj[u'is_signatory'] = not obj._is_viewer

    def _deserialize(self, obj, json_obj):
        super(viewer_descriptor, self)._deserialize(obj, json_obj)
        obj._is_viewer = not obj._is_viewer


class TimeTVU(tvu.TVU):

    TYPES = datetime, unicode

    def unify(self, value):
        if isinstance(value, unicode):
            try:
                value = datetime.strptime(value, '%Y-%m-%dT%H:%M:%SZ')
                return value.replace(tzinfo=tzutc())
            except ValueError:
                self.error(u'time string', soft=True)
        return value


class Signatory(ScriveObject):

    id = id_descriptor(IDTVU, read_only=True)
    user_id = id_descriptor(tvu.nullable(IDTVU), read_only=True)
    is_author = remote_descriptor(tvu.instance(bool), default_ctor_value=False,
                                  read_only=True)
    is_viewer = viewer_descriptor(tvu.instance(bool), default_ctor_value=False,
                                  serialized_name=u'is_signatory')
    fields = scrive_set_descriptor(Field)
    sign_order = scrive_descriptor(tvu.tvus.PositiveInt, default_ctor_value=1)
    sign_time = remote_descriptor(tvu.nullable(TimeTVU), read_only=True,
                                  default_ctor_value=None)
    seen_time = remote_descriptor(tvu.nullable(TimeTVU), read_only=True,
                                  default_ctor_value=None)
    invitation_read_time = remote_descriptor(
        tvu.nullable(TimeTVU), read_only=True, default_ctor_value=None,
        serialized_name=u'read_invitation_time')
    rejection_time = remote_descriptor(
        tvu.nullable(TimeTVU), serialized_name=u'rejected_time',
        read_only=True)
    sign_success_redirect_url = scrive_descriptor(tvu.tvus.Text,
                                                  default_ctor_value=u'')
    reject_redirect_url = scrive_descriptor(tvu.tvus.Text,
                                            default_ctor_value=u'')
    email_delivery_status = remote_descriptor(
        tvu.instance(DeliveryStatus, enum=True), read_only=True,
        default_ctor_value=DeliveryStatus.unknown)
    mobile_delivery_status = remote_descriptor(
        tvu.instance(DeliveryStatus, enum=True), read_only=True,
        default_ctor_value=DeliveryStatus.unknown)
    invitation_delivery_method = enum_descriptor(
        InvitationDeliveryMethod,
        default_ctor_value=InvitationDeliveryMethod.email,
        serialized_name=u'delivery_method')
    confirmation_delivery_method = enum_descriptor(
        ConfirmationDeliveryMethod,
        default_ctor_value=ConfirmationDeliveryMethod.email)
    view_authentication_method = enum_descriptor(
        ViewAuthenticationMethod,
        default_ctor_value=ViewAuthenticationMethod.standard,
        serialized_name=u'authentication_method_to_view')
    sign_authentication_method = enum_descriptor(
        SignAuthenticationMethod,
        default_ctor_value=SignAuthenticationMethod.standard,
        serialized_name=u'authentication_method_to_sign')
