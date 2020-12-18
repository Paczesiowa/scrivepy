#!/usr/bin/env python
import argparse
import json
from os import path

import requests

from scrivepy import _file


class RemoteAuthorAttachment(object):

    def __init__(self, file, name, required, add_to_sealed_file):
        self.file = file
        self.name = name
        self.required = required
        self.add_to_sealed_file = add_to_sealed_file

    def _set_api(self, api, document):
        self.file._set_api(api, document)


class Document(object):

    def __init__(self, doc_json):
        self.json = doc_json
        self._api = None
        self.original_file = None
        self.author_attachments = []

    def _set_api(self, api, document):
        self._api = api
        if self.original_file is not None:
            self.original_file._set_api(api, document)
        for att in self.author_attachments:
            att._set_api(api, document)

    @property
    def id(self):
        return self.json['id']

    @classmethod
    def _from_json_obj(cls, doc_json):
        doc = Document(doc_json)
        doc.original_file = _file.RemoteFile._from_json_obj(doc_json.get(u'file'))
        author_attachments = []
        for att_json in doc_json['author_attachments']:
            att_json['id'] = att_json['file_id']
            att = RemoteAuthorAttachment(_file.RemoteFile._from_json_obj(att_json),
                                         name=att_json['name'],
                                         required=att_json['required'],
                                         add_to_sealed_file=att_json['add_to_sealed_file'])
            author_attachments.append(att)
        doc.author_attachments = author_attachments
        return doc


class Scrive(object):

    def __init__(self, client_credentials_identifier,
                 client_credentials_secret,
                 token_credentials_identifier,
                 token_credentials_secret,
                 api_hostname=b'scrive.com', https=True):
        self._api_hostname = api_hostname
        self._https = https
        proto = b'https' if https else b'http'
        self._api_url = proto + b'://' + api_hostname + b'/api/v2/'

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
                      data=None, files=None, params=None):

        url = self._api_url + b'/'.join(url_elems)

        if params is not None:
            url += '?' + urllib.urlencode(params)
        print url

        headers = dict(self._headers)
        if files is None:
            headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'

        return method(url, data=data, headers=headers, files=files)
        
    def _make_doc_request(self, url_elems, method=requests.post,
                          data=None, files=None):
        response = self._make_request(url_elems, method=method,
                                      data=data, files=files)
        if response.status_code < 200 or response.status_code >= 300:
            raise Exception(response.json())
        document = Document._from_json_obj(response.json())
        document._set_api(self, document)
        return document
        
    def get_document(self, document_id):
        return self._make_doc_request(['documents', document_id, 'get'],
                                       method=requests.get)

    def create_document_from_file(self, file_path):
        if file_path is None:
            files = None
        else:
            files = {'file': (path.basename(file_path),
                              open(file_path, 'rb'),
                              'application/pdf')}

        return self._make_doc_request(['documents', 'new'], data='', files=files)

    def change_document_file(self, document, file_path):
        if file_path is None:
            files = None
        else:
            ascii_file_name = ''.join(c if ord(c) < 128 else '_'
                                      for c in path.basename(file_path))
            files = {'file': (ascii_file_name,
                              open(file_path, 'rb'),
                              'application/pdf')}

        return self._make_doc_request(
            ['documents', document.id, 'setfile'], data='', files=files)

    def update_document(self, document):
        for attachment in document.author_attachments:
            file_data = {'file_param': 'file',
                         'add_to_sealed_file': attachment.add_to_sealed_file,
                         'required': attachment.required,
                         'name': attachment.name}
            data = {'attachments': json.dumps([file_data]), 'incremental': 'true'}
            files = {'file': (attachment.name, attachment.file.stream(), 'application/pdf')}
            new_doc = self._make_doc_request(['documents', document.id, 'setattachments'],
                                             data=data, files=files)
        
        return self._make_doc_request(
            ['documents', document.id, 'update'], data={'document': json.dumps(document.json)}, files=None)

def clone_placement(fp):
    result = FieldPlacement(left=fp.left, top=fp.top, width=fp.width,
                            height=fp.height, font_size=fp.font_size,
                            page=fp.page, tip=fp.tip)

    return result


def clone_field(f):
    sbfbs = f.should_be_filled_by_sender
    if isinstance(f, SignatureField):
        sbfbs = f.should_be_filled_by_sender
        result = SignatureField(name=f.name, obligatory=f.obligatory,
                                should_be_filled_by_sender=sbfbs)
        result._value = f.value
    else:
        result = type(f)(name=f.name,
                         value=f.value,
                         obligatory=f.obligatory,
                         should_be_filled_by_sender=sbfbs)

    for fp in f.placements:
        result.placements.add(clone_placement(fp))

    return result


def clone_signatory(sl):
    result = Signatory()

    result.sign_order = sl.sign_order
    result.invitation_delivery_method = sl.invitation_delivery_method
    result.confirmation_delivery_method = sl.confirmation_delivery_method
    result.authentication_method = sl.authentication_method
    result.viewer = sl.viewer
    result._author = sl.author
    result.sign_success_redirect_url = sl.sign_success_redirect_url
    result.rejection_redirect_url = sl.rejection_redirect_url

    for f in sl.fields:
        result.fields.add(clone_field(f))

    return result


def copy_doc(d1, d2):
    if d1.original_file is not None:
        file_path = '/tmp/' + d1.original_file.name
        d1.original_file.save_as(file_path)
        d2 = d2._api.change_document_file(d2, file_path)

    d2.json['title'] = d1.json['title']
    d2.json['is_template'] = d1.json['is_template']
    d2.json['timezone'] = d1.json['timezone']
    d2.json['lang'] = d1.json['lang']
    d2.json['days_to_sign'] = d1.json['days_to_sign']
    d2.json['display_options'] = d1.json['display_options']

    d2.author_attachments = d1.author_attachments

    d2.json['parties'] = d1.json['parties']

    d2 = d2._api.update_document(d2)
    return d2


if __name__ == '__main__':
    descr = 'Copy documents between servers/accounts'
    parser = argparse.ArgumentParser(description=descr)
    msg = 'Client credentials identifier for source account'
    parser.add_argument('--source-client-credentials-identifier',
                        metavar='ID', type=str, help=msg, required=True)
    msg = 'Client credentials secret for source account'
    parser.add_argument('--source-client-credentials-secret',
                        metavar='ID', type=str, help=msg, required=True)
    msg = 'Token credentials identifier for source account'
    parser.add_argument('--source-token-credentials-identifier',
                        metavar='ID', type=str, help=msg, required=True)
    msg = 'Token credentials secret for source account'
    parser.add_argument('--source-token-credentials-secret',
                        metavar='ID', type=str, help=msg, required=True)
    msg = 'Hostname of source account (e.g. api-testbed.scrive.com)'
    parser.add_argument('--source-hostname',
                        metavar='DOMAIN', type=str, help=msg, required=True)
    msg = 'Source hostname is not using HTTPS'
    parser.add_argument('--source-no-https', help=msg,
                        action='store_true', default=False)
    msg = 'Client credentials identifier for target account'
    parser.add_argument('--target-client-credentials-identifier',
                        metavar='ID', type=str, help=msg, required=True)
    msg = 'Client credentials secret for target account'
    parser.add_argument('--target-client-credentials-secret',
                        metavar='ID', type=str, help=msg, required=True)
    msg = 'Token credentials identifier for target account'
    parser.add_argument('--target-token-credentials-identifier',
                        metavar='ID', type=str, help=msg, required=True)
    msg = 'Token credentials secret for target account'
    parser.add_argument('--target-token-credentials-secret',
                        metavar='ID', type=str, help=msg, required=True)
    msg = 'Hostname of target account (e.g. api-testbed.scrive.com)'
    parser.add_argument('--target-hostname',
                        metavar='DOMAIN', type=str, help=msg, required=True)
    msg = 'Target hostname is not using HTTPS'
    parser.add_argument('--target-no-https', help=msg,
                        action='store_true', default=False)

    msg = 'Ids of the document to copy from source account to target account'
    parser.add_argument('DOCUMENT_ID', type=str, help=msg, nargs='+')

    args = parser.parse_args()

    source_api = Scrive(client_credentials_identifier=
                        args.source_client_credentials_identifier,
                        client_credentials_secret=
                        args.source_client_credentials_secret,
                        token_credentials_identifier=
                        args.source_token_credentials_identifier,
                        token_credentials_secret=
                        args.source_token_credentials_secret,
                        api_hostname=args.source_hostname,
                        https=not args.source_no_https)
    target_api = Scrive(client_credentials_identifier=
                        args.target_client_credentials_identifier,
                        client_credentials_secret=
                        args.target_client_credentials_secret,
                        token_credentials_identifier=
                        args.target_token_credentials_identifier,
                        token_credentials_secret=
                        args.target_token_credentials_secret,
                        api_hostname=args.target_hostname,
                        https=not args.target_no_https)

    for did in args.DOCUMENT_ID:
        source_doc = source_api.get_document(did)
        target_doc = target_api.create_document_from_file(file_path=None)
        target_doc = copy_doc(source_doc, target_doc)
        print source_doc.id, '->', target_doc.id
