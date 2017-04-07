from enum import Enum
import tvu

from scrivepy._exceptions import InvalidResponse
from scrivepy._object import scrive_descriptor, ScriveObject
from scrivepy._set import scrive_set_descriptor


class Ratio(tvu.TVU):
    TYPES = (float, int)

    def unify(self, value):
        return float(value)

    def validate(self, value):
        if not 0. <= value <= 1.:
            self.error(u'in the <0,1> range (inclusive)')


class Tip(unicode, Enum):
    left = u'left'
    right = u'right'


class Anchor(ScriveObject):
    text = scrive_descriptor(tvu.tvus.NonEmptyText)
    index = scrive_descriptor(tvu.instance(int))


class tip_descriptor(scrive_descriptor):

    def __init__(self):
        super(tip_descriptor, self).__init__(tvu.instance(Tip, enum=True),
                                             default_ctor_value=Tip.right)

    def _deserialize(self, obj, json_obj):
        try:
            val = self._retrieve_from_json(obj, json_obj)
            obj._tip = Tip.left if val is None else Tip(val)
        except ValueError:
            err_msg = (u"Invalid value '" + repr(val) + u"' for 'tip' " +
                       u"in server's JSON response for Placement")
            raise InvalidResponse(err_msg)


class Placement(ScriveObject):

    FONT_SIZE_SMALL = 12. / 943.
    FONT_SIZE_NORMAL = 16. / 943.
    FONT_SIZE_LARGE = 20. / 943.
    FONT_SIZE_HUGE = 24. / 943.

    anchors = scrive_set_descriptor(Anchor)
    font_size = scrive_descriptor(Ratio, serialized_name=u'fsrel',
                                  default_ctor_value=FONT_SIZE_NORMAL)
    height = scrive_descriptor(Ratio, serialized_name=u'hrel')
    left = scrive_descriptor(Ratio, serialized_name=u'xrel')
    page = scrive_descriptor(tvu.tvus.PositiveInt, default_ctor_value=1)
    tip = tip_descriptor()
    top = scrive_descriptor(Ratio, serialized_name=u'yrel')
    width = scrive_descriptor(Ratio, serialized_name=u'wrel')
