import contextlib
import os
import re
import shutil
import sys
import tempfile
import unittest
from os import path

import nose
import testconfig

from scrivepy import _exceptions, _scrive


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

    def _test_server_field(self, field_name):
        o = self.o()
        self.assertIsNone(getattr(o, field_name))

        o._set_read_only()
        self.assertIsNone(getattr(o, field_name))

        o._set_invalid()
        with self.assertRaises(_exceptions.InvalidScriveObject, None):
            getattr(o, field_name)

    def _test_field(self, field_name, bad_value, correct_type,
                    default_good_value, other_good_values,
                    serialized_name=None, serialized_default_good_value=None,
                    bad_enum_value=None):
        if serialized_name is None:
            serialized_name = field_name
        if serialized_default_good_value is None:
            serialized_default_good_value = default_good_value
        if isinstance(correct_type, str):
            correct_type_name = correct_type
        else:
            correct_type_name = correct_type.__name__

        type_err_msg = (field_name + u' must be ' + correct_type_name +
                        ', not ' + str(bad_value))
        with self.assertRaises(TypeError, type_err_msg):
            self.o(**{field_name: bad_value})

        if bad_enum_value is not None:
            enum_type_err_msg = (field_name + u' could be ' +
                                 correct_type_name +
                                 "'s variant name, not: " + bad_enum_value)
            with self.assertRaises(ValueError, enum_type_err_msg):
                self.o(**{field_name: bad_enum_value})

        # check default ctor value
        o = self.o()
        self.assertEqual(default_good_value, getattr(o, field_name))

        for good_value in other_good_values:
            if isinstance(good_value, tuple):
                good_value, unified_good_value = good_value
            else:
                unified_good_value = good_value
            o = self.o(**{field_name: good_value})
            self.assertEqual(unified_good_value, getattr(o, field_name))

        with self.assertRaises(TypeError, type_err_msg):
            setattr(o, field_name, bad_value)

        setattr(o, field_name, default_good_value)
        self.assertEqual(default_good_value, getattr(o, field_name))

        self.assertEqual(serialized_default_good_value,
                         o._to_json_obj()[serialized_name])

        o._set_read_only()
        self.assertEqual(default_good_value, getattr(o, field_name))
        for good_value in other_good_values:
            with self.assertRaises(_exceptions.ReadOnlyScriveObject, None):
                setattr(o, field_name, good_value)

        o._set_invalid()
        with self.assertRaises(_exceptions.InvalidScriveObject, None):
            getattr(o, field_name)
        for good_value in other_good_values:
            with self.assertRaises(_exceptions.InvalidScriveObject, None):
                setattr(o, field_name, good_value)

    def _test_time_field(self, field_name, serialized_field_name):
        self._test_server_field(field_name)
        json = dict(self.json)
        json[serialized_field_name] = u'2014-10-29T15:40:20Z'
        o = self.O._from_json_obj(json)
        date_field = getattr(o, field_name)
        self.assertEqual(date_field.year, 2014)
        self.assertEqual(date_field.month, 10)
        self.assertEqual(date_field.day, 29)
        self.assertEqual(date_field.hour, 15)
        self.assertEqual(date_field.minute, 40)
        self.assertEqual(date_field.second, 20)
        self.assertEqual(date_field.microsecond, 0)


class IntegrationTestCase(TestCase):

    @classmethod
    def setUpClass(class_):
        try:
            cfg = testconfig.config['test_api_server']
        except KeyError:
            print 'You need to set api server configuration in'
            print 'tests/test_config.json (see tests/test_config_example.json)'
        else:
            class_.api = _scrive.Scrive(**cfg)
            class_.test_doc_path = \
                path.join(path.dirname(path.abspath(__file__)), 'document.pdf')
            with open(class_.test_doc_path, 'rb') as f:
                class_.test_doc_contents = f.read()

    @contextlib.contextmanager
    def new_document_from_file(self):
        try:
            doc = self.api.create_document_from_file(self.test_doc_path)
            yield doc
        finally:
            # refresh doc
            doc = self.api.get_document(doc.id)
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
