from scrivepy import (
    InvalidScriveObject,
    Placement,
    ReadOnlyScriveObject,
    TipSide
)
from tests import utils


class PlacementTest(utils.TestCase):

    def _make_fp(self, **override_kwargs):
        kwargs = {'left': .5, 'top': .5, 'width': .5, 'height': .5}
        for key, val in override_kwargs.items():
            kwargs[key] = val
        return Placement(**kwargs)

    def test_left(self):
        with self.assertRaises(TypeError,
                               u'left must be float or int, not []'):
            self._make_fp(left=[])

        err_msg = u'left must be in the <0,1> range (inclusive), not: -0.1'
        with self.assertRaises(ValueError, err_msg):
            self._make_fp(left=-.1)

        err_msg = u'left must be in the <0,1> range (inclusive), not: 1.1'
        with self.assertRaises(ValueError, err_msg):
            self._make_fp(left=1.1)

        fp = self._make_fp(left=.7)
        self.assertEqual(.7, fp.left)

        fp = self._make_fp(left=0)
        self.assertEqual(0., fp.left)

        with self.assertRaises(TypeError,
                               u'left must be float or int, not []'):
            fp.left = []

        err_msg = u'left must be in the <0,1> range (inclusive), not: -0.1'
        with self.assertRaises(ValueError, err_msg):
            fp.left = -.1

        err_msg = u'left must be in the <0,1> range (inclusive), not: 1.1'
        with self.assertRaises(ValueError, err_msg):
            fp.left = 1.1

        fp.left = 1
        self.assertEqual(1., fp.left)

        fp.left = .8
        self.assertEqual(.8, fp.left)

        self.assertEqual(.8, fp._to_json_obj()[u'xrel'])

        fp._set_read_only()
        self.assertEqual(.8, fp.left)
        with self.assertRaises(ReadOnlyScriveObject, None):
            fp.left = .9

        fp._set_invalid()
        with self.assertRaises(InvalidScriveObject, None):
            fp.left
        with self.assertRaises(InvalidScriveObject, None):
            fp.left = .9

    def test_top(self):
        with self.assertRaises(TypeError,
                               u'top must be float or int, not []'):
            self._make_fp(top=[])

        err_msg = u'top must be in the <0,1> range (inclusive), not: -0.1'
        with self.assertRaises(ValueError, err_msg):
            self._make_fp(top=-.1)

        err_msg = u'top must be in the <0,1> range (inclusive), not: 1.1'
        with self.assertRaises(ValueError, err_msg):
            self._make_fp(top=1.1)

        fp = self._make_fp(top=.7)
        self.assertEqual(.7, fp.top)

        fp = self._make_fp(top=0)
        self.assertEqual(0., fp.top)

        with self.assertRaises(TypeError,
                               u'top must be float or int, not []'):
            fp.top = []

        err_msg = u'top must be in the <0,1> range (inclusive), not: -0.1'
        with self.assertRaises(ValueError, err_msg):
            fp.top = -.1

        err_msg = u'top must be in the <0,1> range (inclusive), not: 1.1'
        with self.assertRaises(ValueError, err_msg):
            fp.top = 1.1

        fp.top = 1
        self.assertEqual(1., fp.top)

        fp.top = .8
        self.assertEqual(.8, fp.top)

        self.assertEqual(.8, fp._to_json_obj()[u'yrel'])

        fp._set_read_only()
        self.assertEqual(.8, fp.top)
        with self.assertRaises(ReadOnlyScriveObject, None):
            fp.top = .9

        fp._set_invalid()
        with self.assertRaises(InvalidScriveObject, None):
            fp.top
        with self.assertRaises(InvalidScriveObject, None):
            fp.top = .9

    def test_width(self):
        with self.assertRaises(TypeError,
                               u'width must be float or int, not []'):
            self._make_fp(width=[])

        err_msg = u'width must be in the <0,1> range (inclusive), not: -0.1'
        with self.assertRaises(ValueError, err_msg):
            self._make_fp(width=-.1)

        err_msg = u'width must be in the <0,1> range (inclusive), not: 1.1'
        with self.assertRaises(ValueError, err_msg):
            self._make_fp(width=1.1)

        fp = self._make_fp(width=.7)
        self.assertEqual(.7, fp.width)

        fp = self._make_fp(width=0)
        self.assertEqual(0., fp.width)

        with self.assertRaises(TypeError,
                               u'width must be float or int, not []'):
            fp.width = []

        err_msg = u'width must be in the <0,1> range (inclusive), not: -0.1'
        with self.assertRaises(ValueError, err_msg):
            fp.width = -.1

        err_msg = u'width must be in the <0,1> range (inclusive), not: 1.1'
        with self.assertRaises(ValueError, err_msg):
            fp.width = 1.1

        fp.width = 1
        self.assertEqual(1., fp.width)

        fp.width = .8
        self.assertEqual(.8, fp.width)

        self.assertEqual(.8, fp._to_json_obj()[u'wrel'])

        fp._set_read_only()
        self.assertEqual(.8, fp.width)
        with self.assertRaises(ReadOnlyScriveObject, None):
            fp.width = .9

        fp._set_invalid()
        with self.assertRaises(InvalidScriveObject, None):
            fp.width
        with self.assertRaises(InvalidScriveObject, None):
            fp.width = .9

    def test_height(self):
        with self.assertRaises(TypeError,
                               u'height must be float or int, not []'):
            self._make_fp(height=[])

        err_msg = u'height must be in the <0,1> range (inclusive), not: -0.1'
        with self.assertRaises(ValueError, err_msg):
            self._make_fp(height=-.1)

        err_msg = u'height must be in the <0,1> range (inclusive), not: 1.1'
        with self.assertRaises(ValueError, err_msg):
            self._make_fp(height=1.1)

        fp = self._make_fp(height=.7)
        self.assertEqual(.7, fp.height)

        fp = self._make_fp(height=0)
        self.assertEqual(0., fp.height)

        with self.assertRaises(TypeError,
                               u'height must be float or int, not []'):
            fp.height = []

        err_msg = u'height must be in the <0,1> range (inclusive), not: -0.1'
        with self.assertRaises(ValueError, err_msg):
            fp.height = -.1

        err_msg = u'height must be in the <0,1> range (inclusive), not: 1.1'
        with self.assertRaises(ValueError, err_msg):
            fp.height = 1.1

        fp.height = 1
        self.assertEqual(1., fp.height)

        fp.height = .8
        self.assertEqual(.8, fp.height)

        self.assertEqual(.8, fp._to_json_obj()[u'hrel'])

        fp._set_read_only()
        self.assertEqual(.8, fp.height)
        with self.assertRaises(ReadOnlyScriveObject, None):
            fp.height = .9

        fp._set_invalid()
        with self.assertRaises(InvalidScriveObject, None):
            fp.height
        with self.assertRaises(InvalidScriveObject, None):
            fp.height = .9

    def test_font_size(self):
        with self.assertRaises(TypeError,
                               u'font_size must be float or int, not []'):
            self._make_fp(font_size=[])

        err_msg = \
            u'font_size must be in the <0,1> range (inclusive), not: -0.1'
        with self.assertRaises(ValueError, err_msg):
            self._make_fp(font_size=-.1)

        err_msg = \
            u'font_size must be in the <0,1> range (inclusive), not: 1.1'
        with self.assertRaises(ValueError, err_msg):
            self._make_fp(font_size=1.1)

        # check that pre-defined font sizes pass validation
        self._make_fp(font_size=Placement.FONT_SIZE_SMALL)
        self._make_fp(font_size=Placement.FONT_SIZE_NORMAL)
        self._make_fp(font_size=Placement.FONT_SIZE_LARGE)
        self._make_fp(font_size=Placement.FONT_SIZE_HUGE)

        # check default ctor value
        fp = self._make_fp()
        self.assertEqual(Placement.FONT_SIZE_NORMAL, fp.font_size)

        fp = self._make_fp(font_size=.7)
        self.assertEqual(.7, fp.font_size)

        fp = self._make_fp(font_size=0)
        self.assertEqual(0., fp.font_size)

        with self.assertRaises(TypeError,
                               u'font_size must be float or int, not []'):
            fp.font_size = []

        err_msg = \
            u'font_size must be in the <0,1> range (inclusive), not: -0.1'
        with self.assertRaises(ValueError, err_msg):
            fp.font_size = -.1

        err_msg = \
            u'font_size must be in the <0,1> range (inclusive), not: 1.1'
        with self.assertRaises(ValueError, err_msg):
            fp.font_size = 1.1

        # check that pre-defined font sizes pass validation
        fp.font_size = Placement.FONT_SIZE_SMALL
        fp.font_size = Placement.FONT_SIZE_NORMAL
        fp.font_size = Placement.FONT_SIZE_LARGE
        fp.font_size = Placement.FONT_SIZE_HUGE

        fp.font_size = 1
        self.assertEqual(1., fp.font_size)

        fp.font_size = .8
        self.assertEqual(.8, fp.font_size)

        self.assertEqual(.8, fp._to_json_obj()[u'fsrel'])

        fp._set_read_only()
        self.assertEqual(.8, fp.font_size)
        with self.assertRaises(ReadOnlyScriveObject, None):
            fp.font_size = .9

        fp._set_invalid()
        with self.assertRaises(InvalidScriveObject, None):
            fp.font_size
        with self.assertRaises(InvalidScriveObject, None):
            fp.font_size = .9

    def test_page(self):
        with self.assertRaises(TypeError,
                               u'page must be int or float, not []'):
            self._make_fp(page=[])

        err_msg = u'page must be an integer greater or equal to 1, not: 0'
        with self.assertRaises(ValueError, err_msg):
            self._make_fp(page=0)

        err_msg = u'page must be a round number, not: 1.1'
        with self.assertRaises(ValueError, err_msg):
            self._make_fp(page=1.1)

        # check default ctor value
        fp = self._make_fp()
        self.assertEqual(1, fp.page)

        fp = self._make_fp(page=8.)
        self.assertEqual(8, fp.page)

        fp = self._make_fp(page=2)
        self.assertEqual(2, fp.page)

        with self.assertRaises(TypeError,
                               u'page must be int or float, not []'):
            fp.page = []

        err_msg = u'page must be an integer greater or equal to 1, not: 0'
        with self.assertRaises(ValueError, err_msg):
            fp.page = 0

        err_msg = u'page must be a round number, not: 1.1'
        with self.assertRaises(ValueError, err_msg):
            fp.page = 1.1

        fp.page = 8.
        self.assertEqual(8, fp.page)

        fp.page = 3
        self.assertEqual(3, fp.page)

        self.assertEqual(3, fp._to_json_obj()[u'page'])

        fp._set_read_only()
        self.assertEqual(3, fp.page)
        with self.assertRaises(ReadOnlyScriveObject, None):
            fp.page = 4

        fp._set_invalid()
        with self.assertRaises(InvalidScriveObject, None):
            fp.page
        with self.assertRaises(InvalidScriveObject, None):
            fp.page = 4

    def test_tip(self):
        err_msg = u'tip must be TipSide or None, not {}'
        with self.assertRaises(TypeError, err_msg):
            self._make_fp(tip={})

        err_msg = u"tip could be None or TipSide's variant name, not: 'wrong'"
        with self.assertRaises(ValueError, err_msg):
            self._make_fp(tip='wrong')

        # check default ctor value
        fp = self._make_fp()
        self.assertIsNone(fp.tip)

        fp = self._make_fp(tip='right_tip')
        self.assertEqual(TipSide.right_tip, fp.tip)

        fp = self._make_fp(tip=TipSide.left_tip)
        self.assertEqual(TipSide.left_tip, fp.tip)

        err_msg = u'tip must be TipSide or None, not 0'
        with self.assertRaises(TypeError, err_msg):
            fp.tip = 0

        self.assertEqual(u'left', fp._to_json_obj()[u'tip'])

        fp.tip = None
        self.assertIsNone(fp.tip)
        self.assertIsNone(fp._to_json_obj()[u'tip'])

        fp.tip = TipSide.right_tip
        self.assertEqual(TipSide.right_tip, fp.tip)

        self.assertEqual(u'right', fp._to_json_obj()[u'tip'])

        fp._set_read_only()
        self.assertEqual(TipSide.right_tip, fp.tip)
        with self.assertRaises(ReadOnlyScriveObject, None):
            fp.tip = TipSide.left_tip

        fp._set_invalid()
        with self.assertRaises(InvalidScriveObject, None):
            fp.tip
        with self.assertRaises(InvalidScriveObject, None):
            fp.tip = TipSide.left_tip

    def test_resolve_default_tip(self):
        fp = self._make_fp()
        self.assertIsNone(fp.tip)

        fp._resolve_default_tip(TipSide.left_tip)
        self.assertEqual(TipSide.left_tip, fp.tip)

        fp._resolve_default_tip(TipSide.right_tip)
        self.assertEqual(TipSide.left_tip, fp.tip)

        fp = self._make_fp()
        fp._set_read_only()
        with self.assertRaises(ReadOnlyScriveObject, None):
            fp._resolve_default_tip(TipSide.left_tip)

        fp = self._make_fp()
        fp._set_invalid()
        with self.assertRaises(InvalidScriveObject, None):
            fp._resolve_default_tip(TipSide.left_tip)

    def test_from_json_obj(self):
        json1 = {u'xrel': 0.08589607635206786,
                 u'yrel': 0.2596232596232596,
                 u'wrel': 0.09013785790031813,
                 u'hrel': 0.02620802620802621,
                 u'fsrel': 0.016967126193001062,
                 u'page': 1,
                 u'tip': 'right'}
        fp = Placement._from_json_obj(json1)
        self.assertTrue(.08 < fp.left < .09)
        self.assertTrue(.25 < fp.top < .26)
        self.assertTrue(.09 < fp.width < .1)
        self.assertTrue(.02 < fp.height < .03)
        self.assertTrue(.01 < fp.font_size < .02)
        self.assertEqual(fp.page, 1)
        self.assertEqual(fp.tip, TipSide.right_tip)

        json2 = {u'xrel': 0.4188759278897137,
                 u'yrel': 0.31367731367731366,
                 u'wrel': 0.010604453870625663,
                 u'hrel': 0.00819000819000819,
                 u'fsrel': 0.015906680805938492,
                 u'page': 1,
                 u'tip': 'left'}
        fp = Placement._from_json_obj(json2)
        self.assertTrue(.41 < fp.left < .42)
        self.assertTrue(.31 < fp.top < .32)
        self.assertTrue(.01 < fp.width < .02)
        self.assertTrue(.0 < fp.height < .01)
        self.assertTrue(.01 < fp.font_size < .02)
        self.assertEqual(fp.page, 1)
        self.assertEqual(fp.tip, TipSide.left_tip)

    def test_to_json_obj(self):
        fp = Placement(left=.1, top=.2, width=.3, height=.4, font_size=.5,
                       page=6, tip=TipSide.left_tip)
        json = {u'xrel': .1,
                u'yrel': .2,
                u'wrel': .3,
                u'hrel': .4,
                u'fsrel': .5,
                u'page': 6,
                u'tip': u'left'}
        self.assertEqual(json, fp._to_json_obj())
