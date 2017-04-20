# coding: utf-8
from scrivepy import Anchor, Placement, Tip

from tests.utils import TestCase, describe


class AnchorTest(TestCase):

    O = Anchor
    default_ctor_kwargs = {'text': 'foo', 'index': 2}
    json = {u'text': u'foo', u'index': 2}

    def test_text(self):
        self._test_non_empty_text('text')

    def test_index(self):
        self._test_int('index')


class PlacementTest(TestCase):

    O = Placement
    default_ctor_kwargs = {'left': .1, 'top': .2, 'width': .3, 'height': .4}
    json = {u'xrel': .1, u'yrel': .2, u'wrel': .3,
            u'hrel': .4, u'fsrel': .5, u'page': 1,
            u'tip': u'left', u'anchors': [{u'text': u'foo', u'index': 2}]}

    def make_anchor(self, num=1):
        return Anchor(text=u'foo' + str(num), index=num)

    def _test_ratio(self, attr_name, serialized_name):
        range_err = attr_name + r' must be in the <0,1> range \(inclusive\).*'
        self._test_attr(
            attr_name=attr_name,
            good_values=[(.0, .0), (.5, .5), (1., 1.),
                         (.001, .001), (0, 0.), (1, 1.)],
            bad_type_values=[([], u'float or int'),
                             (None, u'float or int')],
            bad_val_values=[(-1., range_err), (1.1, range_err),
                            (2, range_err), (-2, range_err)],
            serialized_name=serialized_name,
            serialized_values=[(0., 0.), (.5, .5), (1., 1.), (.001, .001)])

    def test_left(self):
        self._test_ratio('left', 'xrel')

    def test_top(self):
        self._test_ratio('top', 'yrel')

    def test_width(self):
        self._test_ratio('width', 'wrel')

    def test_height(self):
        self._test_ratio('height', 'hrel')

    def test_font_size(self):
        range_err = r'font_size must be in the <0,1> range \(inclusive\).*'
        self._test_attr(
            attr_name='font_size',
            good_values=[(.0, .0), (.5, .5), (1., 1.),
                         (.001, .001), (0, 0.), (1, 1.),
                         (Placement.FONT_SIZE_SMALL,
                          Placement.FONT_SIZE_SMALL),
                         (Placement.FONT_SIZE_NORMAL,
                          Placement.FONT_SIZE_NORMAL),
                         (Placement.FONT_SIZE_LARGE,
                          Placement.FONT_SIZE_LARGE),
                         (Placement.FONT_SIZE_HUGE,
                          Placement.FONT_SIZE_HUGE)],
            bad_type_values=[([], u'float or int'),
                             (None, u'float or int')],
            bad_val_values=[(-1., range_err), (1.1, range_err),
                            (2, range_err), (-2, range_err)],
            serialized_name='fsrel',
            serialized_values=[(0., 0.), (.5, .5), (1., 1.), (.001, .001)],
            default_value=Placement.FONT_SIZE_NORMAL,
            required=False)

    def test_page(self):
        self._test_positive_int('page', required=False, default_value=1)

    def test_tip(self):
        self._test_enum(Tip, 'tip', required=False, default_value=Tip.right)

        json = dict(self.json)
        json[u'tip'] = None
        with describe(self._deser_call(json) + '.tip == <Tip.left>'):
            o = self.O._from_json_obj(json)
            self.assertEqual(o.tip, Tip.left)
            self.assertEqual(type(o.tip), Tip)

    def test_anchors(self):
        self._test_set(Anchor, 'anchors', self.make_anchor)
