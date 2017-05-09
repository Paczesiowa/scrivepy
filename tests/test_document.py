# coding: utf-8
from scrivepy import (
    Document,
    Signatory)
from tests.utils import IntegrationTestCase


class DocumentTest(IntegrationTestCase):

    O = Document
    default_ctor_kwargs = {}
    json = {u'id': u'123', u'title': u'Document', u'parties': []}

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
