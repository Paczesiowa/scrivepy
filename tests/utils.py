import sys
import unittest


class AssertRaisesContext(object):

    def __init__(self, test_case, exc_class, exc_msg):
        self._test_case = test_case
        self._exc_class = exc_class
        self._exc_msg = exc_msg

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, tb):
        if exc_value is None:
            test_err_msg = self._exc_class.__name__ + u' not raised'
            raise self._test_case.failureException(test_err_msg)
        if not isinstance(exc_value, self._exc_class):
            return False
        if self._exc_msg is not None:
            self._test_case.assertEqual(str(exc_value), self._exc_msg)
        return True


class TestCase(unittest.TestCase):

    def assertRaises(self, exc_class, exc_msg=None,
                     callableObj=None, *args, **kwargs):
        if exc_msg is not None and sys.version_info < (3,):
            exc_msg = exc_msg.encode('ascii', 'replace').decode('ascii')
        if callableObj is None:
            return AssertRaisesContext(self, exc_class, exc_msg)
        try:
            callableObj(*args, **kwargs)
        except exc_class as e:
            if exc_msg is not None:
                self.assertEqual(str(e), exc_msg)
        else:
            test_err_msg = exc_class.__name__ + u' not raised'
            raise self.failureException(test_err_msg)
