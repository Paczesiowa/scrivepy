from scrivepy import _signatory, _document, _exceptions
from tests import utils


S = _signatory.Signatory
D = _document.Document


class SignatoryTest(utils.TestCase):

    def setUp(self):
        s1_json = {u'id': u'1',
                   u'current': True,
                   u'signorder': 1,
                   u'undeliveredInvitation': True,
                   u'undeliveredMailInvitation': False,
                   u'undeliveredSMSInvitation': False,
                   u'deliveredInvitation': False,
                   u'delivery': u'email',
                   u'confirmationdelivery': u'none',
                   u'authentication': u'standard',
                   u'signs': True,
                   u'author': True,
                   u'saved': True,
                   u'datamismatch': None,
                   u'signdate': None,
                   u'seendate': None,
                   u'readdate': None,
                   u'rejecteddate': None,
                   u'rejectionreason': None,
                   u'signsuccessredirect': None,
                   u'rejectredirect': None,
                   u'signlink': None,
                   u'fields': []}
        self.s1 = S._from_json_obj(s1_json)
        s2_json = s1_json.copy()
        s2_json[u'id'] = u'2'
        s2_json[u'author'] = False
        s2_json[u'viewer'] = True
        self.s2 = S._from_json_obj(s2_json)
        self.json = {u'signatories': [s1_json, s2_json]}

    def o(self, *args, **kwargs):
        return D(*args, **kwargs)

    def test_flags(self):
        s1 = S(author=True)
        s2 = S(viewer=True)
        d = self.o(signatories=set([s1, s2]))

        self.assertIsNone(d._check_getter())
        self.assertIsNone(s1._check_getter())
        self.assertIsNone(s2._check_getter())
        self.assertIsNone(d._check_setter())
        self.assertIsNone(s1._check_setter())
        self.assertIsNone(s2._check_setter())

        d._set_read_only()
        self.assertIsNone(d._check_getter())
        self.assertIsNone(s1._check_getter())
        self.assertIsNone(s2._check_getter())
        self.assertRaises(_exceptions.ReadOnlyScriveObject, None,
                          d._check_setter)
        self.assertRaises(_exceptions.ReadOnlyScriveObject, None,
                          s1._check_setter)
        self.assertRaises(_exceptions.ReadOnlyScriveObject, None,
                          s2._check_setter)

        d._set_invalid()
        self.assertRaises(_exceptions.InvalidScriveObject, None,
                          d._check_getter)
        self.assertRaises(_exceptions.InvalidScriveObject, None,
                          s1._check_getter)
        self.assertRaises(_exceptions.InvalidScriveObject, None,
                          s2._check_getter)
        self.assertRaises(_exceptions.InvalidScriveObject, None,
                          d._check_setter)
        self.assertRaises(_exceptions.InvalidScriveObject, None,
                          s1._check_setter)
        self.assertRaises(_exceptions.InvalidScriveObject, None,
                          s2._check_setter)

    def test_to_json_obj(self):
        d = self.o(signatories=set([self.s1]))

        json = {u'signatories': [self.s1]}

        self.assertEqual(json, d._to_json_obj())

    def test_from_json_obj(self):
        d = D._from_json_obj(self.json)
        self.assertEqual(sorted([s._to_json_obj()
                                 for s in d.signatories]),
                         sorted([self.s1._to_json_obj(),
                                 self.s2._to_json_obj()]))

    def test_modification_of_default_signatories_value(self):
        d1 = self.o()
        d1._signatories.add(1)
        d2 = self.o()
        self.assertEqual(set(), set(d2.signatories))

    def test_signatories(self):
        err_msg = u'signatories must be set, not 1'
        with self.assertRaises(TypeError, err_msg):
            self.o(signatories=1)

        err_msg = u'signatories must be set of Signatory objects, ' + \
            u'not: set([1])'
        with self.assertRaises(ValueError, err_msg):
            self.o(signatories=set([1]))

        # check default ctor value
        d = self.o()
        self.assertEqual(set([]), set(d.signatories))

        d = self.o(signatories=set([self.s1]))
        self.assertEqual(set([self.s1]), set(d.signatories))

        with self.assertRaises(TypeError, u'signatories must be set, not 1'):
            d.signatories = 1

        err_msg = u'signatories must be set of Signatory objects, ' + \
            u'not: set([1])'
        with self.assertRaises(ValueError, err_msg):
            d.signatories = set([1])

        d.signatories = set([self.s2])
        self.assertEqual(set([self.s2]), set(d.signatories))

        self.assertEqual([self.s2], d._to_json_obj()[u'signatories'])

        d._set_read_only()
        self.assertEqual(set([self.s2]), set(d.signatories))
        with self.assertRaises(_exceptions.ReadOnlyScriveObject, None):
            d.signatories = set([self.s1])

        d._set_invalid()
        with self.assertRaises(_exceptions.InvalidScriveObject, None):
            d.signatories
        with self.assertRaises(_exceptions.InvalidScriveObject, None):
            d.signatories = set([self.s1])
