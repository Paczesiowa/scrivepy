# coding: utf-8
from scrivepy import (
    CheckboxField,
    NameField,
    Placement,
    SignatureField,
    StandardField,
    StandardFieldType,
    TextField
)
from scrivepy._field import Field

from tests.utils import describe, TestCase


class AbstractFieldTest(object):

    def make_placement(self, num=1):
        return Placement(left=(num * .01), top=(num * .2),
                         width=(num * .3), height=(num * .4))

    def test_obligatory(self):
        self._test_bool('obligatory', required=False, default_value=True,
                        serialized_name=u'is_obligatory')

    def test_placements(self):
        self._test_set(Placement, 'placements', self.make_placement)

    def test_should_be_filled_by_sender(self):
        self._test_bool('should_be_filled_by_sender', required=False,
                        default_value=False)

    def _test_const_type(self, val):
        possible_types = (u'checkbox|text|signature|name|email' +
                          u'|mobile|personal_number|company_number')
        self._test_attr(attr_name='type',
                        good_values=[],
                        bad_type_values=[(3, possible_types)],
                        bad_val_values=[(val + '2', '')],
                        serialized_values=unicode(val),
                        deserialization_values=[(unicode(val), unicode(val))],
                        required=False,
                        default_value=unicode(val),
                        read_only=True,
                        forbidden=True)


class NameFieldTest(AbstractFieldTest, TestCase):

    O = NameField
    default_ctor_kwargs = {'value': u'', 'obligatory': True,
                           'order': 1, 'should_be_filled_by_sender': False}
    json = {u'type': u'name', u'is_obligatory': True, u'order': 1,
            u'value': u'', u'should_be_filled_by_sender': False,
            u'placements': []}

    def test_order(self):
        self._test_positive_int('order', required=False, default_value=1)

    def test_value(self):
        self._test_text('value', required=False, default_value=u'')

    def test_type(self):
        self._test_const_type('name')


class StandardFieldTest(AbstractFieldTest, TestCase):

    O = StandardField
    default_ctor_kwargs = {'value': u'', 'obligatory': True, 'type': 'mobile',
                           'should_be_filled_by_sender': False}
    json = {u'type': u'email', u'is_obligatory': True, u'placements': [],
            u'value': u'', u'should_be_filled_by_sender': False}

    def test_type(self):
        self._test_enum(StandardFieldType, attr_name='type',
                        read_only=True, skip_deser_bad_type_values=True)

    def test_value(self):
        self._test_text('value', required=False, default_value=u'')


class TextFieldTest(AbstractFieldTest, TestCase):

    O = TextField
    default_ctor_kwargs = {'value': u'', 'obligatory': True,
                           'name': u'field1',
                           'should_be_filled_by_sender': False}
    json = {u'type': u'text', u'is_obligatory': True, u'placements': [],
            u'name': u'field1', u'value': u'',
            u'should_be_filled_by_sender': False}

    def test_type(self):
        self._test_const_type('text')

    def test_value(self):
        self._test_text('value', required=False, default_value=u'')

    def test_name(self):
        self._test_non_empty_text('name')


class SignatureFieldTest(AbstractFieldTest, TestCase):

    O = SignatureField
    default_ctor_kwargs = {'obligatory': True, 'name': u'sig1'}
    json = {u'type': u'signature', u'is_obligatory': True,
            u'placements': [], u'name': u'sig1'}

    # override
    def test_should_be_filled_by_sender(self):
        # signatures don't use this param
        pass

    def test_type(self):
        self._test_const_type('signature')

    def test_name(self):
        self._test_non_empty_text('name')


class CheckboxFieldTest(AbstractFieldTest, TestCase):

    O = CheckboxField
    default_ctor_kwargs = {'checked': False, 'obligatory': True,
                           'name': u'checkbox1',
                           'should_be_filled_by_sender': False}
    json = {u'type': u'checkbox', u'is_obligatory': True, u'placements': [],
            u'name': u'checkbox1', u'is_checked': False,
            u'should_be_filled_by_sender': False}

    def test_type(self):
        self._test_const_type('checkbox')

    def test_name(self):
        self._test_non_empty_text('name')

    def test_checked(self):
        self._test_bool(attr_name='checked', required=False,
                        default_value=False, serialized_name=u'is_checked')


class JSONFactoryFieldTest(TestCase):

    O = Field

    def test_from_json(self):
        checkbox_json = CheckboxFieldTest.json
        descr = 'type(%s) == CheckboxField' % self._deser_call(checkbox_json)
        with describe(descr):
            checkbox = Field._from_json_obj(checkbox_json)
            self.assertTrue(isinstance(checkbox, CheckboxField))

        signature_json = SignatureFieldTest.json
        descr = 'type(%s) == SignatureField' % self._deser_call(signature_json)
        with describe(descr):
            signature = Field._from_json_obj(signature_json)
            self.assertTrue(isinstance(signature, SignatureField))

        text_json = TextFieldTest.json
        descr = 'type(%s) == TextField' % self._deser_call(text_json)
        with describe(descr):
            text = Field._from_json_obj(text_json)
            self.assertTrue(isinstance(text, TextField))

        name_json = NameFieldTest.json
        descr = 'type(%s) == NameField' % self._deser_call(name_json)
        with describe(descr):
            name = Field._from_json_obj(name_json)
            self.assertTrue(isinstance(name, NameField))

        email_json = dict(StandardFieldTest.json)
        email_json[u'type'] = u'email'
        descr = 'type(%s) == StandardField' % self._deser_call(email_json)
        with describe(descr):
            email = Field._from_json_obj(email_json)
            self.assertTrue(isinstance(email, StandardField))
            self.assertEqual(email.type, StandardFieldType.email)

        mobile_json = dict(StandardFieldTest.json)
        mobile_json[u'type'] = u'mobile'
        descr = 'type(%s) == StandardField' % self._deser_call(mobile_json)
        with describe(descr):
            mobile = Field._from_json_obj(mobile_json)
            self.assertTrue(isinstance(mobile, StandardField))
            self.assertEqual(mobile.type, StandardFieldType.mobile)

        pers_id_json = dict(StandardFieldTest.json)
        pers_id_json[u'type'] = u'personal_number'
        descr = 'type(%s) == StandardField' % self._deser_call(pers_id_json)
        with describe(descr):
            personal_number = Field._from_json_obj(pers_id_json)
            self.assertTrue(isinstance(personal_number, StandardField))
            self.assertEqual(personal_number.type,
                             StandardFieldType.personal_number)

        company_no_json = dict(StandardFieldTest.json)
        company_no_json[u'type'] = u'company_number'
        descr = 'type(%s) == StandardField' % self._deser_call(company_no_json)
        with describe(descr):
            company_number = Field._from_json_obj(company_no_json)
            self.assertTrue(isinstance(company_number, StandardField))
            self.assertEqual(company_number.type,
                             StandardFieldType.company_number)
