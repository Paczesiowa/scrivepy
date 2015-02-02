from os import path

import requests

from scrivepy import _document


class Scrive(object):

    def __init__(self, client_credentials_identifier,
                 client_credentials_secret,
                 token_credentials_identifier,
                 token_credentials_secret,
                 api_hostname=b'scrive.com', https=True):
        proto = b'https' if https else b'http'
        self._api_url = proto + b'://' + api_hostname + b'/api/v1/'

        oauth_elems = \
            {b'oauth_signature_method': b'"PLAINTEXT"',
             b'oauth_consumer_key': b'"%s"' % client_credentials_identifier,
             b'oauth_token': b'"%s"' % token_credentials_identifier,
             b'oauth_signature': b'"%s&%s"' % (client_credentials_secret,
                                               token_credentials_secret)}
        oauth_string = b','.join([key + b'=' + val
                                  for key, val in oauth_elems.items()])

        self._headers = {b'authorization': oauth_string}

    def _make_request(self, url_elems, method=requests.post,
                      data=None, files=None):

        url = self._api_url + b'/'.join(url_elems)

        headers = dict(self._headers)
        if files is None:
            headers['Content-Type'] = 'application/x-www-form-urlencoded'

        return method(url, data=data, headers=headers, files=files)

    def _make_doc_request(self, url_elems, method=requests.post,
                          data=None, files=None):
        response = self._make_request(url_elems, method=method,
                                      data=data, files=files)
        document = _document.Document._from_json_obj(response.json())
        document._set_api(self)
        return document

    def create_document_from_file(self, file_path):
        files = {'file': (path.basename(file_path),
                          open(file_path, 'rb'),
                          'application/pdf')}

        return self._make_doc_request(['createfromfile'], data='', files=files)

    def create_document_from_template(self, template_id):
        return self._make_doc_request(['createfromtemplate', template_id])

    def get_document(self, document_id):
        return self._make_doc_request(['get', document_id],
                                      method=requests.get)

    def update_document(self, document):
        return self._make_doc_request(['update', document.id],
                                      data={'json': document._to_json()})

    def ready(self, document):
        return self._make_doc_request(['ready', document.id])

    def _sign(self, document, signatory):
        '''
        WARNING! DO NOT USE! for testing purposes only!
        '''
        url_elems = ['sign', document.id, signatory.id]
        return self._make_doc_request(url_elems=url_elems, data='fields=[]')

    def _cancel_document(self, document):
        '''
        WARNING! DO NOT USE! for testing purposes only!
        '''
        url_elems = ['cancel', document.id]
        return self._make_doc_request(url_elems=url_elems)

    def trash_document(self, document):
        if document.status is _document.DocumentStatus.pending:
            self._cancel_document(document)
        self._make_request(url_elems=['delete', document.id],
                           method=requests.delete)

    def delete_document(self, document):
        if document.deletion_status is not _document.DeletionStatus.in_trash:
            self.trash_document(document)
        self._make_request(url_elems=['reallydelete', document.id],
                           method=requests.delete)
