import contextlib
import os

from scrivepy import _document, _file, _exceptions
from tests import utils


class RemoteFileTest(utils.IntegrationTestCase):

    @utils.integration
    def test_stream(self):
        with self.new_document_from_file() as d:
            with contextlib.closing(d.original_file.stream()) as f:
                self.assertPDFsEqual(f.read(), self.test_doc_contents)

    @utils.integration
    def test_save_as(self):
        with self.new_document_from_file() as d:
            with utils.temporary_file_path() as file_path:
                d.original_file.save_as(file_path)
                with open(file_path, 'rb') as f:
                    self.assertPDFsEqual(f.read(), self.test_doc_contents)

    @utils.integration
    def test_save_to(self):
        with self.new_document_from_file() as d:
            with utils.temporary_dir() as dir_path:
                file_ = d.original_file
                file_.save_to(dir_path)
                with open(os.path.join(dir_path, file_.name), 'rb') as f:
                    self.assertPDFsEqual(f.read(), self.test_doc_contents)

    @utils.integration
    def test_get_bytes(self):
        with self.new_document_from_file() as d:
            result = d.original_file.get_bytes()
            self.assertTrue(isinstance(result, bytes))
            self.assertPDFsEqual(result, self.test_doc_contents)

    def test_to_json_obj(self):
        f = _file.RemoteFile(id_=u'1', name=u'document.pdf')
        json = {u'id': u'1', u'name': u'document.pdf'}
        self.assertEqual(json, f._to_json_obj())

    def test_id(self):
        err_msg = u'id_ must be unicode, not None'
        with self.assertRaises(TypeError, err_msg):
            _file.RemoteFile(id_=None, name=u'document.pdf')

        err_msg = u'id_ must be non-empty string, not: '
        with self.assertRaises(ValueError, err_msg):
            _file.RemoteFile(id_=u'', name=u'document.pdf')

        f = _file.RemoteFile(id_=u'1', name=u'document.pdf')
        self.assertEqual(f.id, u'1')

        with self.assertRaises(AttributeError):
            f.id = u'2'

        f._set_read_only()
        self.assertEqual(f.id, u'1')

        f._set_invalid()
        with self.assertRaises(_exceptions.InvalidScriveObject):
            f.id

    def test_name(self):
        err_msg = u'name must be unicode, not None'
        with self.assertRaises(TypeError, err_msg):
            _file.RemoteFile(id_=u'1', name=None)

        err_msg = u'name must be non-empty string, not: '
        with self.assertRaises(ValueError, err_msg):
            _file.RemoteFile(id_=u'1', name=u'')

        f = _file.RemoteFile(id_=u'1', name=u'document.pdf')
        self.assertEqual(f.name, u'document.pdf')

        with self.assertRaises(AttributeError):
            f.name = u'2'

        f._set_read_only()
        self.assertEqual(f.name, u'document.pdf')

        f._set_invalid()
        with self.assertRaises(_exceptions.InvalidScriveObject):
            f.name

    def test_document(self):
        d = _document.Document()
        f = _file.RemoteFile(id_=u'1', name=u'document.pdf')

        with self.assertRaises(AttributeError):
            f.document

        with self.assertRaises(AttributeError):
            f.document = d


class LocalFileTest(utils.IntegrationTestCase):

    @classmethod
    def setUpClass(class_):
        super(LocalFileTest, class_).setUpClass()
        class_.file_ = _file.LocalFile(u'document.pdf',
                                       class_.test_doc_contents)

    def test_stream(self):
        with contextlib.closing(self.file_.stream()) as f:
            self.assertEqual(self.test_doc_contents, f.read())

    def test_get_bytes(self):
        self.assertEqual(self.file_.get_bytes(), self.test_doc_contents)

    def test_from_file_obj(self):
        with open(self.test_doc_path, 'rb') as f:
            file_ = _file.LocalFile.from_file_obj(u'document.pdf', f)
            self.assertEqual(file_.get_bytes(), self.test_doc_contents)

    def test_from_file_path(self):
        file_ = _file.LocalFile.from_file_path(self.test_doc_path)
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
        err_msg = u'name must be unicode, not None'
        with self.assertRaises(TypeError, err_msg):
            _file.LocalFile(name=None, content=b'')

        err_msg = u'name must be non-empty string, not: '
        with self.assertRaises(ValueError, err_msg):
            _file.LocalFile(name=u'', content=b'')

        f = _file.LocalFile(name=u'document.pdf', content=b'')
        self.assertEqual(f.name, u'document.pdf')

        with self.assertRaises(AttributeError):
            f.name = u'2'

        f._set_read_only()
        self.assertEqual(f.name, u'document.pdf')

        f._set_invalid()
        with self.assertRaises(_exceptions.InvalidScriveObject):
            f.name
