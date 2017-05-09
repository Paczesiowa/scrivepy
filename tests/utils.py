# coding: utf-8
import contextlib
from datetime import datetime
import os
from os import path
import re
import shutil
from subprocess import check_output
import sys
import tempfile
import unittest

from dateutil.tz import tzutc
import nose
import testconfig

from scrivepy import (
    InvalidResponse,
    InvalidScriveObject,
    ReadOnlyScriveObject,
    Scrive)
from scrivepy._set import ScriveSet


class AssertRaisesContext(object):

    def __init__(self, test_case, exc_class, exc_msg, regex):
        self._test_case = test_case
        self._exc_class = exc_class
        self._exc_msg = exc_msg
        self._regex = regex

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, tb):
        if exc_value is None:
            test_err_msg = self._exc_class.__name__ + u' not raised'
            raise self._test_case.failureException(test_err_msg)
        if not isinstance(exc_value, self._exc_class):
            return False
        if self._exc_msg is not None and self._regex:
            regexp = re.compile(self._exc_msg)
            if not regexp.match(str(exc_value)):
                raise self._test_case.failureException(
                    '"%s" does not match "%s"' % (regexp.pattern,
                                                  str(exc_value)))
        elif self._exc_msg is not None:
            self._test_case.assertEqual(str(exc_value), self._exc_msg)
        return True


def integration(f):
    @nose.plugins.attrib.attr('integration')
    def wrapper(*args, **kwargs):
        if 'integration' in sys.argv:
            return f(*args, **kwargs)
        else:
            raise nose.plugins.skip.SkipTest
    wrapper.__name__ = f.__name__
    return wrapper


class TestCase(unittest.TestCase):

    def assertRaises(self, exc_class, exc_msg=None,
                     callableObj=None, regex=False, *args, **kwargs):
        if exc_msg is not None and sys.version_info < (3,):
            exc_msg = exc_msg.encode('ascii', 'replace').decode('ascii')
        if callableObj is None:
            return AssertRaisesContext(self, exc_class, exc_msg, regex)
        try:
            callableObj(*args, **kwargs)
        except exc_class as e:
            if exc_msg is not None:
                self.assertEqual(str(e), exc_msg)
        else:
            test_err_msg = exc_class.__name__ + u' not raised'
            raise self.failureException(test_err_msg)

    def _test_invalid_field(self, invalid_field_name):
        # this field should not exist

        params, call_string = self._ctor_call()
        descr = 'o=%s;o.%s throws AttributeError' % (call_string,
                                                     invalid_field_name)
        with describe(descr):
            with self.assertRaises(AttributeError, None):
                o = self.O(**params)
                getattr(o, invalid_field_name)

        params, call_string = self._ctor_call()
        descr = 'o=%s;o.%s=None throws AttributeError' % (call_string,
                                                          invalid_field_name)
        with describe(descr):
            with self.assertRaises(AttributeError, None):
                o = self.O(**params)
                setattr(o, invalid_field_name, None)

        params, call_string = self._ctor_call()
        descr = 'o=%s;o._set_read_only();o.%s throws AttributeError' % (
                call_string, invalid_field_name)
        with describe(descr):
            with self.assertRaises(AttributeError, None):
                o = self.O(**params)
                o._set_read_only()
                getattr(o, invalid_field_name)

        params, call_string = self._ctor_call()
        descr = 'o=%s;o._set_read_only();o.%s=None throws AttributeError' % (
                call_string, invalid_field_name)
        with describe(descr):
            with self.assertRaises(AttributeError, None):
                o = self.O(**params)
                o._set_read_only()
                setattr(o, invalid_field_name, None)

        params, call_string = self._ctor_call()
        descr = 'o=%s;o._set_read_only();o.%s throws AttributeError' % (
                call_string, invalid_field_name)
        with describe(descr):
            with self.assertRaises(AttributeError, None):
                o = self.O(**params)
                o._set_invalid()
                getattr(o, invalid_field_name)

        params, call_string = self._ctor_call()
        descr = \
            'o=%s;o._set_read_only();o.%s=None throws InvalidScriveObject' % (
                call_string, invalid_field_name)
        with describe(descr):
            with self.assertRaises(InvalidScriveObject, None):
                o = self.O(**params)
                o._set_invalid()
                setattr(o, invalid_field_name, None)

    def assertPDFsEqual(self, pdf_contents1, pdf_contents2):
        with temporary_file_path() as file_path:
            mutool_args = ['mutool', 'draw', '-o', '-', file_path]
            with open(file_path, 'wb') as f:
                f.write(pdf_contents1)
            png_contents1 = check_output(mutool_args)
            with open(file_path, 'wb') as f:
                f.write(pdf_contents2)
            png_contents2 = check_output(mutool_args)
        self.assertEqual(png_contents1, png_contents2)

    def _ctor_call(self, params=None, **param_overrides):
        if params is None:
            params = self.default_ctor_kwargs.copy()
        for name, val in param_overrides.items():
            params[name] = val
        params_string = ','.join([param + '=' + repr(val)
                                  for param, val in params.items()])
        return params, '%s(%s)' % (self.O.__name__, params_string)

    def _deser_call(self, json_obj):
        return '%s._from_json_obj(%s)' % (self.O.__name__, repr(json_obj))

    def _test_attr_ctor(self, attr_name, forbidden, good_values,
                        bad_type_values, bad_val_values,
                        required, default_value):
        # if attr_name is a forbidden ctor arg, check that
        # using it, __init__() throws TypeError
        if forbidden:
            err_msg = (u"__init__() got an unexpected keyword argument '" +
                       attr_name + u"'")
            params, call_string = self._ctor_call(**{attr_name: None})
            with describe(call_string + ' throws TypeError'):
                with self.assertRaises(TypeError, err_msg):
                    o = self.O(**params)

        # if attr_name is an optional ctor arg, check that
        # without it, __init__() sets a good value:
        # o().attr_name == default_value
        if not required:
            params = dict(self.default_ctor_kwargs)
            params.pop(attr_name, None)
            params, call_string = self._ctor_call(params)
            with describe('%s.%s == %s' % (call_string, attr_name,
                                           default_value)):
                o = self.O(**params)
                self.assertEqual(getattr(o, attr_name), default_value)
                self.assertEqual(type(getattr(o, attr_name)),
                                 type(default_value))

        # no point in other tests
        if forbidden:
            return

        # test, that for every pair (v1, v2) in good_values
        # o(attr_name=v1).attr_name == v2
        for value_in, value_out in good_values:
            params, call_string = self._ctor_call(**{attr_name: value_in})
            with describe('%s.%s == %s' % (call_string, attr_name, value_out)):
                o = self.O(**params)
                self.assertEqual(getattr(o, attr_name), value_out)
                self.assertEqual(type(getattr(o, attr_name)), type(value_out))

        # test, that for every pair (v, err) in bad_type_values
        # o(attr_name=v) throws TypeError(err)
        for value_in, err in bad_type_values:
            params, call_string = self._ctor_call(**{attr_name: value_in})
            err_msg = \
                attr_name + ' must be ' + err + ', not ' + repr(value_in)
            with describe('%s throws TypeError(%s)' % (call_string, err_msg)):
                with self.assertRaises(TypeError, err_msg):
                    o = self.O(**params)

        # test, that for every pair (v, err) in bad_val_values
        # o(attr_name=v) throws ValueError(err)
        for value_in, err in bad_val_values:
            params, call_string = self._ctor_call(**{attr_name: value_in})
            with describe('%s throws ValueError(%s)' % (call_string, err)):
                with self.assertRaises(ValueError, err, regex=True):
                    o = self.O(**params)

        # if attr_name is not an optional ctor arg, check that
        # TypeError is raised when this param is not used
        if required:
            params = dict(self.default_ctor_kwargs)
            params.pop(attr_name, None)
            params, call_string = self._ctor_call(params)
            err_msg = \
                u'__init__() requires ' + attr_name + u' keyword argument'
            with describe('%s throws TypeError(%s)' % (call_string, err_msg)):
                with self.assertRaises(TypeError, err_msg):
                    o = self.O(**params)

    def _test_attr_setter(self, attr_name, read_only, good_values,
                          bad_type_values, bad_val_values):
        # if attr is read_only, check if assignment throws AttributeError
        if read_only:
            params, call_string = self._ctor_call()
            set_string = '%s.%s=%s' % (call_string, attr_name, repr(None))
            with describe(set_string + ' throws AttributeError'):
                with self.assertRaises(AttributeError):
                    o = self.O(**params)
                    setattr(o, attr_name, None)

            # no point in other tests
            return

        # test, that for every pair (v1, v2) in good_values
        # o = o(); o.attr_name = v1; o.attr_name == v2
        for value_in, value_out in good_values:
            params, call_string = self._ctor_call()
            o = self.O(**params)
            setattr(o, attr_name, value_in)
            with describe('o=%s;o.%s=%s;o.%s == %s' % (call_string, attr_name,
                                                       repr(value_in),
                                                       attr_name,
                                                       repr(value_out))):
                self.assertEqual(getattr(o, attr_name), value_out)
                self.assertEqual(type(getattr(o, attr_name)), type(value_out))

        # test, that for every pair (v, err) in bad_type_values
        # o = o(); o.attr_name=v throws TypeError(err)
        for value_in, err in bad_type_values:
            params, call_string = self._ctor_call()
            err_msg = \
                attr_name + ' must be ' + err + ', not ' + repr(value_in)
            descr = 'o=%s;o.%s=%s throws TypeError(%s)' % (call_string,
                                                           attr_name,
                                                           repr(value_in),
                                                           err_msg)
            with describe(descr):
                o = self.O(**params)
                with self.assertRaises(TypeError, err_msg):
                    setattr(o, attr_name, value_in)

        # test, that for every pair (v, err) in bad_value_values
        # o = o(); o.attr_name=v throws ValueError(err)
        for value_in, err_msg in bad_val_values:
            params, call_string = self._ctor_call()
            descr = 'o=%s;o.%s=%s throws ValueError(%s)' % (call_string,
                                                            attr_name,
                                                            repr(value_in),
                                                            err_msg)
            with describe(descr):
                o = self.O(**params)
                with self.assertRaises(ValueError, regex=err_msg):
                    setattr(o, attr_name, value_in)

        # test, that for every pair (v, _) in good_values
        # o = o(attr_name=v); o._set_read_only(); o.attr_name == v,
        # but o.attr_name = v throws ReadOnlyScriveObject
        for value_in, value_out in good_values:
            params, call_string = self._ctor_call(**{attr_name: value_in})
            descr = 'o=%s;o._set_read_only();o.%s == %s'
            with describe(descr % (call_string, attr_name, repr(value_out))):
                o = self.O(**params)
                o._set_read_only()
                self.assertEqual(getattr(o, attr_name), value_out)
                self.assertEqual(type(getattr(o, attr_name)), type(value_out))
            descr = \
                'o=%s;o._set_read_only();o.%s=%s throws ReadOnlyScriveObject'
            with describe(descr % (call_string, attr_name, repr(value_in))):
                with self.assertRaises(ReadOnlyScriveObject):
                    setattr(o, attr_name, value_in)

        # test, that for every pair (v, _) in good_values
        # o = o(attr_name=v); o._set_invalid(); o.attr_name and
        # o.attr_name = v throws ReadOnlyScriveObject
        for value_in, value_out in good_values:
            params, call_string = self._ctor_call(**{attr_name: value_in})
            descr = 'o=%s;o._set_invalid();o.%s throws InvalidScriveObject'
            with describe(descr % (call_string, attr_name)):
                o = self.O(**params)
                o._set_invalid()
                with self.assertRaises(InvalidScriveObject):
                    getattr(o, attr_name)
            descr = \
                'o=%s;o._set_invalid();o.%s=%s throws InvalidScriveObject'
            with describe(descr % (call_string, attr_name, repr(value_in))):
                with self.assertRaises(InvalidScriveObject):
                    setattr(o, attr_name, value_in)

    def _test_attr_serialization(self, attr_name, serialized_name,
                                 serialized_values):
        if not isinstance(serialized_values, list):
            # just one value that is supposed to be the serialization
            # of default object
            default_serialized_value = serialized_values
            # test that O()._to_json_obj()[serialized_name]
            #     == default_serialized_value
            params, call_string = self._ctor_call()
            str_params = (call_string, serialized_name,
                          repr(default_serialized_value))
            with describe('%s._to_json_obj()["%s"] == %s' % str_params):
                o = self.O(**params)
                self.assertEqual(o._to_json_obj()[serialized_name],
                                 default_serialized_value)
                self.assertEqual(type(o._to_json_obj()[serialized_name]),
                                 type(default_serialized_value))

            # no point in other tests
            return

        # test that for every pair (v1, v2) in serialized_values
        # o(attr_name=v1)._to_json_obj()[serialized_name] == v2
        for value_in, value_out in serialized_values:
            params, call_string = self._ctor_call(**{attr_name: value_in})
            with describe('%s._to_json_obj()["%s"] == %s' % (call_string,
                                                             serialized_name,
                                                             repr(value_out))):
                o = self.O(**params)
                self.assertEqual(o._to_json_obj()[serialized_name], value_out)
                self.assertEqual(type(o._to_json_obj()[serialized_name]),
                                 type(value_out))

    def _test_attr_deserialization(self, attr_name, serialized_name,
                                   serialized_values, bad_type_values,
                                   bad_val_values):
        # test that if attr is missing in server's response
        # _from_json_obj() throws InvalidResponse
        json = dict(self.json)
        del json[serialized_name]
        err_msg = serialized_name + r' missing'
        descr = '%s throws InvalidResponse(%s)' % (self._deser_call(json),
                                                   err_msg)
        with describe(descr):
            with self.assertRaises(InvalidResponse, regex=err_msg):
                self.O._from_json_obj(json)

        # test that for every pair (v1, v2) in serialized_values
        # json[serialized_name]=v2; O._from_json_obj(json).attr_name == v1
        for value_in, value_out in serialized_values:
            json = dict(self.json)
            json[serialized_name] = value_out
            with describe('%s.%s == %s' % (self._deser_call(json), attr_name,
                                           repr(value_in))):
                o = self.O._from_json_obj(json)
                self.assertTrue(isinstance(o, self.O))
                self.assertEqual(getattr(o, attr_name), value_in)
                self.assertEqual(type(getattr(o, attr_name)), type(value_in))

        # test, that for every pair (v, err) in bad_type_values
        # O._from_json_obj({attr_name: v}) throws ValidationError(err)
        for value_in, err in bad_type_values:
            json = dict(self.json)
            json[serialized_name] = value_in
            err_msg = \
                attr_name + ' must be ' + err + ', not ' + repr(value_in)
            deser_call = self._deser_call(json)
            with describe('%s throws InvalidResponse(%s)' % (deser_call,
                                                             err_msg)):
                with self.assertRaises(InvalidResponse, err_msg):
                    self.O._from_json_obj(json)

        # test, that for every pair (v, err) in bad_val_values
        # O._from_json_obj({attr_name: v}) throws ValidationError(err)
        for value_in, err in bad_val_values:
            json = dict(self.json)
            json[serialized_name] = value_in
            deser_call = self._deser_call(json)
            with describe('%s throws InvalidResponse(%s)' % (deser_call, err)):
                with self.assertRaises(InvalidResponse, regex=err):
                    self.O._from_json_obj(json)

    def _test_attr(self, preset_values=None, **overrides):
        kwargs = {'good_values': [],
                  'bad_type_values': [],
                  'bad_val_values': [],
                  'serialized_values': [],
                  'serialized_name': None,
                  'required': True,
                  'default_value': None,
                  'forbidden': False,
                  'deserialization_values': None,
                  'read_only': False,
                  'skip_deser_bad_type_values': False}
        kwargs.update(preset_values or {}, **overrides)

        if kwargs['serialized_name'] is None:
            kwargs['serialized_name'] = kwargs['attr_name']
        if kwargs['deserialization_values'] is None:
            kwargs['deserialization_values'] = kwargs['serialized_values']

        self._test_attr_ctor(attr_name=kwargs['attr_name'],
                             good_values=kwargs['good_values'],
                             bad_type_values=kwargs['bad_type_values'],
                             bad_val_values=kwargs['bad_val_values'],
                             required=kwargs['required'],
                             default_value=kwargs['default_value'],
                             forbidden=kwargs['forbidden'])

        self._test_attr_setter(attr_name=kwargs['attr_name'],
                               read_only=kwargs['read_only'],
                               good_values=kwargs['good_values'],
                               bad_type_values=kwargs['bad_type_values'],
                               bad_val_values=kwargs['bad_val_values'])

        self._test_attr_serialization(
            attr_name=kwargs['attr_name'],
            serialized_name=kwargs['serialized_name'],
            serialized_values=kwargs['serialized_values'])

        if kwargs['skip_deser_bad_type_values']:
            bad_deser_type_vals = []
        else:
            bad_deser_type_vals = kwargs['bad_type_values']
        self._test_attr_deserialization(
            attr_name=kwargs['attr_name'],
            serialized_name=kwargs['serialized_name'],
            serialized_values=kwargs['deserialization_values'],
            bad_type_values=bad_deser_type_vals,
            bad_val_values=kwargs['bad_val_values'])

        self._test_invalid_field(kwargs['attr_name'] + '77')

    def _test_text(self, **kwargs):
        unicode_err = (kwargs['attr_name'] +
                       u' must be unicode text, or ascii-only bytestring')
        self._test_attr({'good_values': [(u'', u''), (u'foo', u'foo'),
                                         (b'bar', u'bar'), (u'żółw', u'żółw')],
                         'bad_type_values': [([], u'unicode or str'),
                                             (None, u'unicode or str'),
                                             (2, u'unicode or str')],
                         'bad_val_values': [(u'ą'.encode('utf-8'),
                                             unicode_err)],
                         'serialized_values': [(u'', u''), (u'foo', u'foo'),
                                               (u'żółw', u'żółw'),
                                               (u'bar', u'bar')]},
                        **kwargs)

    def _test_non_empty_text(self, **kwargs):
        unicode_err = (kwargs['attr_name'] + u' must be unicode text,' +
                       ' or ascii-only bytestring')
        non_empty_err = kwargs['attr_name'] + u' must be non-empty string'
        self._test_attr({
            'good_values': [(u'foo', u'foo'), (b'bar', u'bar'),
                            (u'żółw', u'żółw')],
            'bad_type_values': [([], u'unicode or str'),
                                (None, u'unicode or str'),
                                (2, u'unicode or str')],
            'bad_val_values': [(u'ą'.encode('utf-8'), unicode_err),
                               (u'', non_empty_err)],
            'serialized_values': [(u'foo', u'foo'), (u'żółw', u'żółw'),
                                  (u'bar', u'bar')]}, **kwargs)

    def _test_int(self, **kwargs):
        self._test_attr({
            'good_values': [(-2, -2), (-1, -1), (0, 0), (1, 1), (2, 2)],
            'bad_type_values': [([], u'int'), (3.0, u'int'), ('4', u'int')],
            'serialized_values': [(-2, -2), (-1, -1), (0, 0), (1, 1), (2, 2)]},
            **kwargs)

    def _test_bool(self, **kwargs):
        self._test_attr({
            'good_values': [(True, True), (False, False)],
            'bad_type_values': [([], u'bool'), (3.0, u'bool'), ('4', u'bool')],
            'serialized_values': [(True, True), (False, False)]}, **kwargs)

    def _test_positive_int(self, **kwargs):
        self._test_attr({
            'good_values': [(1, 1), (2, 2), (3, 3), (10, 10)],
            'bad_type_values': [([], u'int or float'), ('4', u'int or float')],
            'bad_val_values': [(0, r'.*integer greater or equal to 1.*'),
                               (1.1, r'.*round number.*')],
            'serialized_values': [(1, 1), (2, 2), (3, 3), (2, 2), (100, 100)]},
            **kwargs)

    def _test_enum(self, enum_class, **kwargs):
        ename = enum_class.__name__
        good_values = ([(x, x) for x in list(enum_class)] +
                       [(enum_elem.name, enum_elem)
                        for enum_elem in enum_class])
        serialized_values = [(enum_elem, enum_elem._serialize())
                             for enum_elem in enum_class]
        enum_variant_err = r'.*could be ' + ename + r"'s variant name.*"
        self._test_attr({
            'good_values': good_values,
            'bad_type_values': [({}, ename), (0, ename), ([], ename)],
            'bad_val_values': [('wrong', enum_variant_err)],
            'serialized_values': serialized_values}, **kwargs)

    def _test_set(self, elem_type, attr_name,
                  sub_factory, serialized_name=None):
        if serialized_name is None:
            serialized_name = attr_name

        self._test_attr_ctor(attr_name, forbidden=True, good_values=[],
                             bad_type_values=[], bad_val_values=[],
                             required=False, default_value=ScriveSet())
        self._test_attr_setter(attr_name, read_only=True, good_values=[],
                               bad_type_values=[], bad_val_values=[])

        subobj_str = elem_type.__name__ + '(..)'

        # new objects should have empty ScriveSet attribute
        params, call_string = self._ctor_call()
        with describe('%s.%s == set()' % (call_string, attr_name)):
            o = self.O(**params)
            self.assertEqual(set(getattr(o, attr_name)), set())
            self.assertTrue(isinstance(getattr(o, attr_name), ScriveSet))

        # test that adding subobjects works
        params, call_string = self._ctor_call()
        descr = 'o=%s;o.%s.add(%s);list(o.%s)[0]==%s' % (
            call_string, attr_name, subobj_str, attr_name, subobj_str)
        with describe(descr):
            o = self.O(**params)
            sub_obj = elem_type._from_json_obj(sub_factory())
            getattr(o, attr_name).add(sub_obj)
            self.assertEqual(list(getattr(o, attr_name))[0], sub_obj)

        # subobject validation
        params, call_string = self._ctor_call()
        descr = 'o=%s;o.%s.add(None) throws TypeError' % (call_string,
                                                          attr_name)
        with describe(descr):
            o = self.O(**params)
            err_msg = u'elem must be ' + elem_type.__name__ + ', not None'
            with self.assertRaises(TypeError, err_msg):
                getattr(o, attr_name).add(None)

        # test serialization
        params, call_string = self._ctor_call()
        descr = 'o=%s;o.%s.add([%s,%s]);o._to_json_obj()[%s]==[%s,%s]' % (
            call_string, attr_name, subobj_str, subobj_str,
            attr_name, subobj_str, subobj_str)
        with describe(descr):
            o = self.O(**params)
            sub_obj1 = elem_type._from_json_obj(sub_factory())
            sub_obj2 = elem_type._from_json_obj(sub_factory(2))
            getattr(o, attr_name).update([sub_obj1, sub_obj2])
            self.assertEqual(sorted([sub_obj1._to_json_obj(),
                                     sub_obj2._to_json_obj()]),
                             sorted(o._to_json_obj()[serialized_name]))

        # test deserialization
        descr = ('o=%s;o.%s.add([%s,%s]);' +
                 'o2=%s._from_json_obj(o._to_json_obj());' +
                 'o2.%s==[%s,%s]') % (call_string, attr_name, subobj_str,
                                      subobj_str, self.O.__name__,
                                      attr_name, subobj_str, subobj_str)
        with describe(descr):
            sub_obj_json1 = sub_factory()
            sub_obj_json2 = sub_factory(2)
            sub_jsons = [sub_obj_json1, sub_obj_json2]
            sub_objs = [elem_type._from_json_obj(sub_obj_json1),
                        elem_type._from_json_obj(sub_obj_json2)]
            json = dict(self.json)
            json[serialized_name] = sub_jsons
            o = self.O._from_json_obj(json)
            # from ipdb import set_trace; set_trace()
            self.assertEqual(sorted(map(lambda x: x._to_json_obj(), sub_objs)),
                             sorted(map(lambda x: x._to_json_obj(),
                                        getattr(o, attr_name))))

        # test flag propagation
        o = self.O(**params)
        sub_obj = elem_type._from_json_obj(sub_factory())
        sub_obj2 = elem_type._from_json_obj(sub_factory(2))
        getattr(o, attr_name).add(sub_obj)
        o._set_read_only()
        self.assertEqual(list(getattr(o, attr_name))[0], sub_obj)
        with self.assertRaises(ReadOnlyScriveObject):
            getattr(o, attr_name).add(sub_obj)
        with self.assertRaises(ReadOnlyScriveObject):
            getattr(o, attr_name).add(sub_obj2)
        self.assertTrue(sub_obj._read_only)

        o = self.O(**params)
        sub_obj = elem_type._from_json_obj(sub_factory())
        sub_obj2 = elem_type._from_json_obj(sub_factory(2))
        getattr(o, attr_name).add(sub_obj)
        o._set_invalid()
        with self.assertRaises(InvalidScriveObject):
            getattr(o, attr_name)
        self.assertTrue(sub_obj._invalid)

    def _test_remote_attr(self, preset_values=None, **overrides):
        kwargs = {'serialized_values': [],
                  'bad_type_values': [],
                  'bad_val_values': [],
                  'serialized_name': None,
                  'skip_preservation': True,
                  'default_value': None}
        kwargs.update(preset_values or {}, **overrides)
        if kwargs['serialized_name'] is None:
            kwargs['serialized_name'] = kwargs['attr_name']
        serialized_name = kwargs['serialized_name']
        attr_name = kwargs['attr_name']

        self._test_attr_ctor(attr_name=attr_name,
                             good_values=[],
                             bad_type_values=[],
                             bad_val_values=[],
                             required=False,
                             default_value=kwargs['default_value'],
                             forbidden=True)

        self._test_attr_setter(attr_name=attr_name,
                               read_only=True,
                               good_values=[],
                               bad_type_values=[],
                               bad_val_values=[])

        # test that constructed objects dont serialize this field
        params, call_string = self._ctor_call()
        with describe('%s not in %s._to_json_obj()' % (serialized_name,
                                                       call_string)):
                o = self.O(**params)
                self.assertFalse(serialized_name in o._to_json_obj())

        # test that deserialized object serialize in the same way or skip
        for _, value in kwargs['serialized_values']:
            if kwargs['skip_preservation']:
                # test that for every _, v in serialized_values
                # serialized_name not in O._from_json_obj({serialized_name:v})
                # ...._to_json_obj()
                json = dict(self.json)
                json[serialized_name] = value
                str_attrs = (serialized_name, self._deser_call(json))
                with describe('%s not in %s._to_json_obj()' % str_attrs):
                    o = self.O._from_json_obj(json)
                    self.assertFalse(serialized_name in o._to_json_obj())
            else:
                # test that for every _, v in serialized_values
                # O._from_json_obj({serialized_name:v})._to_json_obj()
                # ...[serialized_name] == v
                json = dict(self.json)
                json[serialized_name] = value
                str_attrs = (self._deser_call(json), serialized_name,
                             repr(value))
                with describe('%s._to_json_obj()["%s"] == %s' % str_attrs):
                    o = self.O._from_json_obj(json)
                    self.assertEqual(o._to_json_obj()[attr_name], value)
                    self.assertEqual(type(o._to_json_obj()[attr_name]),
                                     type(value))

        self._test_attr_deserialization(
            attr_name=attr_name,
            serialized_name=serialized_name,
            serialized_values=kwargs['serialized_values'],
            bad_type_values=kwargs['bad_type_values'],
            bad_val_values=kwargs['bad_val_values'])

        self._test_invalid_field(attr_name + '77')

    def _test_remote_id(self, remote_null_ok=False, **kwargs):
        attr_name = kwargs['attr_name']
        serialized_values = [(u'123', u'123'), (u'456789', u'456789')]
        bad_type_values = [([], u'unicode'), (2, u'unicode')]
        if remote_null_ok:
            serialized_values.append((None, None))
            bad_type_values = [([], u'unicode or None'),
                               (2, u'unicode or None')]
        else:
            bad_type_values = [([], u'unicode'), (2, u'unicode'),
                               (None, u'unicode')]
        value_error = attr_name + u' must be non-empty digit-string'
        self._test_remote_attr({'serialized_values': serialized_values,
                                'bad_type_values': bad_type_values,
                                'bad_val_values': [(u'', value_error),
                                                   (u'żółw', value_error),
                                                   (u'abc', value_error)]},
                               **kwargs)

    def _test_remote_bool(self, **kwargs):
        self._test_remote_attr({'bad_type_values': [([], u'bool'),
                                                    (3.0, u'bool'),
                                                    ('4', u'bool')],
                                'serialized_values': [(True, True),
                                                      (False, False)]},
                               **kwargs)

    def _test_remote_time_attr(self, **kwargs):
        d1s = u'2014-10-29T15:40:20Z'
        d1 = datetime(2014, 10, 29, 15, 40, 20, tzinfo=tzutc())
        d2s = u'2017-04-22T12:56:00Z'
        d2 = datetime(2017, 4, 22, 12, 56, 0, tzinfo=tzutc())
        type_error = u'datetime, unicode or None'
        self._test_remote_attr({'serialized_values': [(d1, d1s), (d2, d2s)],
                                'bad_type_values': [([], type_error),
                                                    (2, type_error)],
                                'bad_val_values': [(u'2014-10-29T', u''),
                                                   (d1s + u'foo', u'')]},
                               **kwargs)

    def _test_remote_enum(self, enum_class, **kwargs):
        ename = enum_class.__name__
        serialized_values = [(enum_elem, enum_elem.value)
                             for enum_elem in enum_class]
        enum_variant_err = r'.*could be ' + ename + r"'s variant name.*"
        self._test_remote_attr({'serialized_values': serialized_values,
                               'bad_type_values': [({}, ename),
                                                   (0, ename),
                                                   ([], ename)],
                                'bad_val_values': [('wrong',
                                                    enum_variant_err)]},
                               **kwargs)

    def _test_remote_nullable_non_empty_text(self, **kwargs):
        attr_name = kwargs['attr_name']
        unicode_err = (attr_name + u' must be unicode text,' +
                       ' or ascii-only bytestring')
        non_empty_err = attr_name + u' must be non-empty string'
        type_err = u'unicode, str or None'
        self._test_remote_attr({'serialized_name': 'api_delivery_url',
                                'serialized_values': [(u'foo', u'foo'),
                                                      (u'żółw', u'żółw'),
                                                      (u'bar', u'bar')],
                                'bad_type_values': [([], type_err),
                                                    (2, type_err)],
                                'bad_val_values': [(u'ą'.encode('utf-8'),
                                                    unicode_err),
                                                   (u'', non_empty_err)]},
                               **kwargs)


class IntegrationTestCase(TestCase):

    @classmethod
    def setUpClass(class_):
        try:
            cfg = testconfig.config['test_api_server']
        except KeyError:
            print 'You need to set api server configuration in'
            print 'tests/test_config.json (see tests/test_config_example.json)'
        else:
            class_.api = Scrive(**cfg)
            docs_path = path.dirname(path.abspath(__file__))
            class_.test_doc_path = path.join(docs_path, 'document.pdf')
            with open(class_.test_doc_path, 'rb') as f:
                class_.test_doc_contents = f.read()
            class_.test_doc_path2 = path.join(docs_path, 'document2.pdf')
            with open(class_.test_doc_path2, 'rb') as f:
                class_.test_doc_contents2 = f.read()

    @contextlib.contextmanager
    def new_document_from_file(self):
        try:
            doc = self.api.create_document_from_file(self.test_doc_path)
            doc_id = doc.id
            doc.author.invitation_delivery_method = 'api'
            doc.author.confirmation_delivery_method = 'none'
            yield self.api.update_document(doc)
        finally:
            # refresh doc
            doc = self.api.get_document(doc_id)
            self.api.delete_document(doc)

    @contextlib.contextmanager
    def new_document_from_template(self, template_id):
        try:
            doc = self.api.create_document_from_template(template_id)
            yield doc
        finally:
            # refresh doc
            doc = self.api.get_document(doc.id)
            self.api.delete_document(doc)


@contextlib.contextmanager
def temporary_file_path():
    fd, file_path = tempfile.mkstemp()
    try:
        os.close(fd)
        yield file_path
    finally:
        try:
            os.remove(file_path)
        except OSError:
            pass


@contextlib.contextmanager
def temporary_dir():
    dir_path = tempfile.mkdtemp()
    try:
        yield dir_path
    finally:
        try:
            shutil.rmtree(dir_path)
        except OSError:
            pass


@contextlib.contextmanager
def describe(description):
    print (description + '?'),
    try:
        yield
    except:
        print ':(((((('
        raise
    else:
        print 'OK'
