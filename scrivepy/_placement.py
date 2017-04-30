from enum import Enum
import tvu

from scrivepy._exceptions import InvalidResponse
from scrivepy._object import \
     scrive_descriptor, enum_descriptor, ScriveEnum, ScriveObject
from scrivepy._set import scrive_set_descriptor


class Ratio(tvu.TVU):
    TYPES = (float, int)

    def unify(self, value):
        return float(value)

    def validate(self, value):
        if not 0. <= value <= 1.:
            self.error(u'in the <0,1> range (inclusive)')


Tip = ScriveEnum('Tip', 'left right')


class Anchor(ScriveObject):
    text = scrive_descriptor(tvu.tvus.NonEmptyText)
    index = scrive_descriptor(tvu.instance(int))


class tip_descriptor(enum_descriptor):

    def __init__(self):
        super(tip_descriptor, self).__init__(Tip, default_ctor_value=Tip.right)

    def _deserialize(self, obj, json_obj):
        val = self._retrieve_from_json(obj, json_obj)
        if val is None:
            obj._tip = Tip.left
        else:
            super(tip_descriptor, self)._deserialize(obj, json_obj)


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
