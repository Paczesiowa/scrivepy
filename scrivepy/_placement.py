import enum
import tvu

from scrivepy._object import scrive_descriptor, ScriveObject
from scrivepy._set import ScriveSet


class Ratio(tvu.TVU):

    TYPES = (float, int)

    def unify(self, value):
        return float(value)

    def validate(self, value):
        if not 0. <= value <= 1.:
            self.error(u'in the <0,1> range (inclusive)')


class TipSide(unicode, enum.Enum):
    left_tip = u'left'
    right_tip = u'right'


MaybeTipSide = tvu.nullable(tvu.instance(TipSide, enum=True))


class Anchor(ScriveObject):

    @tvu(text=tvu.tvus.NonEmptyText, index=tvu.instance(int))
    def __init__(self, text, index):
        super(Anchor, self).__init__()
        self._text = text
        self._index = index

    text = scrive_descriptor(tvu.tvus.NonEmptyText)
    index = scrive_descriptor(tvu.instance(int))

    def _to_json_obj(self):
        return {u'text': self.text, u'index': self.index}

    @classmethod
    def _from_json_obj(cls, json):
        return Anchor(text=json[u'text'], index=json[u'index'])


class Placement(ScriveObject):

    FONT_SIZE_SMALL = 12. / 943.
    FONT_SIZE_NORMAL = 16. / 943.
    FONT_SIZE_LARGE = 20. / 943.
    FONT_SIZE_HUGE = 24. / 943.

    @tvu(left=Ratio, top=Ratio, width=Ratio,
         height=Ratio, font_size=Ratio,
         page=tvu.tvus.PositiveInt, tip=MaybeTipSide)
    def __init__(self, left, top, width, height,
                 font_size=FONT_SIZE_NORMAL, page=1, tip=None):
        super(Placement, self).__init__()
        self._left = left
        self._top = top
        self._width = width
        self._height = height
        self._font_size = font_size
        self._page = page
        self._tip = tip
        self._anchors = ScriveSet()
        self._anchors._elem_validator = tvu.instance(Anchor)

    def _to_json_obj(self):
        return {u'xrel': self.left,
                u'yrel': self.top,
                u'wrel': self.width,
                u'hrel': self.height,
                u'fsrel': self.font_size,
                u'page': self.page,
                u'anchors': list(self.anchors),
                u'tip': self.tip.value if self.tip else None}

    def __str__(self):
        return u'Placement(page ' + str(self.page) + u',' + \
            str(self.left) + u':' + str(self.top) + u')'

    @classmethod
    def _from_json_obj(cls, json):
        anchors = [Anchor._from_json_obj(anchor_json)
                   for anchor_json in json[u'anchors']]
        placement = Placement(left=json[u'xrel'], top=json[u'yrel'],
                              width=json[u'wrel'], height=json[u'hrel'],
                              font_size=json[u'fsrel'], page=json[u'page'],
                              tip=TipSide(json[u'tip']))
        placement.anchors.update(anchors)
        return placement

    def _set_invalid(self):
        # invalidate anchors first, before getter stops working
        self.anchors._set_invalid()
        super(Placement, self)._set_invalid()

    def _set_read_only(self):
        super(Placement, self)._set_read_only()
        self.anchors._set_read_only()

    def _resolve_default_tip(self, default_tip_value):
        self._check_invalid()
        if self.tip is None:
            self.tip = default_tip_value

    left = scrive_descriptor(Ratio)
    top = scrive_descriptor(Ratio)
    width = scrive_descriptor(Ratio)
    height = scrive_descriptor(Ratio)
    font_size = scrive_descriptor(Ratio)
    page = scrive_descriptor(tvu.tvus.PositiveInt)
    tip = scrive_descriptor(MaybeTipSide)
    anchors = scrive_descriptor()
