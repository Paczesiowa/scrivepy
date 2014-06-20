import enum

import type_value_unifier as tvu
from scrivepy import _object


class Ratio(tvu.TypeValueUnifier):

    TYPES = (float,)

    def validate(self, value):
        if not 0. <= value <= 1.:
            self.error(u'in the <0,1> range (inclusive)')


class PositiveInt(tvu.TypeValueUnifier):

    TYPES = (int,)

    def validate(self, value):
        if value < 1:
            self.error(u'a positive integer')


class TipSide(unicode, enum.Enum):
    left_tip = u'left'
    right_tip = u'right'


class MaybeTipSide(tvu.TypeValueUnifier):

    TYPES = (TipSide, type(None))


class FieldPlacement(_object.ScriveObject):

    FONT_SIZE_SMALL = 12. / 943.
    FONT_SIZE_NORMAL = 16. / 943.
    FONT_SIZE_LARGE = 20. / 943.
    FONT_SIZE_HUGE = 24. / 943.

    @tvu.validate_and_unify(left=Ratio, top=Ratio, width=Ratio,
                            height=Ratio, font_size=Ratio, page=PositiveInt,
                            tip=MaybeTipSide)
    def __init__(self, left, top, width, height,
                 font_size=FONT_SIZE_NORMAL, page=1, tip=None):
        super(FieldPlacement, self).__init__()
        self._json = {u'xrel': left,
                      u'yrel': top,
                      u'wrel': width,
                      u'hrel': height,
                      u'fsrel': font_size,
                      u'page': page,
                      u'tip': tip.value if tip else None}

    def _to_json_obj(self):
        return self._json

    def __str__(self):
        return u'Placement(page ' + str(self.page) + u',' + \
            str(self.left) + u':' + str(self.top) + u')'

    @classmethod
    def _from_json(cls, json):
        return FieldPlacement(left=json[u'xrel'], top=json[u'yrel'],
                              width=json[u'wrel'], height=json[u'hrel'],
                              font_size=json[u'fsrel'], page=json[u'page'],
                              tip=TipSide(json[u'tip']))

    def _resolve_default_tip(self, default_tip_value):
        self._check_invalid()
        if self.tip is None:
            self.tip = default_tip_value

    @property
    def left(self):
        self._check_getter()
        return self._json[u'xrel']

    @left.setter
    @tvu.validate_and_unify(left=Ratio)
    def left(self, left):
        self._check_setter()
        self._json[u'xrel'] = left

    @property
    def top(self):
        self._check_getter()
        return self._json[u'yrel']

    @top.setter
    @tvu.validate_and_unify(top=Ratio)
    def top(self, top):
        self._check_setter()
        self._json[u'yrel'] = top

    @property
    def width(self):
        self._check_getter()
        return self._json[u'wrel']

    @width.setter
    @tvu.validate_and_unify(width=Ratio)
    def width(self, width):
        self._check_setter()
        self._json[u'wrel'] = width

    @property
    def height(self):
        self._check_getter()
        return self._json[u'hrel']

    @height.setter
    @tvu.validate_and_unify(height=Ratio)
    def height(self, height):
        self._check_setter()
        self._json[u'hrel'] = height

    @property
    def font_size(self):
        self._check_getter()
        return self._json[u'fsrel']

    @font_size.setter
    @tvu.validate_and_unify(font_size=Ratio)
    def font_size(self, font_size):
        self._check_setter()
        self._json[u'fsrel'] = font_size

    @property
    def page(self):
        self._check_getter()
        return self._json[u'page']

    @page.setter
    @tvu.validate_and_unify(page=PositiveInt)
    def page(self, page):
        self._check_setter()
        self._json[u'page'] = page

    @property
    def tip(self):
        self._check_getter()
        tip = self._json[u'tip']
        if tip is not None:
            tip = TipSide(tip)
        return tip

    @tip.setter
    @tvu.validate_and_unify(tip=MaybeTipSide)
    def tip(self, tip):
        self._check_setter()
        self._json[u'tip'] = tip.value if tip else None
