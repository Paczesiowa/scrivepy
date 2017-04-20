import re

from dateutil.parser import parse as time_parse
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


class Signatory(ScriveObject):

    id = id_descriptor(IDTVU, read_only=True)
    user_id = id_descriptor(tvu.nullable(IDTVU), read_only=True)
    is_author = remote_descriptor(tvu.instance(bool), default_ctor_value=False,
                                  read_only=True)
