# coding: utf-8
from scrivepy import (
    Anchor,
    InvalidScriveObject,
    Placement,
    ReadOnlyScriveObject,
    TipSide
)
from scrivepy._set import ScriveSet
from tests import utils


class AnchorTest(utils.TestCase):

    O = Anchor
    default_ctor_kwargs = {'text': 'foo', 'index': 2}
    json = {u'text': u'foo', u'index': 2}

    def test_text(self):
        unicode_err = u'text must be unicode text, or ascii-only bytestring'
        self._test_attr(
            attr_name='text',
            good_values=[u'foo', (b'bar', u'bar'), u'ą'],
            bad_type_values=[([], u'unicode or str')],
            bad_val_values=[(u'ą'.encode('utf-8'), unicode_err),
                            (u'', u'text must be non-empty string')],
            serialized_name='text',
            serialized_values=[u'foo', u'ą'],
            required=True)

    def test_index(self):
        self._test_attr(
            attr_name='index',
            good_values=[1, 2, -1],
            bad_type_values=[([], u'int')],
            bad_val_values=[],
            serialized_name='index',
            serialized_values=[1, 2, -1],
            required=True)


class PlacementTest(utils.TestCase):

    O = Placement
    default_ctor_kwargs = {'left': .1, 'top': .2, 'width': .3, 'height': .4}
    json = {u'xrel': .1, u'yrel': .2, u'wrel': .3,
            u'hrel': .4, u'fsrel': .5, u'page': 1,
            u'tip': u'left', u'anchors': [{u'text': u'foo', u'index': 2}]}
    a1 = Anchor(text=u'foo', index=1)
    a2 = Anchor(text=u'bar', index=2)

    def test_left(self):
        range_err = r'left must be in the <0,1> range \(inclusive\).*'
        self._test_attr(
            attr_name='left',
            good_values=[.0, .5, 1., .001, (0, 0.), (1, 1.)],
            bad_type_values=[([], u'float or int')],
            bad_val_values=[(-1., range_err), (1.1, range_err)],
            serialized_name='xrel',
            serialized_values=[(0, 0.), .0, .1, 1., (1, 1.), .5],
            required=True)

    def test_top(self):
        range_err = r'top must be in the <0,1> range \(inclusive\).*'
        self._test_attr(
            attr_name='top',
            good_values=[.0, .5, 1., .001, (0, 0.), (1, 1.)],
            bad_type_values=[([], u'float or int')],
            bad_val_values=[(-1., range_err), (1.1, range_err)],
            serialized_name='yrel',
            serialized_values=[(0, .0), .0, .1, 1., (1, 1.), .5],
            required=True)

    def test_width(self):
        range_err = r'width must be in the <0,1> range \(inclusive\).*'
        self._test_attr(
            attr_name='width',
            good_values=[.0, .5, 1., .001, (0, 0.), (1, 1.)],
            bad_type_values=[([], u'float or int')],
            bad_val_values=[(-1., range_err), (1.1, range_err)],
            serialized_name='wrel',
            serialized_values=[(0, .0), .0, .1, 1., (1, 1.), .5],
            required=True)

    def test_height(self):
        range_err = r'height must be in the <0,1> range \(inclusive\).*'
        self._test_attr(
            attr_name='height',
            good_values=[.0, .5, 1., .001, (0, 0.), (1, 1.)],
            bad_type_values=[([], u'float or int')],
            bad_val_values=[(-1., range_err), (1.1, range_err)],
            serialized_name='hrel',
            serialized_values=[(0, .0), .0, .1, 1., (1, 1.), .5],
            required=True)

    def test_font_size(self):
        range_err = r'font_size must be in the <0,1> range \(inclusive\).*'
        self._test_attr(
            attr_name='font_size',
            good_values=[.0, .5, 1., .001, (0, 0.), (1, 1.),
                         Placement.FONT_SIZE_SMALL, Placement.FONT_SIZE_NORMAL,
                         Placement.FONT_SIZE_LARGE, Placement.FONT_SIZE_HUGE],
            bad_type_values=[([], u'float or int')],
            bad_val_values=[(-1., range_err), (1.1, range_err)],
            serialized_name='fsrel',
            serialized_values=[(0, .0), .0, .1, 1., (1, 1.), .5],
            default_value=Placement.FONT_SIZE_NORMAL,
            required=False)

    def test_page(self):
        self._test_attr(
            attr_name='page',
            good_values=[1, 2, 100, (1., 1)],
            bad_type_values=[([], u'int or float')],
            bad_val_values=[(0, r'.*integer greater or equal to 1.*'),
                            (1.1, r'.*round number.*')],
            serialized_name='page',
            serialized_values=[1, 2, 3, 100, (2., 2)],
            default_value=1,
            required=False)

    def test_tip(self):
        self._test_attr(
            attr_name='tip',
            good_values=[('left', TipSide.left), ('right', TipSide.right),
                         TipSide.left, TipSide.right],
            bad_type_values=[({}, u'TipSide'), (0, u'TipSide')],
            bad_val_values=[('wrong', r".*could be TipSide's variant name.*")],
            serialized_name='tip',
            serialized_values=[('left', u'left'), (TipSide.left, u'left'),
                               ('right', u'right'), (TipSide.right, u'right')],
            default_value=TipSide.right,
            required=False)

        json = dict(self.json)
        json[u'tip'] = None
        p = self.O._from_json_obj(json)
        self.assertEqual(p.tip, TipSide.left)

    def test_from_json_obj(self):
        json1 = {u'xrel': 0.08589607635206786,
                 u'yrel': 0.2596232596232596,
                 u'wrel': 0.09013785790031813,
                 u'hrel': 0.02620802620802621,
                 u'fsrel': 0.016967126193001062,
                 u'page': 1,
                 u'anchors': [],
                 u'tip': u'right'}
        fp = Placement._from_json_obj(json1)
        self.assertTrue(.08 < fp.left < .09)
        self.assertTrue(.25 < fp.top < .26)
        self.assertTrue(.09 < fp.width < .1)
        self.assertTrue(.02 < fp.height < .03)
        self.assertTrue(.01 < fp.font_size < .02)
        self.assertEqual(fp.page, 1)
        self.assertEqual(fp.tip, TipSide.right)

        json2 = {u'xrel': 0.4188759278897137,
                 u'yrel': 0.31367731367731366,
                 u'wrel': 0.010604453870625663,
                 u'hrel': 0.00819000819000819,
                 u'fsrel': 0.015906680805938492,
                 u'page': 1,
                 u'anchors': [],
                 u'tip': None}
        fp = Placement._from_json_obj(json2)
        self.assertTrue(.41 < fp.left < .42)
        self.assertTrue(.31 < fp.top < .32)
        self.assertTrue(.01 < fp.width < .02)
        self.assertTrue(.0 < fp.height < .01)
        self.assertTrue(.01 < fp.font_size < .02)
        self.assertEqual(fp.page, 1)
        self.assertEqual(fp.tip, TipSide.left)

    def test_to_json_obj(self):
        fp = Placement(left=.1, top=.2, width=.3, height=.4, font_size=.5,
                       page=6, tip=TipSide.left)
        json = {u'xrel': .1,
                u'yrel': .2,
                u'wrel': .3,
                u'hrel': .4,
                u'fsrel': .5,
                u'page': 6,
                u'anchors': [],
                u'tip': u'left'}
        self.assertEqual(json, fp._to_json_obj())

    def test_anchors(self):
        # check default ctor value
        p = self.o()
        self.assertEqual(ScriveSet(), p.anchors)

        p.anchors.add(self.a1)
        self.assertEqual(ScriveSet([self.a1]), p.anchors)

        err_msg = u'elem must be Anchor, not 1'
        with self.assertRaises(TypeError, err_msg):
            p.anchors.add(1)

        p.anchors.clear()
        p.anchors.add(self.a2)
        self.assertEqual(ScriveSet([self.a2]), p.anchors)

        self.assertEqual([self.a2], p._to_json_obj()[u'anchors'])

        p._set_read_only()
        # set() is because the 2nd one is read only and not really equal
        self.assertEqual(set(ScriveSet([self.a2])), set(p.anchors))
        with self.assertRaises(ReadOnlyScriveObject, None):
            p.anchors.clear()

        anchors = p.anchors
        p._set_invalid()
        with self.assertRaises(InvalidScriveObject, None):
            p.anchors
        with self.assertRaises(InvalidScriveObject, None):
            anchors.add(self.a1)
