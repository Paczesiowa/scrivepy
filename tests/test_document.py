# coding: utf-8
from scrivepy import (
    Document,
    DocumentStatus,
    Signatory)
from tests.utils import IntegrationTestCase


class DocumentTest(IntegrationTestCase):

    O = Document
    default_ctor_kwargs = {}
    json = {u'id': u'123', u'title': u'Document', u'parties': [],
            u'ctime': u'2017-04-22T12:56:00Z', u'status': u'preparation',
            u'mtime': u'2017-04-22T12:56:00Z',
            u'timeout_time': None, u'auto_remind_time': None}

    def make_signatory(self, num=1):
        json = {u'id': u'123', u'user_id': u'456', u'is_author': False,
                u'is_signatory': False, u'fields': [], u'sign_order': 1,
                u'sign_time': None, u'seen_time': None,
                u'read_invitation_time': None,
                u'rejected_time': None,
                u'sign_success_redirect_url': u'',
                u'reject_redirect_url': u'',
                u'email_delivery_status': u'unknown',
                u'mobile_delivery_status': u'unknown',
                u'delivery_method': u'email',
                u'confirmation_delivery_method': u'email',
                u'authentication_method_to_view': u'standard',
                u'authentication_method_to_sign': u'standard',
                u'allows_highlighting': False,
                u'api_delivery_url': None}
        if num == 2:
            json[u'is_author'] = False
            json[u'id'] = u'789'
        return json

    def test_id(self):
        self._test_remote_id(attr_name='id', skip_preservation=False)

    def test_title(self):
        self._test_non_empty_text(attr_name='title', required=False,
                                  default_value=u'document')

    def test_parties(self):
        self._test_set(Signatory, 'parties', self.make_signatory)

    def test_creation_time(self):
        self._test_remote_time_attr(attr_name='creation_time',
                                    serialized_name=u'ctime',
                                    null_ok=False)

    def test_modification_time(self):
        self._test_remote_time_attr(attr_name='modification_time',
                                    serialized_name=u'mtime',
                                    null_ok=False)

    def test_timeout_time(self):
        self._test_remote_time_attr(attr_name='timeout_time')

    def test_autoremind_time(self):
        self._test_remote_time_attr(attr_name='autoremind_time',
                                    serialized_name=u'auto_remind_time')

    def test_status(self):
        self._test_remote_enum(DocumentStatus,
                               attr_name='status',
                               default_value=DocumentStatus.preparation)
