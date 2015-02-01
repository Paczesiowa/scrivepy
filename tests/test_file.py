import contextlib
import hashlib
import os

from scrivepy import _document, _file, _exceptions
from tests import utils


def md5_file(fpath):
    with open(fpath, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


class FileTest(utils.IntegrationTestCase):

    @classmethod
    def setUpClass(class_):
        super(FileTest, class_).setUpClass()
        class_.orig_md5 = md5_file(class_.test_doc_path)

    @utils.integration
    def test_stream(self):
        d = self.api.create_document_from_file(self.test_doc_path)

        with contextlib.closing(d.original_file.stream()) as f:
            md5 = hashlib.md5(f.read()).hexdigest()

        self.assertEqual(self.orig_md5, md5)

    @utils.integration
    def test_save_as(self):
        d = self.api.create_document_from_file(self.test_doc_path)

        with utils.temporary_file_path() as file_path:
            d.original_file.save_as(file_path)
            md5 = md5_file(file_path)

        self.assertEqual(self.orig_md5, md5)

    @utils.integration
    def test_save_to(self):
        d = self.api.create_document_from_file(self.test_doc_path)

        with utils.temporary_dir() as dir_path:
            file_ = d.original_file
            file_.save_to(dir_path)
            md5 = md5_file(os.path.join(dir_path, file_.name))

        self.assertEqual(self.orig_md5, md5)

    @utils.integration
    def test_get_bytes(self):
        d = self.api.create_document_from_file(self.test_doc_path)

        with utils.temporary_file_path() as file_path:
            result = d.original_file.get_bytes()
            self.assertTrue(isinstance(result, bytes))
            with open(file_path, 'wb') as f:
                f.write(result)
            md5 = md5_file(file_path)

        self.assertEqual(self.orig_md5, md5)

    def test_id(self):
        d = _document.Document()

        err_msg = u'id_ must be unicode, not None'
        with self.assertRaises(TypeError, err_msg):
            _file.ScriveFile(id_=None, name=u'document.pdf', document=d)

        err_msg = u'id_ must be non-empty string, not: '
        with self.assertRaises(ValueError, err_msg):
            _file.ScriveFile(id_=u'', name=u'document.pdf', document=d)

        f = _file.ScriveFile(id_=u'1', name=u'document.pdf',
                             document=d)
        self.assertEqual(f.id, u'1')

        with self.assertRaises(AttributeError):
            f.id = u'2'

        f._set_read_only()
        self.assertEqual(f.id, u'1')

        f._set_invalid()
        with self.assertRaises(_exceptions.InvalidScriveObject):
            f.id

    def test_name(self):
        d = _document.Document()

        err_msg = u'name must be unicode, not None'
        with self.assertRaises(TypeError, err_msg):
            _file.ScriveFile(id_=u'1', name=None, document=d)

        err_msg = u'name must be non-empty string, not: '
        with self.assertRaises(ValueError, err_msg):
            _file.ScriveFile(id_=u'1', name=u'', document=d)

        f = _file.ScriveFile(id_=u'1', name=u'document.pdf',
                             document=d)
        self.assertEqual(f.name, u'document.pdf')

        with self.assertRaises(AttributeError):
            f.name = u'2'

        f._set_read_only()
        self.assertEqual(f.name, u'document.pdf')

        f._set_invalid()
        with self.assertRaises(_exceptions.InvalidScriveObject):
            f.id

    def test_document(self):
        d = _document.Document()

        err_msg = u'document must be Document, not None'
        with self.assertRaises(TypeError, err_msg):
            _file.ScriveFile(id_=u'1', name=u'document.pdf', document=None)

        f = _file.ScriveFile(id_=u'1', name=u'document.pdf',
                             document=d)

        with self.assertRaises(AttributeError):
            f.document

        with self.assertRaises(AttributeError):
            f.document = d
