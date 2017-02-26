# coding: utf-8
from scrivepy import (
    CheckboxField,
    InvalidScriveObject,
    NameField,
    Placement,
    ReadOnlyScriveObject,
    SignatureField,
    StandardField,
    StandardFieldType,
    TextField
)

from scrivepy._set import ScriveSet

from tests import utils


class AbstractFieldTest(object):

    def p1(self):
        return Placement(left=.1, top=.2, width=.3, height=.4)

    def p2(self):
        return Placement(left=.5, top=.6, width=.7, height=.8)

    def test_obligatory(self):
        self._test_attr(
            attr_name='obligatory',
            good_values=[True, False],
            bad_type_values=[([], u'bool')],
            bad_val_values=[],
            serialized_name='is_obligatory',
            serialized_values=[True, False],
            default_value=True,
            required=False)

    def test_should_be_filled_by_sender(self):
        self._test_attr(
            attr_name='should_be_filled_by_sender',
            good_values=[True, False],
            bad_type_values=[([], u'bool')],
            bad_val_values=[],
            serialized_name='should_be_filled_by_sender',
            serialized_values=[True, False],
            default_value=False,
            required=False)

    # optional test
    def _test_value(self):
        unicode_err = u'value must be unicode text, or ascii-only bytestring'
        self._test_attr(
            attr_name='value',
            good_values=[u'foo', (b'bar', u'bar'), u'ą'],
            bad_type_values=[([], u'unicode or str')],
            bad_val_values=[(u'ą'.encode('utf-8'), unicode_err)],
            serialized_name='value',
            serialized_values=[u'foo', u'ą'],
            default_value=u'',
            required=False)

    # optional test
    def _test_name(self):
        unicode_err = u'name must be unicode text, or ascii-only bytestring'
        self._test_attr(
            attr_name='name',
            good_values=[u'foo', (b'bar', u'bar'), u'ą'],
            bad_type_values=[([], u'unicode or str')],
            bad_val_values=[(u'ą'.encode('utf-8'), unicode_err),
                            (u'', u'name must be non-empty string')],
            serialized_name='name',
            serialized_values=[u'foo', u'ą'],
            required=True)

    def test_placements(self):
        # check default ctor value
        f = self.o()
        self.assertEqual(ScriveSet(), f.placements)

        p1 = self.p1()
        f.placements.add(p1)
        self.assertEqual(ScriveSet([p1]), f.placements)

        err_msg = u'elem must be Placement, not 1'
        with self.assertRaises(TypeError, err_msg):
            f.placements.add(1)

        f.placements.clear()
        p2 = self.p2()
        f.placements.add(p2)
        self.assertEqual(ScriveSet([p2]), f.placements)

        self.assertEqual([p2], f._to_json_obj()[u'placements'])

        f._set_read_only()
        # set() is because the 2nd one is read only and not really equal
        self.assertEqual(set(ScriveSet([p2])), set(f.placements))
        with self.assertRaises(ReadOnlyScriveObject, None):
            f.placements.clear()

        placements = f.placements
        f._set_invalid()
        with self.assertRaises(InvalidScriveObject, None):
            f.placements
        with self.assertRaises(InvalidScriveObject, None):
            placements.add(p1)


class NameFieldTest(AbstractFieldTest, utils.TestCase):

    O = NameField
    default_ctor_kwargs = {'value': u'', 'obligatory': True,
                           'order': 1, 'should_be_filled_by_sender': False}
    json = {u'type': u'name', u'is_obligatory': True, u'placements': [],
            u'order': 1, u'value': u'', u'should_be_filled_by_sender': False}

    def test_type(self):
        self._test_ctor_param('type', default_value=u'name')
        o = self.o()
        self.assertEqual(o._to_json_obj()[u'type'], u'name')

    def test_value(self):
        self._test_value()

    def test_order(self):
        self._test_attr(
            attr_name='order',
            good_values=[1, 2, 100, (1., 1)],
            bad_type_values=[([], u'int or float')],
            bad_val_values=[(0, r'.*integer greater or equal to 1.*'),
                            (1.1, r'.*round number.*')],
            serialized_name='order',
            serialized_values=[1, 2, 3, 100, (2., 2)],
            default_value=1,
            sealed_attr=True,
            required=False)


class StandardFieldTest(AbstractFieldTest, utils.TestCase):

    O = StandardField
    default_ctor_kwargs = {'value': u'', 'obligatory': True, 'type_': 'mobile',
                           'should_be_filled_by_sender': False}
    json = {u'type': u'email', u'is_obligatory': True, u'placements': [],
            u'value': u'', u'should_be_filled_by_sender': False}

    def test_type(self):
        ctor_params = [('email', StandardFieldType.email),
                       ('mobile', StandardFieldType.mobile),
                       ('personal_number', StandardFieldType.personal_number),
                       ('company_number', StandardFieldType.company_number)]
        ctor_params += list(StandardFieldType)
        serialized_values = [('email', u'email'),
                             ('mobile', u'mobile'),
                             ('personal_number', u'personal_number'),
                             ('company_number', u'company_number')]
        self._test_ctor_param('type', ctor_attr_name='type_',
                              ctor_params=ctor_params,
                              serialized_name='type',
                              serialized_values=serialized_values)

    def test_value(self):
        self._test_value()


class TextFieldTest(AbstractFieldTest, utils.TestCase):

    O = TextField
    default_ctor_kwargs = {'value': u'', 'obligatory': True,
                           'name': u'field1',
                           'should_be_filled_by_sender': False}
    json = {u'type': u'text', u'is_obligatory': True, u'placements': [],
            u'name': u'field1', u'value': u'',
            u'should_be_filled_by_sender': False}

    def test_type(self):
        self._test_ctor_param('type', default_value=u'text')
        o = self.o()
        self.assertEqual(o._to_json_obj()[u'type'], u'text')

    def test_value(self):
        self._test_value()

    def test_name(self):
        self._test_name()


class SignatureFieldTest(AbstractFieldTest, utils.TestCase):

    O = SignatureField
    default_ctor_kwargs = {'obligatory': True, 'name': u'sig1'}
    json = {u'type': u'signature', u'is_obligatory': True,
            u'placements': [], u'name': u'sig1', u'signature': None}

    def test_should_be_filled_by_sender(self):
        self._test_ctor_param('should_be_filled_by_sender',
                              default_value=False)
        o = self.o()
        self.assertFalse(u'should_be_filled_by_sender' in o._to_json_obj())

    def test_type(self):
        self._test_ctor_param('type', default_value=u'signature')
        o = self.o()
        self.assertEqual(o._to_json_obj()[u'type'], u'signature')

    def test_name(self):
        self._test_name()


class CheckboxFieldTest(AbstractFieldTest, utils.TestCase):

    O = CheckboxField
    default_ctor_kwargs = {'checked': False, 'obligatory': True,
                           'name': u'checkbox1',
                           'should_be_filled_by_sender': False}
    json = {u'type': u'checkbox', u'is_obligatory': True, u'placements': [],
            u'name': u'checkbox1', u'is_checked': False,
            u'should_be_filled_by_sender': False}

    def test_type(self):
        self._test_ctor_param('type', default_value=u'checkbox')
        o = self.o()
        self.assertEqual(o._to_json_obj()[u'type'], u'checkbox')

    def test_name(self):
        self._test_name()

    def test_checked(self):
        self._test_attr(
            attr_name='checked',
            good_values=[True, False],
            bad_type_values=[([], u'bool')],
            bad_val_values=[],
            serialized_name='is_checked',
            serialized_values=[True, False],
            default_value=False,
            required=False)
