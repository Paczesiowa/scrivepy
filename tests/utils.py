import sys
import unittest


class TestCase(unittest.TestCase):

    def assertRaisesExcStr(self, excClass, excMsg,
                           callableObj, *args, **kwargs):
        try:
            callableObj(*args, **kwargs)
        except excClass as e:
            if sys.version_info < (3,):
                excMsg = excMsg.encode('ascii', 'replace').decode('ascii')
            self.assertEqual(str(e), excMsg)
