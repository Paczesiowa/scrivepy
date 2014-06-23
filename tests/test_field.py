from scrivepy import _field_placement, _field, _exceptions
from tests import utils


FP = _field_placement.FieldPlacement
TS = _field_placement.TipSide
F = _field.Field


class FieldTest(utils.TestCase):

    def __init__(self, *args, **kwargs):
        super(FieldTest, self).__init__(*args, **kwargs)
        self.fp = FP(left=.5, top=.5, width=.5, height=.5)
        self.fp2 = FP(left=.7, top=.7, width=.7, height=.7)

    def test_value(self):
        with self.assertRaises(TypeError, u'value must be unicode, not 1'):
            F(value=1)

        # check default ctor value
        f = F()
        self.assertEqual(u'', f.value)

        f = F(value=u'foo')
        self.assertEqual(u'foo', f.value)

        with self.assertRaises(TypeError, u'value must be unicode, not 1'):
            f.value = 1

        f.value = u'bar'
        self.assertEqual(u'bar', f.value)

        self.assertEqual(u'bar', f._to_json_obj()[u'value'])

        f._set_read_only()
        self.assertEqual(u'bar', f.value)
        with self.assertRaises(_exceptions.ReadOnlyScriveObject, None):
            f.value = u'baz'

        f._set_invalid()
        with self.assertRaises(_exceptions.InvalidScriveObject, None):
            f.value
        with self.assertRaises(_exceptions.InvalidScriveObject, None):
            f.value = u'baz'

    def test_obligatory(self):
        with self.assertRaises(TypeError, u'obligatory must be bool, not 1'):
            F(obligatory=1)

        # check default ctor value
        f = F()
        self.assertTrue(f.obligatory)

        f = F(obligatory=False)
        self.assertFalse(f.obligatory)

        with self.assertRaises(TypeError, u'obligatory must be bool, not 1'):
            f.obligatory = 1

        f.obligatory = False
        self.assertFalse(f.obligatory)

        self.assertFalse(f._to_json_obj()[u'obligatory'])

        f._set_read_only()
        self.assertFalse(f.obligatory)
        with self.assertRaises(_exceptions.ReadOnlyScriveObject, None):
            f.obligatory = True

        f._set_invalid()
        with self.assertRaises(_exceptions.InvalidScriveObject, None):
            f.obligatory
        with self.assertRaises(_exceptions.InvalidScriveObject, None):
            f.obligatory = True

    def test_should_be_filled_by_sender(self):
        err_msg = u'should_be_filled_by_sender must be bool, not 1'
        with self.assertRaises(TypeError, err_msg):
            F(should_be_filled_by_sender=1)

        # check default ctor value
        f = F()
        self.assertFalse(f.should_be_filled_by_sender)

        f = F(should_be_filled_by_sender=False)
        self.assertFalse(f.should_be_filled_by_sender)

        with self.assertRaises(TypeError, err_msg):
            f.should_be_filled_by_sender = 1

        f.should_be_filled_by_sender = True
        self.assertTrue(f.should_be_filled_by_sender)

        self.assertTrue(f._to_json_obj()[u'shouldbefilledbysender'])

        f._set_read_only()
        self.assertTrue(f.should_be_filled_by_sender)
        with self.assertRaises(_exceptions.ReadOnlyScriveObject, None):
            f.should_be_filled_by_sender = False

        f._set_invalid()
        with self.assertRaises(_exceptions.InvalidScriveObject, None):
            f.should_be_filled_by_sender
        with self.assertRaises(_exceptions.InvalidScriveObject, None):
            f.should_be_filled_by_sender = False

    def test_placements(self):
        err_msg = u'placements must be set, not 1'
        with self.assertRaises(TypeError, err_msg):
            F(placements=1)

        err_msg = u'placements should be set of FieldPlacement objects, ' + \
            u'not: set([1])'
        with self.assertRaises(ValueError, err_msg):
            F(placements=set([1]))

        # check default ctor value
        f = F()
        self.assertEqual(set([]), set(f.placements()))

        f = F(placements=set([self.fp]))
        self.assertEqual(set([self.fp]), set(f.placements()))

        with self.assertRaises(TypeError, u'placements must be set, not 1'):
            f.set_placements(1)

        err_msg = u'placements should be set of FieldPlacement objects, ' + \
            u'not: set([1])'
        with self.assertRaises(ValueError, err_msg):
            f.set_placements(set([1]))

        f.set_placements(set([self.fp2]))
        self.assertEqual(set([self.fp2]), set(f.placements()))

        self.assertEqual([self.fp2], f._to_json_obj()[u'placements'])

        f._set_read_only()
        self.assertEqual(set([self.fp2]), set(f.placements()))
        with self.assertRaises(_exceptions.ReadOnlyScriveObject, None):
            f.set_placements(set([self.fp]))

        f._set_invalid()
        with self.assertRaises(_exceptions.InvalidScriveObject, None):
            f.placements()
        with self.assertRaises(_exceptions.InvalidScriveObject, None):
            f.set_placements(set([self.fp]))

    def test_default_placement_tip(self):
        f = F()
        self.assertEqual(TS.right_tip, f._default_placement_tip())

    def test_closed(self):
        f = F()
        self.assertIsNone(f.closed)

        f._set_read_only()
        self.assertIsNone(f.closed)

        f._set_invalid()
        with self.assertRaises(_exceptions.InvalidScriveObject, None):
            f.closed

    def test_flags(self):
        fp1 = FP(left=.5, top=.5, width=.5, height=.5)
        fp2 = FP(left=.7, top=.7, width=.7, height=.7)
        f = F(placements=set([fp1, fp2]))

        self.assertIsNone(f._check_getter())
        self.assertIsNone(fp1._check_getter())
        self.assertIsNone(fp2._check_getter())
        self.assertIsNone(f._check_setter())
        self.assertIsNone(fp1._check_setter())
        self.assertIsNone(fp2._check_setter())

        f._set_read_only()
        self.assertIsNone(f._check_getter())
        self.assertIsNone(fp1._check_getter())
        self.assertIsNone(fp2._check_getter())
        self.assertRaises(_exceptions.ReadOnlyScriveObject, None,
                          f._check_setter)
        self.assertRaises(_exceptions.ReadOnlyScriveObject, None,
                          fp1._check_setter)
        self.assertRaises(_exceptions.ReadOnlyScriveObject, None,
                          fp2._check_setter)

        f._set_invalid()
        self.assertRaises(_exceptions.InvalidScriveObject, None,
                          f._check_getter)
        self.assertRaises(_exceptions.InvalidScriveObject, None,
                          fp1._check_getter)
        self.assertRaises(_exceptions.InvalidScriveObject, None,
                          fp2._check_getter)
        self.assertRaises(_exceptions.InvalidScriveObject, None,
                          f._check_setter)
        self.assertRaises(_exceptions.InvalidScriveObject, None,
                          fp1._check_setter)
        self.assertRaises(_exceptions.InvalidScriveObject, None,
                          fp2._check_setter)

    def test_to_json_obj(self):
        fp = FP(left=.1, top=.2, width=.3, height=.4, font_size=.5,
                page=6, tip=None)

        f = F(value=u'foo', obligatory=False, should_be_filled_by_sender=True,
              placements=set([fp]))

        json = {u'value': u'foo',
                u'obligatory': False,
                u'shouldbefilledbysender': True,
                u'placements': [fp]}

        self.assertEqual(json, f._to_json_obj())
        self.assertEqual(fp.tip, TS.right_tip)

    def test_modification_of_default_placements_value(self):
        f1 = F()
        f1._json[u'placements'].add(1)
        f2 = F()
        self.assertEqual(set(), set(f2.placements()))
