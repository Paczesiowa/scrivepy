import time
from datetime import datetime

from dateutil import tz

from scrivepy import (
    AuthenticationMethod as AM,
    AuthorAttachment as AA,
    InvitationDeliveryMethod as IDM,
    DocumentStatus as DS,
    DeletionStatus as DelS,
    Language as Lang
)
from tests import utils


class ScriveTest(utils.IntegrationTestCase):

    @utils.integration
    def test_create_document_from_file(self):
        with self.new_document_from_file() as d:
            now = datetime.now(tz.tzutc())

            self.assertEqual(d.title, u'document')
            self.assertTrue(abs((d.creation_time - now).total_seconds()) < 120)
            self.assertEqual(len(list(d.signatories)), 1)
            self.assertIsNotNone(d.id)
            self.assertEqual(d.number_of_days_to_sign, 90)
            self.assertEqual(d.status, DS.preparation)
            self.assertTrue(
                abs((d.modification_time - now).total_seconds()) < 120)
            self.assertTrue(
                abs((d.creation_time -
                     d.modification_time).total_seconds()) < 10)
            self.assertIsNone(d.signing_deadline)
            self.assertIsNone(d.autoremind_time)
            self.assertEqual(d.current_sign_order, 1)
            self.assertEqual(d.authentication_method, AM.standard)
            self.assertEqual(d.invitation_delivery_method, IDM.api)
            self.assertFalse(d.is_template)
            self.assertIsNone(d.number_of_days_to_remind)
            self.assertTrue(d.show_header)
            self.assertTrue(d.show_pdf_download)
            self.assertTrue(d.show_reject_option)
            self.assertTrue(d.show_footer)
            self.assertIsNone(d.invitation_message)
            self.assertIsNone(d.confirmation_message)
            self.assertIsNone(d.api_callback_url)

            # this depends on account settings
            # self.assertEqual(d.language, Lang.swedish)

            self.assertEqual(dict(d.tags), {})
            self.assertTrue(d.saved_as_draft)
            self.assertEqual(d.deletion_status, DelS.not_deleted)
            self.assertFalse(d.signing_possible)
            self.assertEqual(d.object_version, 2)
            self.assertEqual(d.timezone, u'Europe/Stockholm')
            self.assertTrue(d.viewed_by_author)
            self.assertIsNotNone(d.access_token)

    @utils.integration
    def test_update_document(self):
        with self.new_document_from_file() as d:
            d.title = u'document2'
            d.number_of_days_to_sign = 21
            sig = list(d.signatories)[0]
            sig.authentication_method = AM.eleg
            sig.invitation_delivery_method = IDM.mobile
            d.show_header = False
            d.show_pdf_download = False
            d.show_reject_option = False
            d.show_footer = False
            d.invitation_message = u'<p>hello</p>'
            d.confirmation_message = u'<p>bye</p>'
            d.api_callback_url = u'http://example.net/'
            d.language = Lang.finnish
            d.tags[u'foo'] = u'bar'
            d.timezone = u'Europe/Warsaw'

            # make sure that modification time is greater than ctime
            time.sleep(1)
            d = self.api.update_document(d)

            now = datetime.now(tz.tzutc())

            self.assertEqual(d.title, u'document2')
            self.assertTrue(abs((d.creation_time - now).total_seconds()) < 120)
            self.assertEqual(len(list(d.signatories)), 1)
            self.assertIsNotNone(d.id)
            self.assertEqual(d.number_of_days_to_sign, 21)
            self.assertEqual(d.status, DS.preparation)
            self.assertTrue(
                abs((d.modification_time - now).total_seconds()) < 120)
            self.assertTrue(d.creation_time < d.modification_time)
            self.assertIsNone(d.signing_deadline)
            self.assertIsNone(d.autoremind_time)
            self.assertEqual(d.current_sign_order, 1)
            self.assertEqual(d.authentication_method, AM.eleg)
            self.assertEqual(d.invitation_delivery_method, IDM.mobile)
            self.assertFalse(d.is_template)
            self.assertIsNone(d.number_of_days_to_remind)
            self.assertFalse(d.show_header)
            self.assertFalse(d.show_pdf_download)
            self.assertFalse(d.show_reject_option)
            self.assertFalse(d.show_footer)
            self.assertEqual(d.invitation_message, u'<p>hello</p>')
            self.assertEqual(d.confirmation_message, u'<p>bye</p>')
            self.assertEqual(d.api_callback_url, u'http://example.net/')
            self.assertEqual(d.language, Lang.finnish)
            self.assertEqual(dict(d.tags), {u'foo': u'bar'})
            self.assertTrue(d.saved_as_draft)
            self.assertEqual(d.deletion_status, DelS.not_deleted)
            self.assertFalse(d.signing_possible)
            self.assertEqual(d.object_version, 3)
            self.assertEqual(d.timezone, u'Europe/Warsaw')
            self.assertTrue(d.viewed_by_author)
            self.assertIsNotNone(d.access_token)

    @utils.integration
    def test_get_document(self):
        with self.new_document_from_file() as d:
            d.title = u'document2'
            d.number_of_days_to_sign = 21
            sig = list(d.signatories)[0]
            sig.authentication_method = AM.eleg
            sig.invitation_delivery_method = IDM.mobile
            d.show_header = False
            d.show_pdf_download = False
            d.show_reject_option = False
            d.show_footer = False
            d.invitation_message = u'hello'
            d.confirmation_message = u'bye'
            d.api_callback_url = u'http://example.net/'
            d.language = Lang.finnish
            d.tags[u'foo'] = u'bar'
            d.timezone = u'Europe/Warsaw'

            d = self.api.update_document(d)
            d2 = self.api.get_document(d.id)

            self.assertEqual(d.title, d2.title)
            self.assertEqual(d.creation_time, d2.creation_time)
            self.assertEqual([s.id for s in d.signatories],
                             [s.id for s in d2.signatories])
            self.assertEqual(d.id, d2.id)
            self.assertEqual(d.number_of_days_to_sign,
                             d2.number_of_days_to_sign)
            self.assertEqual(d.status, d2.status)
            self.assertEqual(d.modification_time, d2.modification_time)
            self.assertEqual(d.signing_deadline, d2.signing_deadline)
            self.assertEqual(d.autoremind_time, d2.autoremind_time)
            self.assertEqual(d.current_sign_order, d2.current_sign_order)
            self.assertEqual(d.authentication_method, d2.authentication_method)
            self.assertEqual(d.invitation_delivery_method,
                             d2.invitation_delivery_method)
            self.assertEqual(d.is_template, d2.is_template)
            self.assertEqual(d.number_of_days_to_remind,
                             d2.number_of_days_to_remind)
            self.assertEqual(d.show_header, d2.show_header)
            self.assertEqual(d.show_pdf_download, d2.show_pdf_download)
            self.assertEqual(d.show_reject_option, d2.show_reject_option)
            self.assertEqual(d.show_footer, d2.show_footer)
            self.assertEqual(d.invitation_message, d2.invitation_message)
            self.assertEqual(d.confirmation_message, d2.confirmation_message)
            self.assertEqual(d.api_callback_url, d2.api_callback_url)
            self.assertEqual(d.language, d2.language)
            self.assertEqual(d.tags, d2.tags)
            self.assertEqual(d.saved_as_draft, d2.saved_as_draft)
            self.assertEqual(d.deletion_status, d2.deletion_status)
            self.assertEqual(d.signing_possible, d2.signing_possible)
            self.assertEqual(d.object_version, d2.object_version)
            self.assertEqual(d.timezone, d2.timezone)
            self.assertEqual(d.viewed_by_author, d2.viewed_by_author)
            self.assertEqual(d.access_token, d2.access_token)

    @utils.integration
    def test_create_document_from_template(self):
        with self.new_document_from_file() as t:
            t.title = u'document2'
            t.number_of_days_to_sign = 21
            sig = list(t.signatories)[0]
            sig.authentication_method = AM.eleg
            sig.invitation_delivery_method = IDM.mobile
            t.show_header = False
            t.show_pdf_download = False
            t.show_reject_option = False
            t.show_footer = False
            t.invitation_message = u'<p>hello</p>'
            t.confirmation_message = u'<p>bye</p>'
            t.api_callback_url = u'http://example.net/'
            t.language = Lang.finnish
            t.tags[u'foo'] = u'bar'
            t.timezone = u'Europe/Warsaw'

            t.is_template = True

            # make sure that modification time is greater than ctime
            time.sleep(1)
            self.api.update_document(t)

            with self.new_document_from_template(t.id) as d:
                now = datetime.now(tz.tzutc())

                self.assertEqual(d.title, u'document2')
                self.assertTrue(
                    abs((d.creation_time - now).total_seconds()) < 120)
                self.assertEqual(len(list(d.signatories)), 1)
                self.assertIsNotNone(d.id)
                self.assertNotEqual(t.id, d.id)
                self.assertEqual(d.number_of_days_to_sign, 21)
                self.assertEqual(d.status, DS.preparation)
                self.assertTrue(
                    abs((d.modification_time - now).total_seconds()) < 120)
                self.assertEqual(d.creation_time, d.modification_time)
                self.assertIsNone(d.signing_deadline)
                self.assertIsNone(d.autoremind_time)
                self.assertEqual(d.current_sign_order, 1)
                self.assertEqual(d.authentication_method, AM.eleg)
                self.assertEqual(d.invitation_delivery_method, IDM.mobile)
                self.assertFalse(d.is_template)
                self.assertIsNone(d.number_of_days_to_remind)
                self.assertFalse(d.show_header)
                self.assertFalse(d.show_pdf_download)
                self.assertFalse(d.show_reject_option)
                self.assertFalse(d.show_footer)
                self.assertEqual(d.invitation_message, u'<p>hello</p>')
                self.assertEqual(d.confirmation_message, u'<p>bye</p>')
                self.assertEqual(d.api_callback_url, u'http://example.net/')
                self.assertEqual(d.language, Lang.finnish)
                self.assertEqual(dict(d.tags), {u'foo': u'bar'})
                self.assertTrue(d.saved_as_draft)
                self.assertEqual(d.deletion_status, DelS.not_deleted)
                self.assertFalse(d.signing_possible)
                self.assertEqual(d.object_version, 3)  # WTF?
                self.assertEqual(d.timezone, u'Europe/Warsaw')
                self.assertTrue(d.viewed_by_author)
                self.assertIsNotNone(d.access_token)

    @utils.integration
    def test_ready(self):
        with self.new_document_from_file() as d:
            self.assertEqual(d.status, DS.preparation)

            # make sure that modification time is greater than ctime
            time.sleep(1)

            # make sure there's no email from running this test
            author = list(d.signatories)[0]
            author.viewer = True
            d = self.api.update_document(d)

            d = self.api.ready(d)

            self.assertTrue(d._read_only)

            now = datetime.now(tz.tzutc())

            self.assertEqual(d.title, u'document')
            self.assertTrue(abs((d.creation_time - now).total_seconds()) < 120)
            self.assertEqual(len(list(d.signatories)), 1)
            self.assertIsNotNone(d.id)
            self.assertEqual(d.number_of_days_to_sign, 90)
            self.assertEqual(d.status, DS.pending)
            self.assertTrue(
                abs((d.modification_time - now).total_seconds()) < 120)
            self.assertTrue(d.creation_time < d.modification_time)
            self.assertTrue(89 <= (d.signing_deadline - now).days <= 90)
            self.assertIsNone(d.autoremind_time)
            self.assertEqual(d.current_sign_order, 1)
            self.assertEqual(d.authentication_method, AM.standard)
            self.assertEqual(d.invitation_delivery_method, IDM.api)
            self.assertFalse(d.is_template)
            self.assertIsNone(d.number_of_days_to_remind)
            self.assertTrue(d.show_header)
            self.assertTrue(d.show_pdf_download)
            self.assertTrue(d.show_reject_option)
            self.assertTrue(d.show_footer)
            self.assertIsNone(d.invitation_message)
            self.assertIsNone(d.confirmation_message)
            self.assertIsNone(d.api_callback_url)

            # this depends on account settings
            # self.assertEqual(d.language, Lang.swedish)

            self.assertEqual(dict(d.tags), {})
            self.assertTrue(d.saved_as_draft)
            self.assertEqual(d.deletion_status, DelS.not_deleted)
            self.assertFalse(d.signing_possible)
            self.assertEqual(d.object_version, 4)
            self.assertEqual(d.timezone, u'Europe/Stockholm')
            self.assertTrue(d.viewed_by_author)
            self.assertIsNotNone(d.access_token)

    @utils.integration
    def test_trash_document(self):
        with self.new_document_from_file() as d:
            self.assertEqual(d.deletion_status, DelS.not_deleted)
            doc_id = d.id

            self.api.trash_document(d)
            d = self.api.get_document(doc_id)
            self.assertEqual(d.deletion_status, DelS.in_trash)

    @utils.integration
    def test_delete_document(self):
        d = self.api.create_document_from_file(self.test_doc_path)
        self.assertEqual(d.deletion_status, DelS.not_deleted)
        doc_id = d.id

        d = self.api.get_document(doc_id)

        self.api.delete_document(d)
        d = self.api.get_document(doc_id)
        self.assertEqual(d.deletion_status, DelS.deleted)

    @utils.integration
    def test_set_author_attachments(self):
        contents = self.test_doc_contents

        def file_(n):
            return AA(u'document' + unicode(n) + u'.pdf', contents)

        with self.new_document_from_file() as d:
            d.author_attachments.add(file_(1))
            d = self.api.update_document(d)
            self.assertEqual(1, len(d.author_attachments))
            self.assertEqual(u'document1.pdf',
                             list(d.author_attachments)[0].name)

            att = list(d.author_attachments)[0]
            att.mandatory = True
            att.merge = False

            d.author_attachments.add(file_(2))
            d = self.api.update_document(d)
            self.assertEqual(2, len(d.author_attachments))
            for f in d.author_attachments:
                self.assertTrue(f.name in [u'document1.pdf', u'document2.pdf'])
                self.assertTrue(isinstance(f.id, unicode))
                self.assertTrue(f.id is not u'')
                self.assertPDFsEqual(contents, f.get_bytes())
                if f.name == u'document1.pdf':
                    id1 = f.id
                    self.assertTrue(f.mandatory)
                    self.assertFalse(f.merge)
                else:
                    id2 = f.id
                    self.assertFalse(f.mandatory)
                    self.assertTrue(f.merge)

            remote_file2 = d.author_attachments.get_by_attrs(id=id2)
            d.author_attachments.remove(remote_file2)
            d.author_attachments.add(file_(3))

            d = self.api.update_document(d)
            self.assertEqual(2, len(d.author_attachments))
            for f in d.author_attachments:
                self.assertTrue(f.name in [u'document1.pdf', u'document3.pdf'])
                self.assertTrue(isinstance(f.id, unicode))
                self.assertTrue(f.id is not u'')
                self.assertPDFsEqual(contents, f.get_bytes())
                if f.name == u'document1.pdf':
                    self.assertEqual(f.id, id1)
