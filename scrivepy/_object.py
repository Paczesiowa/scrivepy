import json

from scrivepy import _exceptions


class ScriveObject(object):

    def __init__(self):
        self._invalid = False
        self._read_only = False

    def _to_json(self):
        return json.dumps(self, cls=ScriveObjectEncoder)

    def _check_invalid(self):
        if self._invalid:
            raise _exceptions.InvalidScriveObject()

    def _invalid(self):
        self._invalid = True

    def _read_only(self):
        self._read_only = True

    def _check_getter(self):
        self._check_invalid()

    def _check_setter(self):
        self._check_invalid()
        if self._read_only:
            raise _exceptions.ReadOnlyScriveObject()


class ScriveObjectEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, ScriveObject):
            return obj._to_json_obj()
        return json.JSONEncoder.default(self, obj)
