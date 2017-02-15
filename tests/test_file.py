import contextlib
import os

from scrivepy import InvalidScriveObject, _file
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

    def test_from_json_obj(self):
        f = _file.RemoteFile._from_json_obj(
            {u'id': u'1', u'name': u'document.pdf'})
        self.assertEqual(f.id, u'1')
        self.assertEqual(f.name, u'document.pdf')

    def test_id(self):
        err_msg = u'id_ must be unicode or str, not None'
        with self.assertRaises(TypeError, err_msg):
            _file.RemoteFile(id_=None, name=u'document.pdf')

        with self.assertRaises(ValueError, u'id_ must be non-empty string'):
            _file.RemoteFile(id_=u'', name=u'document.pdf')

        f = _file.RemoteFile(id_=u'1', name=u'document.pdf')
        self.assertEqual(f.id, u'1')

        with self.assertRaises(AttributeError):
            f.id = u'2'

        f._set_read_only()
        self.assertEqual(f.id, u'1')

        f._set_invalid()
        with self.assertRaises(InvalidScriveObject):
            f.id

    def test_name(self):
        err_msg = u'name must be unicode or str, not None'
        with self.assertRaises(TypeError, err_msg):
            _file.RemoteFile(id_=u'1', name=None)

        with self.assertRaises(ValueError, u'name must be non-empty string'):
            _file.RemoteFile(id_=u'1', name=u'')

        f = _file.RemoteFile(id_=u'1', name=u'document.pdf')
        self.assertEqual(f.name, u'document.pdf')

        with self.assertRaises(AttributeError):
            f.name = u'2'

        f._set_read_only()
        self.assertEqual(f.name, u'document.pdf')

        f._set_invalid()
        with self.assertRaises(InvalidScriveObject):
            f.name
