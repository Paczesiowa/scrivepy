from datetime import datetime
import re

from dateutil.tz import tzutc
from enum import Enum
import tvu

from scrivepy._field import Field
from scrivepy._object import scrive_descriptor, ScriveObject
from scrivepy._set import scrive_set_descriptor


class InvitationDeliveryMethod(unicode, Enum):
    email = u'email'
    pad = u'pad'
    api = u'api'
    mobile = u'mobile'
    email_and_mobile = u'email_mobile'


class ConfirmationDeliveryMethod(unicode, Enum):
    email = u'email'
    mobile = u'mobile'
    email_and_mobile = u'email_mobile'
    none = u'none'


class SignAuthenticationMethod(unicode, Enum):
    standard = u'standard'
    swedish_bankid = u'se_bankid'
    sms_pin = u'sms_pin'


class ViewAuthenticationMethod(unicode, Enum):
    standard = u'standard'
    swedish_bankid = u'se_bankid'
    norwegian_bankid = u'no_bankid'


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
