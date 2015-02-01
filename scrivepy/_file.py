import contextlib
import os
import shutil

import requests

import type_value_unifier as tvu
from scrivepy import _object


scrive_property = _object.scrive_property


class ScriveFile(_object.ScriveObject):

    @tvu.validate_and_unify(id_=_object.ID,
                            name=tvu.NonEmptyUnicode)
    def __init__(self, id_, name, document):
        # done from funcall, to avoid circular import
        from scrivepy import _document
        doc_validator = tvu.instance(_document.Document)
        document = doc_validator('document').unify_validate(document)

        super(ScriveFile, self).__init__()
        self._id = id_
        self._name = name
        self._document = document

    @scrive_property
    def id(self):
        return self._id

    @scrive_property
    def name(self):
        return self._name

    @property
    def document(self):
        raise AttributeError("can't set attribute")

    def stream(self):
        def stream_get(*args, **kwargs):
            kwargs = dict(kwargs)
            kwargs['stream'] = True
            return requests.get(*args, **kwargs)

        response = self._api._make_request([b'downloadfile', self._document.id,
                                            self.id, self.name],
                                           method=stream_get)
        response.raw.decode_content = True
        return response.raw

    def save_as(self, file_path):
        with contextlib.closing(self.stream()) as s:
            with open(file_path, 'wb') as f:
                shutil.copyfileobj(s, f)

    def save_to(self, dir_path):
        self.save_as(os.path.join(dir_path, self.name))

    def get_bytes(self):
        with contextlib.closing(self.stream()) as s:
            return s.read()
