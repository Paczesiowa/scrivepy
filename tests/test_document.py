from scrivepy import _signatory, _document, _exceptions
from tests import utils


S = _signatory.Signatory
D = _document.Document
DS = _document.DocumentStatus


class DocumentTest(utils.TestCase):

    def setUp(self):
        self.O = D
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
        self.json = {u'id': u'1234',
                     u'title': u'a document',
                     u'daystosign': 20,
                     u'daystoremind': 10,
                     u'status': u'Pending',
                     u'time': None,
                     u'ctime': None,
                     u'timeouttime': None,
                     u'autoremindtime': None,
                     u'signorder': 1,
                     u'template': True,
                     u'signatories': [s1_json, s2_json]}

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
        d = self.o(title=u'the document',
                   number_of_days_to_sign=30,
                   number_of_days_to_remind=20,
                   is_template=True,
                   signatories=set([self.s1]))

        json = {u'title': u'the document',
                u'daystosign': 30,
                u'daystoremind': 20,
                u'template': True,
                u'signatories': [self.s1]}

        self.assertEqual(json, d._to_json_obj())

    def test_from_json_obj(self):
        d = D._from_json_obj(self.json)
        self.assertEqual(d.id, u'1234')
        self.assertEqual(d.title, u'a document')
        self.assertEqual(d.number_of_days_to_sign, 20)
        self.assertEqual(d.number_of_days_to_remind, 10)
        self.assertEqual(d.status, DS.pending)
        self.assertEqual(d.modification_time, None)
        self.assertEqual(d.creation_time, None)
        self.assertEqual(d.signing_deadline, None)
        self.assertEqual(d.autoremind_time, None)
        self.assertEqual(d.current_sign_order, 1)
        self.assertEqual(d.authentication_method, u'standard')
        self.assertEqual(d.invitation_delivery_method, u'email')
        self.assertEqual(d.is_template, True)
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

    def test_id(self):
        self._test_server_field('id')

    def test_title(self):
        self._test_field('title',
                         bad_value=[], correct_type=unicode,
                         default_good_value=u'',
                         other_good_values=[u'some document'])

    def test_number_of_days_to_sign(self):
        self._test_field('number_of_days_to_sign',
                         bad_value=[], correct_type='int or float',
                         default_good_value=14,
                         other_good_values=[1, 45, 90],
                         serialized_name=u'daystosign')

        err_msg = u'number_of_days_to_sign must be an integer ' + \
                  u'between 1 and 90 (inclusive), not: 0'
        with self.assertRaises(ValueError, err_msg):
            self.o(number_of_days_to_sign=0)

        err_msg = u'number_of_days_to_sign must be an integer ' + \
                  u'between 1 and 90 (inclusive), not: 91.0'
        with self.assertRaises(ValueError, err_msg):
            self.o(number_of_days_to_sign=91.)

    def test_status(self):
        self._test_server_field('status')

    def test_modification_time(self):
        self._test_time_field('modification_time', u'time')

    def test_creation_time(self):
        self._test_time_field('creation_time', u'ctime')

    def test_signing_deadline(self):
        self._test_time_field('signing_deadline', u'timeouttime')

    def test_autoremind_time(self):
        self._test_time_field('autoremind_time', u'autoremindtime')

    def test_current_sign_order(self):
        self._test_server_field('current_sign_order')

    def test_authentication_method(self):
        # by default, without signatories it's mixed
        d = self.o()
        self.assertEqual(d.authentication_method, u'mixed')

        # if all signatories have the same method, document has that as well
        s1 = S()
        s2 = S()
        s1.authentication_method = 'sms_pin'
        s2.authentication_method = 'sms_pin'
        d.signatories = set([s1, s2])
        self.assertEqual(d.authentication_method, u'sms_pin')
        s1.authentication_method = 'eleg'
        s2.authentication_method = 'eleg'
        self.assertEqual(d.authentication_method, u'eleg')

        # if signatories have different methods, document has mixed
        s2.authentication_method = 'standard'
        self.assertEqual(d.authentication_method, u'mixed')

    def test_invitation_delivery_method(self):
        # by default, without signatories it's mixed
        d = self.o()
        self.assertEqual(d.invitation_delivery_method, u'mixed')

        # if all signatories have the same method, document has that as well
        s1 = S()
        s2 = S()
        s1.invitation_delivery_method = 'email'
        s2.invitation_delivery_method = 'email'
        d.signatories = set([s1, s2])
        self.assertEqual(d.invitation_delivery_method, u'email')
        s1.invitation_delivery_method = 'api'
        s2.invitation_delivery_method = 'api'
        self.assertEqual(d.invitation_delivery_method, u'api')

        # if signatories have different methods, document has mixed
        s2.invitation_delivery_method = 'pad'
        self.assertEqual(d.invitation_delivery_method, u'mixed')

    def test_is_template(self):
        self._test_field('is_template',
                         bad_value=[], correct_type=bool,
                         default_good_value=False,
                         other_good_values=[True],
                         serialized_name=u'template')

    def test_number_of_days_to_remind(self):
        self._test_field('number_of_days_to_remind',
                         bad_value=[], correct_type='int, float or NoneType',
                         default_good_value=None,
                         other_good_values=[1, 20.],
                         serialized_name=u'daystoremind')
