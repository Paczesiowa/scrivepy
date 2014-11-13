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

        response = method(url, data=data, headers=headers, files=files)
        doc_data = response.json()
        return _document.Document._from_json_obj(doc_data)

    def create_document_from_file(self, file_path):
        files = {'file': (path.basename(file_path),
                          open(file_path, 'rb'),
                          'application/pdf')}

        return self._make_request(['createfromfile'], data='', files=files)

    def create_document_from_template(self, template_id):
        return self._make_request(['createfromtemplate', template_id])

    def get_document(self, document_id):
        return self._make_request(['get', document_id], method=requests.get)

    def update_document(self, document):
        return self._make_request(['update', document.id],
                                  data={'json': document._to_json()})

    def ready(self, document):
        return self._make_request(['ready', document.id])
