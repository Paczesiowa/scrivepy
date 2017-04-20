# coding: utf-8
from scrivepy import Signatory

from tests.utils import IntegrationTestCase, describe


class SignatoryTest(IntegrationTestCase):

    O = Signatory
    default_ctor_kwargs = {}
    json = {u'id': u'123', u'user_id': u'456', u'is_author': False}

    def _test_remote_attr(self, attr_name, serialized_values,
                          bad_type_values, bad_val_values,
                          skip_preservation=True, default_value=None):
        self._test_attr_ctor(attr_name=attr_name,
                             good_values=[],
                             bad_type_values=[],
                             bad_val_values=[],
                             required=False,
                             default_value=default_value,
                             forbidden=True)

        self._test_attr_setter(attr_name=attr_name,
                               read_only=True,
                               good_values=[],
                               bad_type_values=[],
                               bad_val_values=[])

        # test that constructed objects dont serialize this field
        params, call_string = self._ctor_call()
        with describe('%s not in %s._to_json_obj()' % (attr_name,
                                                       call_string)):
                o = self.O(**params)
                self.assertFalse(attr_name in o._to_json_obj())

        # test that deserialized object serialize in the same way or skip
        for value in serialized_values:
            if skip_preservation:
                # test that for every v in serialized_values
                # serialized_name not in O._from_json_obj({attr_name:v})
                # ...._to_json_obj()
                json = dict(self.json)
                json[attr_name] = value
                str_attrs = (attr_name, self._deser_call(json))
                with describe('%s not in %s._to_json_obj()' % str_attrs):
                    o = self.O._from_json_obj(json)
                    self.assertFalse(attr_name in o._to_json_obj())
            else:
                # test that for every v in serialized_values
                # O._from_json_obj({attr_name:v})._to_json_obj()
                # ...[serialized_name] == v
                json = dict(self.json)
                json[attr_name] = value
                str_attrs = (self._deser_call(json), attr_name, repr(value))
                with describe('%s._to_json_obj()["%s"] == %s' % str_attrs):
                    o = self.O._from_json_obj(json)
                    self.assertEqual(o._to_json_obj()[attr_name], value)
                    self.assertEqual(type(o._to_json_obj()[attr_name]),
                                     type(value))

        serialized_values = [(x, x) for x in serialized_values]

        self._test_attr_deserialization(
            attr_name=attr_name,
            serialized_name=attr_name,
            serialized_values=serialized_values,
            bad_type_values=bad_type_values,
            bad_val_values=bad_val_values)

        self._test_invalid_field(attr_name + '77')

    def test_id(self):
        value_error = u'id must be non-empty digit-string'
        self._test_remote_attr('id', serialized_values=[u'123', u'456789'],
                               skip_preservation=False,
                               bad_type_values=[([], u'unicode'),
                                                (2, u'unicode'),
                                                (None, u'unicode')],
                               bad_val_values=[(u'', value_error),
                                               (u'żółw', value_error),
                                               (u'abc', value_error)])

    def test_user_id(self):
        value_error = u'user_id must be non-empty digit-string'
        self._test_remote_attr('user_id',
                               serialized_values=[u'123', u'456789', None],
                               bad_type_values=[([], u'unicode or None'),
                                                (2, u'unicode or None')],
                               bad_val_values=[(u'', value_error),
                                               (u'żółw', value_error),
                                               (u'abc', value_error)])

    def test_is_author(self):
        self._test_remote_attr('is_author',
                               serialized_values=[True, False],
                               default_value=False,
                               bad_type_values=[([], u'bool'),
                                                (2, u'bool')],
                               bad_val_values=[])
