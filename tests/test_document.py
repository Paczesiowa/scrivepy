import cStringIO
import contextlib
import os
import time

import pyPdf

from scrivepy import (
    AuthorAttachment as AA,
    Signatory as S,
    Document as D,
    DocumentStatus as DS,
    DeletionStatus as DelS,
    Language as Lang,
    InvalidScriveObject,
    ReadOnlyScriveObject,
    Error,
    _document,
    _set,
    _file,
    _unicode_dict
)
from tests import utils


RAA = _document.RemoteAuthorAttachment
ScriveSet = _set.ScriveSet
UnicodeDict = _unicode_dict.UnicodeDict


class AuthorAttachmentTest(utils.IntegrationTestCase):

    @classmethod
    def setUpClass(class_):
        super(AuthorAttachmentTest, class_).setUpClass()
        class_.file_ = AA(u'document.pdf', class_.test_doc_contents)

    def test_stream(self):
        with contextlib.closing(self.file_.stream()) as f:
            self.assertEqual(self.test_doc_contents, f.read())

    def test_get_bytes(self):
        self.assertEqual(self.file_.get_bytes(), self.test_doc_contents)

    def test_from_file_obj(self):
        with open(self.test_doc_path, 'rb') as f:
            file_ = AA.from_file_obj(u'document.pdf', f)
            self.assertEqual(file_.get_bytes(), self.test_doc_contents)

    def test_from_file_path(self):
        file_ = AA.from_file_path(self.test_doc_path)
        self.assertEqual(file_.get_bytes(), self.test_doc_contents)

    def test_save_as(self):
        with utils.temporary_file_path() as file_path:
            self.file_.save_as(file_path)
            with open(file_path, 'rb') as f:
                self.assertEqual(self.test_doc_contents, f.read())

    def test_save_to(self):
        with utils.temporary_dir() as dir_path:
            self.file_.save_to(dir_path)
            with open(os.path.join(dir_path, self.file_.name), 'rb') as f:
                self.assertEqual(self.test_doc_contents, f.read())

    def test_name(self):
        err_msg = u'name must be unicode or str, not None'
        with self.assertRaises(TypeError, err_msg):
            AA(name=None, content=b'')

        with self.assertRaises(ValueError, u'name must be non-empty string'):
            AA(name=u'', content=b'')

        f = AA(name=u'document.pdf', content=b'')
        self.assertEqual(f.name, u'document.pdf')

        with self.assertRaises(AttributeError):
            f.name = u'2'

        f._set_read_only()
        self.assertEqual(f.name, u'document.pdf')

        f._set_invalid()
        with self.assertRaises(InvalidScriveObject):
            f.name

    def test_mandatory(self):
        err_msg = u'mandatory must be bool, not 2'
        with self.assertRaises(TypeError, err_msg):
            AA(name=u'x', content=b'', mandatory=2)

        aa = AA(name=u'document.pdf', content=b'')
        self.assertFalse(aa.mandatory)

        aa.mandatory = True
        self.assertTrue(aa.mandatory)

        err_msg = u'mandatory must be bool, not []'
        with self.assertRaises(TypeError, err_msg):
            aa.mandatory = []

        aa._set_read_only()
        self.assertTrue(aa.mandatory)

        aa._set_invalid()
        with self.assertRaises(InvalidScriveObject):
            aa.mandatory

    def test_merge(self):
        err_msg = u'merge must be bool, not 2'
        with self.assertRaises(TypeError, err_msg):
            AA(name=u'x', content=b'', merge=2)

        aa = AA(name=u'document.pdf', content=b'')
        self.assertTrue(aa.merge)

        aa.merge = False
        self.assertFalse(aa.merge)

        err_msg = u'merge must be bool, not []'
        with self.assertRaises(TypeError, err_msg):
            aa.merge = []

        aa._set_read_only()
        self.assertFalse(aa.merge)

        aa._set_invalid()
        with self.assertRaises(InvalidScriveObject):
            aa.merge


class RemoteAuthorAttachmentTest(utils.IntegrationTestCase):

    @utils.integration
    def test_stream(self):
        with self.new_document_from_file() as d:
            d.author_attachments.add(AA(u'document.pdf',
                                        self.test_doc_contents))
            d = self.api.update_document(d)
            raa = list(d.author_attachments)[0]
            with contextlib.closing(raa.stream()) as f:
                self.assertPDFsEqual(f.read(), self.test_doc_contents)

    @utils.integration
    def test_save_as(self):
        with self.new_document_from_file() as d:
            d.author_attachments.add(AA(u'document.pdf',
                                        self.test_doc_contents))
            d = self.api.update_document(d)
            raa = list(d.author_attachments)[0]
            with utils.temporary_file_path() as file_path:
                raa.save_as(file_path)
                with open(file_path, 'rb') as f:
                    self.assertPDFsEqual(f.read(), self.test_doc_contents)

    @utils.integration
    def test_save_to(self):
        with self.new_document_from_file() as d:
            d.author_attachments.add(AA(u'document.pdf',
                                        self.test_doc_contents))
            d = self.api.update_document(d)
            raa = list(d.author_attachments)[0]
            with utils.temporary_dir() as dir_path:
                raa.save_to(dir_path)
                with open(os.path.join(dir_path, raa.name), 'rb') as f:
                    self.assertPDFsEqual(f.read(), self.test_doc_contents)

    @utils.integration
    def test_get_bytes(self):
        with self.new_document_from_file() as d:
            d.author_attachments.add(AA(u'document.pdf',
                                        self.test_doc_contents))
            d = self.api.update_document(d)
            raa = list(d.author_attachments)[0]
            result = raa.get_bytes()
            self.assertTrue(isinstance(result, bytes))
            self.assertPDFsEqual(result, self.test_doc_contents)

    def test_from_json_obj(self):
        json = {u'id': u'1234', u'name': u'document.pdf',
                u'required': True, u'add_to_sealed_file': False}
        raa = RAA._from_json_obj(json)
        self.assertEqual(raa.id, u'1234')
        self.assertEqual(raa.name, u'document.pdf')
        self.assertTrue(raa.mandatory)
        self.assertFalse(raa.merge)

    def test_id(self):
        err_msg = u'id_ must be unicode or str, not None'
        with self.assertRaises(TypeError, err_msg):
            RAA(id_=None, name=u'document.pdf')

        with self.assertRaises(ValueError, u'id_ must be non-empty string'):
            RAA(id_=u'', name=u'document.pdf')

        raa = RAA(id_=u'1', name=u'document.pdf')
        self.assertEqual(raa.id, u'1')

        with self.assertRaises(AttributeError):
            raa.id = u'2'

        raa._set_read_only()
        self.assertEqual(raa.id, u'1')

        raa._set_invalid()
        with self.assertRaises(InvalidScriveObject):
            raa.id

    def test_name(self):
        err_msg = u'name must be unicode or str, not None'
        with self.assertRaises(TypeError, err_msg):
            RAA(id_=u'1', name=None)

        with self.assertRaises(ValueError, u'name must be non-empty string'):
            RAA(id_=u'1', name=u'')

        raa = RAA(id_=u'1', name=u'document.pdf')
        self.assertEqual(raa.name, u'document.pdf')

        with self.assertRaises(AttributeError):
            raa.name = u'2'

        raa._set_read_only()
        self.assertEqual(raa.name, u'document.pdf')

        raa._set_invalid()
        with self.assertRaises(InvalidScriveObject):
            raa.name

    def test_mandatory(self):
        err_msg = u'mandatory must be bool, not 2'
        with self.assertRaises(TypeError, err_msg):
            RAA(id_=u'1', name=u'x', mandatory=2)

        raa = RAA(id_=u'1', name=u'document.pdf')
        self.assertFalse(raa.mandatory)

        err_msg = u'mandatory must be bool, not 2'
        with self.assertRaises(TypeError, err_msg):
            raa.mandatory = 2

        raa.mandatory = True
        self.assertTrue(raa.mandatory)

        raa._set_read_only()
        self.assertTrue(raa.mandatory)

        raa._set_invalid()
        with self.assertRaises(InvalidScriveObject):
            raa.mandatory

    def test_merge(self):
        err_msg = u'merge must be bool, not 2'
        with self.assertRaises(TypeError, err_msg):
            RAA(id_=u'1', name=u'x', merge=2)

        raa = RAA(id_=u'1', name=u'document.pdf')
        self.assertTrue(raa.merge)

        err_msg = u'merge must be bool, not 2'
        with self.assertRaises(TypeError, err_msg):
            raa.merge = 2

        raa.merge = False
        self.assertFalse(raa.merge)

        raa._set_read_only()
        self.assertFalse(raa.merge)

        raa._set_invalid()
        with self.assertRaises(InvalidScriveObject):
            raa.merge


class DocumentTest(utils.IntegrationTestCase):

    def setUp(self):
        self.O = D
        self.s1_json = {u'id': u'1',
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
                        u'allowshighlighting': True,
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
                        u'attachments': [],
                        u'fields': []}
        self.s1 = S._from_json_obj(self.s1_json)
        s2_json = self.s1_json.copy()
        s2_json[u'id'] = u'2'
        s2_json[u'author'] = False
        s2_json[u'signs'] = True
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
                     u'showheader': False,
                     u'showpdfdownload': False,
                     u'showrejectoption': False,
                     u'allowrejectreason': False,
                     u'showfooter': False,
                     u'invitationmessage': u'',
                     u'confirmationmessage': u'',
                     u'apicallbackurl': u'http://example.net/',
                     u'lang': u'pt',
                     u'tags': [{u'name': u'key1', u'value': u'val1'},
                               {u'name': u'key2', u'value': u'val2'}],
                     u'saved': True,
                     u'deleted': False,
                     u'reallydeleted': False,
                     u'canperformsigning': True,
                     u'objectversion': 1,
                     u'timezone': u'Europe/Berlin',
                     u'isviewedbyauthor': True,
                     u'accesstoken': u'1234567890abcdef',
                     u'authorattachments': [],
                     u'signatories': [self.s1_json, s2_json]}

    def o(self, *args, **kwargs):
        d = D._private_ctor()
        for arg, val in kwargs.items():
            setattr(d, arg, val)
        return d

    def test_flags(self):
        s1 = S()
        s1._author = True
        s2 = S(viewer=True)
        d = self.o()
        d.signatories.update([s1, s2])

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
        self.assertRaises(ReadOnlyScriveObject, None,
                          d._check_setter)
        self.assertRaises(ReadOnlyScriveObject, None,
                          s1._check_setter)
        self.assertRaises(ReadOnlyScriveObject, None,
                          s2._check_setter)

        d._set_invalid()
        self.assertRaises(InvalidScriveObject, None,
                          d._check_getter)
        self.assertRaises(InvalidScriveObject, None,
                          s1._check_getter)
        self.assertRaises(InvalidScriveObject, None,
                          s2._check_getter)
        self.assertRaises(InvalidScriveObject, None,
                          d._check_setter)
        self.assertRaises(InvalidScriveObject, None,
                          s1._check_setter)
        self.assertRaises(InvalidScriveObject, None,
                          s2._check_setter)

    def test_to_json_obj(self):
        d = self.o(title=u'the document',
                   number_of_days_to_sign=30,
                   number_of_days_to_remind=20,
                   is_template=True,
                   show_header=False,
                   show_pdf_download=False,
                   show_reject_option=False,
                   show_reject_reason=False,
                   show_footer=False,
                   invitation_message=u'some text',
                   confirmation_message=u'some confirmation text',
                   api_callback_url=u'http://example.com/',
                   language='spanish',
                   saved_as_draft=False,
                   timezone=u'Europe/Warsaw')
        d.signatories.add(self.s1)
        d.tags.update({u'key1': u'val2', u'key3': u'val4'})

        json = {u'title': u'the document',
                u'daystosign': 30,
                u'daystoremind': 20,
                u'template': True,
                u'showheader': False,
                u'showpdfdownload': False,
                u'showrejectoption': False,
                u'allowrejectreason': False,
                u'showfooter': False,
                u'invitationmessage': u'some text',
                u'confirmationmessage': u'some confirmation text',
                u'apicallbackurl': u'http://example.com/',
                u'lang': u'es',
                u'tags': [{u'name': u'key1', u'value': u'val2'},
                          {u'name': u'key3', u'value': u'val4'}],
                u'saved': False,
                u'timezone': u'Europe/Warsaw',
                u'authorattachments': [],
                u'signatories': [self.s1]}

        d_json = d._to_json_obj()
        d_json[u'tags'] = sorted(d_json[u'tags'], key=lambda x: x[u'name'])

        self.assertEqual(json, d_json)

    def test_from_json_obj(self):
        d = D._from_json_obj(self.json)
        self.assertEqual(d.id, u'1234')
        self.assertEqual(d.title, u'a document')
        self.assertEqual(d.number_of_days_to_sign, 20)
        self.assertEqual(d.number_of_days_to_remind, 10)
        self.assertEqual(d.status, DS.pending)
        self.assertIsNone(d.modification_time)
        self.assertIsNone(d.creation_time)
        self.assertIsNone(d.signing_deadline)
        self.assertIsNone(d.autoremind_time)
        self.assertEqual(d.current_sign_order, 1)
        self.assertEqual(d.authentication_method, u'standard')
        self.assertEqual(d.invitation_delivery_method, u'email')
        self.assertTrue(d.is_template)
        self.assertFalse(d.show_header)
        self.assertFalse(d.show_pdf_download)
        self.assertFalse(d.show_reject_option)
        self.assertFalse(d.show_reject_reason)
        self.assertFalse(d.show_footer)
        self.assertIsNone(d.invitation_message)
        self.assertIsNone(d.confirmation_message)
        self.assertEqual(d.api_callback_url, u'http://example.net/')
        self.assertEqual(d.language, Lang.portuguese)
        self.assertTrue(d.saved_as_draft)
        self.assertEqual(d.deletion_status, DelS.not_deleted)
        self.assertTrue(d.signing_possible)
        self.assertEqual(d.object_version, 1)
        self.assertEqual(d.timezone, u'Europe/Berlin')
        self.assertTrue(d.viewed_by_author)
        self.assertEqual(d.access_token, u'1234567890abcdef')
        self.assertEqual(sorted([s._to_json_obj()
                                 for s in d.signatories]),
                         sorted([self.s1._to_json_obj(),
                                 self.s2._to_json_obj()]))

    def test_signatories(self):
        # check default ctor value
        d = self.o()
        self.assertEqual(ScriveSet(), d.signatories)

        d.signatories.add(self.s1)
        self.assertEqual(ScriveSet([self.s1]), d.signatories)

        err_msg = u'elem must be Signatory, not 1'
        with self.assertRaises(TypeError, err_msg):
            d.signatories.add(1)

        d.signatories.clear()
        d.signatories.add(self.s2)
        self.assertEqual(ScriveSet([self.s2]), d.signatories)

        self.assertEqual([self.s2], d._to_json_obj()[u'signatories'])

        d._set_read_only()
        # set() is because the 2nd one is read only and not really equal
        self.assertEqual(set(ScriveSet([self.s2])), set(d.signatories))
        with self.assertRaises(ReadOnlyScriveObject, None):
            d.signatories.clear()
            d.signatories.add(self.s1)

        sigs = d.signatories
        d._set_invalid()
        with self.assertRaises(InvalidScriveObject, None):
            d.signatories
        with self.assertRaises(InvalidScriveObject, None):
            sigs.add(self.s1)

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
        d.signatories.update([s1, s2])
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
        d.signatories.update([s1, s2])
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
                         bad_value=[], correct_type='int, float or None',
                         default_good_value=None,
                         other_good_values=[1, 20.],
                         serialized_name=u'daystoremind')

    def test_show_header(self):
        self._test_field('show_header',
                         bad_value=[], correct_type=bool,
                         default_good_value=True,
                         other_good_values=[False],
                         serialized_name=u'showheader')

    def test_show_pdf_download(self):
        self._test_field('show_pdf_download',
                         bad_value=[], correct_type=bool,
                         default_good_value=True,
                         other_good_values=[False],
                         serialized_name=u'showpdfdownload')

    def test_show_reject_option(self):
        self._test_field('show_reject_option',
                         bad_value=[], correct_type=bool,
                         default_good_value=True,
                         other_good_values=[False],
                         serialized_name=u'showrejectoption')

    def test_show_reject_reason(self):
        self._test_field('show_reject_reason',
                         bad_value=[], correct_type=bool,
                         default_good_value=True,
                         other_good_values=[False],
                         serialized_name=u'allowrejectreason')

    def test_show_footer(self):
        self._test_field('show_footer',
                         bad_value=[], correct_type=bool,
                         default_good_value=True,
                         other_good_values=[False],
                         serialized_name=u'showfooter')

    def test_invitation_message(self):
        self._test_field('invitation_message',
                         bad_value={}, correct_type='unicode or None',
                         default_good_value=None,
                         other_good_values=[u'some text'],
                         serialized_name=u'invitationmessage',
                         serialized_default_good_value=u'')
        d1 = self.o()
        self.assertIsNone(d1.invitation_message)
        for x in [None, u'', u'   ', u'  \n  ']:
            d1.invitation_message = x

            d2 = self.o(invitation_message=x)

            json = self.json.copy()
            json[u'invitationmessage'] = x

            d3 = self.O._from_json_obj(json)

            for d in [d1, d2, d3]:
                self.assertEqual(u'', d._to_json_obj()[u'invitationmessage'])
                self.assertIsNone(d.invitation_message)

    def test_confirmation_message(self):
        self._test_field('confirmation_message',
                         bad_value={}, correct_type='unicode or None',
                         default_good_value=None,
                         other_good_values=[u'some text'],
                         serialized_name=u'confirmationmessage',
                         serialized_default_good_value=u'')
        d1 = self.o()
        self.assertIsNone(d1.confirmation_message)
        for x in [None, u'', u'   ', u'  \n  ']:
            d1.confirmation_message = x

            d2 = self.o(confirmation_message=x)

            json = self.json.copy()
            json[u'confirmationmessage'] = x

            d3 = self.O._from_json_obj(json)

            for d in [d1, d2, d3]:
                self.assertEqual(u'', d._to_json_obj()[u'confirmationmessage'])
                self.assertIsNone(d.confirmation_message)

    def test_api_callback_url(self):
        self._test_field('api_callback_url',
                         bad_value=[], correct_type='unicode or None',
                         default_good_value=None,
                         other_good_values=[u'http://example.com/'],
                         serialized_name=u'apicallbackurl')

    def test_language(self):
        self._test_field('language',
                         bad_value={}, correct_type=Lang,
                         default_good_value=Lang.swedish,
                         other_good_values=[Lang.english,
                                            ('greek', Lang.greek),
                                            Lang.finnish],
                         serialized_name=u'lang',
                         bad_enum_value='wrong')

        json = self.json.copy()
        json[u'lang'] = u'gb'
        d = self.O._from_json_obj(json)
        self.assertEqual(d.language, Lang.english)

    def test_tags(self):
        # check default ctor value
        d = self.o()
        self.assertEqual(UnicodeDict(), d.tags)

        d.tags[u'foo'] = u'bar'
        self.assertEqual(UnicodeDict(foo=u'bar'), d.tags)

        err_msg = u'value must be unicode or str, not 1'
        with self.assertRaises(TypeError, err_msg):
            d.tags[u'baz'] = 1

        d.tags.clear()
        d.tags[u'foo'] = u'baz'
        self.assertEqual(UnicodeDict(foo=u'baz'), d.tags)

        self.assertEqual([{u'name': u'foo', u'value': u'baz'}],
                         d._to_json_obj()[u'tags'])

        d._set_read_only()
        # set() is because the 2nd one is read only and not really equal
        self.assertEqual(dict(UnicodeDict(foo=u'baz')), dict(d.tags))
        with self.assertRaises(ReadOnlyScriveObject, None):
            d.tags.clear()
            d.tags[u'foo'] = u'bar'

        tags = d.tags
        d._set_invalid()
        with self.assertRaises(InvalidScriveObject, None):
            d.tags
        with self.assertRaises(InvalidScriveObject, None):
            tags[u'foo'] = u'bar'

    def test_saved_as_draft(self):
        self._test_field('saved_as_draft',
                         bad_value=[], correct_type=bool,
                         default_good_value=False,
                         other_good_values=[True],
                         serialized_name=u'saved')

    def test_deletion_status(self):
        json = self.json.copy()

        json[u'deleted'] = True
        json[u'reallydeleted'] = False
        self.assertEqual(self.O._from_json_obj(json).deletion_status,
                         DelS.in_trash)

        json[u'deleted'] = True
        json[u'reallydeleted'] = True
        self.assertEqual(self.O._from_json_obj(json).deletion_status,
                         DelS.deleted)

    def test_signing_possible(self):
        self._test_server_field('signing_possible')

    def test_object_version(self):
        self._test_server_field('object_version')

    def test_timezone(self):
        self._test_field('timezone',
                         bad_value=[], correct_type=unicode,
                         default_good_value=u'Europe/Stockholm',
                         other_good_values=[u'Europe/Berlin'])

    def test_viewed_by_author(self):
        self._test_server_field('viewed_by_author')

    def test_access_token(self):
        self._test_server_field('access_token')

    def test_document_read_only_by_status(self):
        json = self.json.copy()
        for status in ['pending', 'closed', 'canceled',
                       'timedout', 'rejected', 'error']:
            json['status'] = DS[status].value
            d = self.O._from_json_obj(json)
            self.assertTrue(d._read_only)
        json['status'] = DS['preparation'].value
        d = self.O._from_json_obj(json)
        self.assertFalse(d._read_only)

    def test_original_file(self):
        json = self.json.copy()
        json[u'file'] = {u'id': u'1', u'name': u'document.pdf'}
        d = self.O._from_json_obj(json)

        d._set_read_only()
        self.assertTrue(d.original_file._read_only)

        d._set_invalid()
        with self.assertRaises(InvalidScriveObject, None):
            d.original_file.get_bytes()

    @utils.integration
    def test_sealed_document(self):
        with self.new_document_from_file() as d:
            file_contents = d.original_file.get_bytes()
            with contextlib.closing(cStringIO.StringIO(file_contents)) as s:
                self.assertEqual(1, pyPdf.PdfFileReader(s).getNumPages())
            self.assertIsNone(d.sealed_document)
            d = self.api.ready(d)
            self.assertIsNone(d.sealed_document)
            author = d.author
            d = self.api._sign(d, author)
            self.assertIsNone(d.sealed_document)

            # wait for sealing to be completed, and refresh
            time.sleep(10)
            d = self.api.get_document(d.id)

            self.assertIsNotNone(d.sealed_document)

            file_contents = d.sealed_document.get_bytes()
            with contextlib.closing(cStringIO.StringIO(file_contents)) as s:
                self.assertEqual(2, pyPdf.PdfFileReader(s).getNumPages())

            d._set_read_only()
            self.assertTrue(d.sealed_document._read_only)

            d._set_invalid()
            with self.assertRaises(InvalidScriveObject, None):
                d.sealed_document.get_bytes()

    def test_author_attachments(self):
        json = self.json.copy()
        json[u'status'] = u'Preparation'  # so it's not read only
        d = self.O._from_json_obj(json)
        self.assertEqual(d.author_attachments, ScriveSet())
        json[u'authorattachments'] = [{u'id': u'1', u'name': u'document1.pdf',
                                       u'required': True,
                                       u'add_to_sealed_file': False},
                                      {u'id': u'2', u'name': u'document2.pdf',
                                       u'required': False,
                                       u'add_to_sealed_file': True}]
        d2 = self.O._from_json_obj(json)
        self.assertEqual(2, len(d2.author_attachments))
        for file_ in d2.author_attachments:
            if file_.id == u'1':
                self.assertEqual(file_.name, u'document1.pdf')
            else:
                self.assertEqual(file_.name, u'document2.pdf')

        file2 = filter(lambda f: f.id == u'2', d2.author_attachments)[0]
        d2.author_attachments.remove(file2)
        file1 = list(d2.author_attachments)[0]
        self.assertEqual([file1], d2._to_json_obj()[u'authorattachments'])

        type_err_msg = (u'elem must be AuthorAttachment, not '
                        u'<scrivepy._document.RemoteAuthorAttachment '
                        u'object at .*')
        with self.assertRaisesRegexp(TypeError, type_err_msg):
            d2.author_attachments.add(file1)

        d2._set_read_only()
        # set() is because the 2nd one is read only and not really equal
        self.assertEqual(set(ScriveSet([file1])), set(d2.author_attachments))
        with self.assertRaises(ReadOnlyScriveObject, None):
            d2.author_attachments.clear()
            d2.author_attachments.add(_file.LocalFile(u'x', b''))

        atts = d2.author_attachments
        d2._set_invalid()
        with self.assertRaises(InvalidScriveObject, None):
            d2.author_attachments
        with self.assertRaises(InvalidScriveObject, None):
            atts.add(AA(u'x', b''))

    def test_author(self):
        json = self.json.copy()
        json[u'status'] = u'Preparation'  # so it's not read only
        json[u'signatories'] = []
        d = self.O._from_json_obj(json)

        with self.assertRaises(Error, u'No author'):
            d.author
        d._set_read_only()
        with self.assertRaises(Error, u'No author'):
            d.author
        d._set_invalid()
        with self.assertRaises(InvalidScriveObject, None):
            d.author

        json = self.json.copy()
        json[u'status'] = u'Preparation'  # so it's not read only
        s1_json = self.s1_json.copy()
        s1_json[u'author'] = False
        s2_json = self.s1_json.copy()
        s2_json[u'author'] = False
        json[u'signatories'] = [s1_json, s2_json]
        d = self.O._from_json_obj(json)

        with self.assertRaises(Error, u'No author'):
            d.author
        d._set_read_only()
        with self.assertRaises(Error, u'No author'):
            d.author
        d._set_invalid()
        with self.assertRaises(InvalidScriveObject, None):
            d.author

        json = self.json.copy()
        json[u'status'] = u'Preparation'  # so it's not read only
        s1_json = self.s1_json.copy()
        s1_json[u'author'] = True
        s2_json = self.s1_json.copy()
        s2_json[u'author'] = True
        json[u'signatories'] = [s1_json, s2_json]
        d = self.O._from_json_obj(json)

        with self.assertRaises(Error, u'Multiple authors'):
            d.author
        d._set_read_only()
        with self.assertRaises(Error, u'Multiple authors'):
            d.author
        d._set_invalid()
        with self.assertRaises(InvalidScriveObject, None):
            d.author

        json = self.json.copy()
        json[u'status'] = u'Preparation'  # so it's not read only
        s1_json = self.s1_json.copy()
        s1_json[u'author'] = False
        s2_json = self.s1_json.copy()
        s2_json[u'author'] = True
        json[u'signatories'] = [s1_json, s2_json]
        d = self.O._from_json_obj(json)

        self.assertEqual(d.author.id, s1_json[u'id'])
        d._set_read_only()
        self.assertEqual(d.author.id, s1_json[u'id'])
        d._set_invalid()
        with self.assertRaises(InvalidScriveObject, None):
            d.author

        d = self.o()
        with self.assertRaises(AttributeError, None):
            d.author = 2
        d._set_read_only()
        with self.assertRaises(AttributeError, None):
            d.author = 2
        d._set_invalid()
        with self.assertRaises(AttributeError, None):
            d.author = 2

    def test_other_parties(self):
        json = self.json.copy()

        s1_json = self.s1_json.copy()
        s1_json[u'id'] = u'1'
        s1_json[u'author'] = True
        s2_json = self.s1_json.copy()
        s2_json[u'id'] = u'2'
        s2_json[u'author'] = False
        s2_json[u'signs'] = True
        s3_json = self.s1_json.copy()
        s3_json[u'id'] = u'3'
        s3_json[u'author'] = False
        s3_json[u'signs'] = False
        json[u'signatories'] = [s1_json, s2_json, s3_json]
        d = self.O._from_json_obj(json)
        others = list(d.other_parties())
        self.assertEqual(2, len(others))
        self.assertEqual(set([u'2', u'3']), set(map(lambda s: s.id, others)))

        d._set_invalid()
        with self.assertRaises(InvalidScriveObject, None):
            list(d.other_parties())

    def test_other_signatories(self):
        json = self.json.copy()

        s1_json = self.s1_json.copy()
        s1_json[u'id'] = u'1'
        s1_json[u'author'] = True
        s2_json = self.s1_json.copy()
        s2_json[u'id'] = u'2'
        s2_json[u'author'] = False
        s2_json[u'signs'] = True
        s3_json = self.s1_json.copy()
        s3_json[u'id'] = u'3'
        s3_json[u'author'] = False
        s3_json[u'signs'] = False
        json[u'signatories'] = [s1_json, s2_json, s3_json]
        d = self.O._from_json_obj(json)
        self.assertEqual([u'2'], map(lambda s: s.id, d.other_signatories()))

        d._set_invalid()
        with self.assertRaises(InvalidScriveObject, None):
            list(d.other_signatories())

    def test_other_signatory(self):
        json = self.json.copy()

        s1_json = self.s1_json.copy()
        s1_json[u'id'] = u'1'
        s1_json[u'author'] = True
        s2_json = self.s1_json.copy()
        s2_json[u'id'] = u'2'
        s2_json[u'author'] = False
        s2_json[u'signs'] = True
        s3_json = self.s1_json.copy()
        s3_json[u'id'] = u'3'
        s3_json[u'author'] = False
        s3_json[u'signs'] = False

        json[u'signatories'] = [s1_json, s2_json, s3_json]
        d = self.O._from_json_obj(json)
        self.assertEqual(u'2', d.other_signatory().id)

        s3_json[u'signs'] = True
        d = self.O._from_json_obj(json)
        err_msg = u'Multiple signatories'
        with self.assertRaises(Error, err_msg):
            d.other_signatory()

        s2_json[u'signs'] = False
        s3_json[u'signs'] = False
        d = self.O._from_json_obj(json)
        err_msg = u'No other signatories'
        with self.assertRaises(Error, err_msg):
            d.other_signatory()

        d._set_invalid()
        with self.assertRaises(InvalidScriveObject, None):
            list(d.other_signatories())

    def test_private_ctor(self):
        msg = u'Dont create Document objects directly. Use Scrive object.'
        with self.assertRaises(TypeError, msg):
            D()
