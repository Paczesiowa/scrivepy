from scrivepy import (
    CheckboxField as ChF,
    CustomField as CF,
    Field as F,
    InvalidScriveObject,
    Placement,
    ReadOnlyScriveObject,
    SignatureField as SigF,
    StandardField as SF,
    StandardFieldType as SFT,
    TipSide,
    _set
)
from tests import utils


ScriveSet = _set.ScriveSet


class FieldTest(object):

    def setUp(self):
        self.fp = Placement(left=.5, top=.5, width=.5,
                            height=.5, tip=TipSide.right)
        self.fp2 = Placement(left=.7, top=.7, width=.7,
                             height=.7, tip=TipSide.right)

    def f(self, *args, **kwargs):
        return F(*args, **kwargs)

    def test_value(self):
        with self.assertRaises(TypeError,
                               u'value must be unicode or str, not 1'):
            self.f(value=1)

        # check default ctor value
        f = self.f()
        self.assertEqual(u'', f.value)

        f = self.f(value=u'foo')
        self.assertEqual(u'foo', f.value)

        with self.assertRaises(TypeError,
                               u'value must be unicode or str, not 1'):
            f.value = 1

        f.value = u'bar'
        self.assertEqual(u'bar', f.value)

        self.assertEqual(u'bar', f._to_json_obj()[u'value'])

        f._set_read_only()
        self.assertEqual(u'bar', f.value)
        with self.assertRaises(ReadOnlyScriveObject, None):
            f.value = u'baz'

        f._set_invalid()
        with self.assertRaises(InvalidScriveObject, None):
            f.value
        with self.assertRaises(InvalidScriveObject, None):
            f.value = u'baz'

    def test_obligatory_default(self):
        f = self.f()
        self.assertTrue(f.obligatory)

    def test_obligatory(self):
        with self.assertRaises(TypeError, u'obligatory must be bool, not 1'):
            self.f(obligatory=1)

        f = self.f(obligatory=False)
        self.assertFalse(f.obligatory)

        with self.assertRaises(TypeError, u'obligatory must be bool, not 1'):
            f.obligatory = 1

        f.obligatory = False
        self.assertFalse(f.obligatory)

        self.assertFalse(f._to_json_obj()[u'obligatory'])

        f._set_read_only()
        self.assertFalse(f.obligatory)
        with self.assertRaises(ReadOnlyScriveObject, None):
            f.obligatory = True

        f._set_invalid()
        with self.assertRaises(InvalidScriveObject, None):
            f.obligatory
        with self.assertRaises(InvalidScriveObject, None):
            f.obligatory = True

    def test_should_be_filled_by_sender(self):
        err_msg = u'should_be_filled_by_sender must be bool, not 1'
        with self.assertRaises(TypeError, err_msg):
            self.f(should_be_filled_by_sender=1)

        # check default ctor value
        f = self.f()
        self.assertFalse(f.should_be_filled_by_sender)

        f = self.f(should_be_filled_by_sender=False)
        self.assertFalse(f.should_be_filled_by_sender)

        with self.assertRaises(TypeError, err_msg):
            f.should_be_filled_by_sender = 1

        f.should_be_filled_by_sender = True
        self.assertTrue(f.should_be_filled_by_sender)

        self.assertTrue(f._to_json_obj()[u'shouldbefilledbysender'])

        f._set_read_only()
        self.assertTrue(f.should_be_filled_by_sender)
        with self.assertRaises(ReadOnlyScriveObject, None):
            f.should_be_filled_by_sender = False

        f._set_invalid()
        with self.assertRaises(InvalidScriveObject, None):
            f.should_be_filled_by_sender
        with self.assertRaises(InvalidScriveObject, None):
            f.should_be_filled_by_sender = False

    def test_placements(self):
        # check default ctor value
        f = self.f()
        self.assertEqual(ScriveSet(), f.placements)

        f.placements.add(self.fp)
        self.assertEqual(ScriveSet([self.fp]), f.placements)

        err_msg = u'elem must be Placement, not 1'
        with self.assertRaises(TypeError, err_msg):
            f.placements.add(1)

        f.placements.clear()
        f.placements.add(self.fp2)
        self.assertEqual(ScriveSet([self.fp2]), f.placements)

        self.assertEqual([self.fp2], f._to_json_obj()[u'placements'])

        f._set_read_only()
        # set() is because the 2nd one is read only and not really equal
        self.assertEqual(set(ScriveSet([self.fp2])), set(f.placements))
        with self.assertRaises(ReadOnlyScriveObject, None):
            f.placements.clear()
            f.placements.add(self.fp)

        plcmts = f.placements
        f._set_invalid()
        with self.assertRaises(InvalidScriveObject, None):
            f.placements
        with self.assertRaises(InvalidScriveObject, None):
            plcmts.add(self.fp)

    def test_closed(self):
        f = self.f()
        self.assertIsNone(f.closed)

        f._set_read_only()
        self.assertIsNone(f.closed)

        f._set_invalid()
        with self.assertRaises(InvalidScriveObject, None):
            f.closed

    def test_flags(self):
        fp1 = Placement(left=.5, top=.5, width=.5, height=.5)
        fp2 = Placement(left=.7, top=.7, width=.7, height=.7)
        f = self.f()
        f.placements.update([fp1, fp2])

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
        self.assertRaises(ReadOnlyScriveObject, None,
                          f._check_setter)
        self.assertRaises(ReadOnlyScriveObject, None,
                          fp1._check_setter)
        self.assertRaises(ReadOnlyScriveObject, None,
                          fp2._check_setter)

        f._set_invalid()
        self.assertRaises(InvalidScriveObject, None,
                          f._check_getter)
        self.assertRaises(InvalidScriveObject, None,
                          fp1._check_getter)
        self.assertRaises(InvalidScriveObject, None,
                          fp2._check_getter)
        self.assertRaises(InvalidScriveObject, None,
                          f._check_setter)
        self.assertRaises(InvalidScriveObject, None,
                          fp1._check_setter)
        self.assertRaises(InvalidScriveObject, None,
                          fp2._check_setter)


class StandardFieldTest(FieldTest):

    def f(self, *args, **kwargs):
        return SF(name=self.FIELD_NAME, *args, **kwargs)

    def test_to_json_obj(self):
        fp = Placement(left=.1, top=.2, width=.3, height=.4,
                       font_size=.5, page=6, tip='right')

        f = self.f(value=u'foo', obligatory=False,
                   should_be_filled_by_sender=True)
        f.placements.add(fp)

        json = {u'value': u'foo',
                u'obligatory': False,
                u'shouldbefilledbysender': True,
                u'placements': [fp],
                u'type': u'standard',
                u'name': self.FIELD_NAME}

        self.assertEqual(json, f._to_json_obj())
        self.assertEqual(fp.tip, TipSide.right)

    def test_from_json_obj(self):
        json = {u'type': u'standard',
                u'name': self.FIELD_NAME.value,
                u'value': u'bar',
                u'closed': False,
                u'obligatory': True,
                u'shouldbefilledbysender': False,
                u'placements': [self.fp._to_json_obj(),
                                self.fp2._to_json_obj()]}
        f = F._from_json_obj(json)
        self.assertEqual(f.type, u'standard')
        self.assertEqual(f.name, self.FIELD_NAME.value)
        self.assertEqual(f.value, u'bar')
        self.assertFalse(f.closed)
        self.assertTrue(f.obligatory)
        self.assertFalse(f.should_be_filled_by_sender)

        self.assertEqual(sorted([fp._to_json_obj()
                                 for fp in f.placements]),
                         sorted([self.fp._to_json_obj(),
                                 self.fp2._to_json_obj()]))

    def test_type(self):
        f = self.f()
        self.assertEqual(f.type, u'standard')
        with self.assertRaises(AttributeError, u"can't set attribute"):
            f.type = u'custom'

    def test_name(self):
        f = self.f()
        self.assertEqual(f.name, self.FIELD_NAME)
        self.assertTrue(isinstance(f.name, SFT))
        with self.assertRaises(AttributeError, u"can't set attribute"):
            f.name = u'quux'

        f = SF(name=self.FIELD_NAME.name)
        self.assertTrue(isinstance(f.name, SFT))
        self.assertEqual(f.name, self.FIELD_NAME)

        err_msg = \
            u"name could be StandardFieldType's variant name, not: 'wrong'"
        with self.assertRaises(ValueError, err_msg):
            SF(name='wrong')


class FirstNameFieldTest(StandardFieldTest, utils.TestCase):

    FIELD_NAME = SFT.first_name


class LastNameFieldTest(StandardFieldTest, utils.TestCase):

    FIELD_NAME = SFT.last_name


class EmailFieldTest(StandardFieldTest, utils.TestCase):

    FIELD_NAME = SFT.email


class MobileNumberFieldTest(StandardFieldTest, utils.TestCase):

    FIELD_NAME = SFT.mobile


class PersonalNumberFieldTest(StandardFieldTest, utils.TestCase):

    FIELD_NAME = SFT.personal_number


class CompanyNameFieldTest(StandardFieldTest, utils.TestCase):

    FIELD_NAME = SFT.company_name


class CompanyNumberFieldTest(StandardFieldTest, utils.TestCase):

    FIELD_NAME = SFT.company_number


class CustomFieldTest(FieldTest, utils.TestCase):

    def f(self, *args, **kwargs):
        if u'name' not in kwargs:
            kwargs[u'name'] = u'fieldname'
        return CF(*args, **kwargs)

    def test_to_json_obj(self):
        fp = Placement(left=.1, top=.2, width=.3, height=.4,
                       font_size=.5, page=6, tip='right')

        f = self.f(name=u'fieldname', value=u'fieldvalue', obligatory=False,
                   should_be_filled_by_sender=True)
        f.placements.add(fp)

        json = {u'value': u'fieldvalue',
                u'obligatory': False,
                u'shouldbefilledbysender': True,
                u'placements': [fp],
                u'type': u'custom',
                u'name': u'fieldname'}

        self.assertEqual(json, f._to_json_obj())
        self.assertEqual(fp.tip, TipSide.right)

    def test_from_json_obj(self):
        json = {u'type': u'custom',
                u'name': u'fieldname',
                u'value': u'fieldvalue',
                u'closed': False,
                u'obligatory': True,
                u'shouldbefilledbysender': False,
                u'placements': [self.fp._to_json_obj(),
                                self.fp2._to_json_obj()]}
        f = F._from_json_obj(json)
        self.assertTrue(isinstance(f, CF))
        self.assertEqual(f.value, u'fieldvalue')
        self.assertFalse(f.closed)
        self.assertTrue(f.obligatory)
        self.assertFalse(f.should_be_filled_by_sender)

        self.assertEqual(sorted([fp._to_json_obj()
                                 for fp in f.placements]),
                         sorted([self.fp._to_json_obj(),
                                 self.fp2._to_json_obj()]))

    def test_type(self):
        f = self.f()
        self.assertEqual(f.type, u'custom')
        with self.assertRaises(AttributeError, u"can't set attribute"):
            f.type = u'standard'

    def test_name(self):
        f = self.f(name=u'fieldname')
        self.assertEqual(f.name, u'fieldname')
        f.name = u'quux'
        self.assertEqual(f.name, u'quux')


class SignatureFieldTest(FieldTest, utils.TestCase):

    def f(self, *args, **kwargs):
        if u'name' not in kwargs:
            kwargs[u'name'] = u'signature-1'
        return SigF(*args, **kwargs)

    def test_value(self):
        with self.assertRaises(TypeError):  # unexpected argument
            self.f(value=1)

        f = self.f()
        self.assertEqual(u'', f.value)

        with self.assertRaises(AttributeError, u"can't set attribute"):
            f.value = 1

        f._set_read_only()
        self.assertEqual(u'', f.value)

        f._set_invalid()
        with self.assertRaises(InvalidScriveObject, None):
            f.value

    def test_to_json_obj(self):
        fp = Placement(left=.1, top=.2, width=.3, height=.4,
                       font_size=.5, page=6, tip='left')

        f = self.f(name=u'signature-2', obligatory=False,
                   should_be_filled_by_sender=True)
        f.placements.add(fp)

        json = {u'value': u'',
                u'obligatory': False,
                u'shouldbefilledbysender': True,
                u'placements': [fp],
                u'type': u'signature',
                u'name': u'signature-2'}

        self.assertEqual(json, f._to_json_obj())
        self.assertEqual(fp.tip, TipSide.left)

    def test_from_json_obj(self):
        json = {u'type': u'signature',
                u'name': u'signature-3',
                u'value': u'somejpegdata',
                u'closed': True,
                u'obligatory': True,
                u'shouldbefilledbysender': False,
                u'placements': [self.fp._to_json_obj(),
                                self.fp2._to_json_obj()]}
        f = F._from_json_obj(json)
        self.assertTrue(isinstance(f, SigF))
        self.assertEqual(f.value, u'somejpegdata')
        self.assertTrue(f.closed)
        self.assertTrue(f.obligatory)
        self.assertFalse(f.should_be_filled_by_sender)

        self.assertEqual(sorted([fp._to_json_obj()
                                 for fp in f.placements]),
                         sorted([self.fp._to_json_obj(),
                                 self.fp2._to_json_obj()]))

    def test_type(self):
        f = self.f()
        self.assertEqual(f.type, u'signature')
        with self.assertRaises(AttributeError, u"can't set attribute"):
            f.type = u'standard'

    def test_name(self):
        f = self.f(name=u'signature-1')
        self.assertEqual(f.name, u'signature-1')
        f.name = u'signature-2'
        self.assertEqual(f.name, u'signature-2')


class CheckboxFieldTest(FieldTest, utils.TestCase):

    def f(self, *args, **kwargs):
        if u'name' not in kwargs:
            kwargs[u'name'] = u'checkbox-1'
        return ChF(*args, **kwargs)

    def test_value(self):
        with self.assertRaises(TypeError, u'value must be bool, not 1'):
            self.f(value=1)

        # check default ctor value
        f = self.f()
        self.assertFalse(f.value)

        f = self.f(value=True)
        self.assertTrue(f.value)

        with self.assertRaises(TypeError, u'value must be bool, not 1'):
            f.value = 1

        f.value = False
        self.assertFalse(f.value)

        self.assertFalse(f._to_json_obj()[u'value'])

        f._set_read_only()
        self.assertFalse(f.value)
        with self.assertRaises(ReadOnlyScriveObject, None):
            f.value = True

        f._set_invalid()
        with self.assertRaises(InvalidScriveObject, None):
            f.value
        with self.assertRaises(InvalidScriveObject, None):
            f.value = True

    def test_obligatory_default(self):
        f = self.f()
        self.assertFalse(f.obligatory)

    def test_to_json_obj(self):
        fp = Placement(left=.1, top=.2, width=.3, height=.4,
                       font_size=.5, page=6, tip='right')

        f = self.f(name=u'checkbox-2', obligatory=False,
                   should_be_filled_by_sender=True)
        f.placements.add(fp)

        json = {u'value': u'',
                u'obligatory': False,
                u'shouldbefilledbysender': True,
                u'placements': [fp],
                u'type': u'checkbox',
                u'name': u'checkbox-2'}

        self.assertEqual(json, f._to_json_obj())
        self.assertEqual(fp.tip, TipSide.right)

    def test_from_json_obj(self):
        json = {u'type': u'checkbox',
                u'name': u'checkbox-3',
                u'value': u'',
                u'closed': True,
                u'obligatory': True,
                u'shouldbefilledbysender': False,
                u'placements': [self.fp._to_json_obj(),
                                self.fp2._to_json_obj()]}
        f = F._from_json_obj(json)
        self.assertTrue(isinstance(f, ChF))
        self.assertFalse(f.value)
        self.assertTrue(f.closed)
        self.assertTrue(f.obligatory)
        self.assertFalse(f.should_be_filled_by_sender)

        self.assertEqual(sorted([fp._to_json_obj()
                                 for fp in f.placements]),
                         sorted([self.fp._to_json_obj(),
                                 self.fp2._to_json_obj()]))

    def test_type(self):
        f = self.f()
        self.assertEqual(f.type, u'checkbox')
        with self.assertRaises(AttributeError, u"can't set attribute"):
            f.type = u'standard'

    def test_name(self):
        f = self.f(name=u'checkbox-1')
        self.assertEqual(f.name, u'checkbox-1')
        f.name = u'checkbox-2'
        self.assertEqual(f.name, u'checkbox-2')
